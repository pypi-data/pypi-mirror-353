# blockbridge/s3_compatible.py
import base64
import sys
import tempfile
from pathlib import Path

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from .base import BlockBridgeInterface
from .exceptions import (InitializationError, ObjectNotFound,
                          StorageException)
from .utils import calculate_md5_hash, retry_on_exception


class S3_Compatible_Storage(BlockBridgeInterface):
    """
    Generic client for any S3-compatible object storage service that requires
    an explicit endpoint URL.

    This client is strictly vendor-agnostic and is ideal for services like:
    - MinIO (self-hosted)
    - GCS S3 Interoperability Mode
    - Any other S3-standard service.
    
    Note: For providers like Cloudflare R2 and Wasabi, which have specific endpoint
    conventions, it is recommended to use their dedicated clients in the
    `blockbridge.providers` module for a more seamless experience.
    """

    def __init__(self, endpoint_url: str,
                 access_key_id: str,
                 secret_access_key: str,
                 region_name: str | None = "us-east-1"):
        """
        Initializes the S3-compatible client.

        Args:
            endpoint_url: The full S3-compatible endpoint URL for the service.
            access_key_id: The access key ID for the service.
            secret_access_key: The secret access key for the service.
            region_name: The region name. Defaults to 'us-east-1'.
        """
        if not all([endpoint_url, access_key_id, secret_access_key]):
            raise InitializationError("S3_Compatible_Storage requires endpoint_url, access_key_id, and secret_access_key.")

        try:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region_name,
                endpoint_url=endpoint_url,
                config=BotoConfig(signature_version='s3v4')
            )
            self.endpoint_url = endpoint_url.rstrip('/')
            self.region = region_name
        except Exception as e:
            raise InitializationError(f"Failed to initialize S3-compatible client for endpoint {endpoint_url}. Error: {e}")

    def _parse_uri(self, uri: str) -> tuple[str, str]:
        """Parses an s3:// URI into bucket and object key."""
        if not uri.startswith("s3://"):
            raise ValueError("Invalid S3-compatible URI. Must start with 's3://'.")
        parts = uri.replace("s3://", "").split("/", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""

    @retry_on_exception(exceptions=(ClientError,))
    def download(self, uri: str, validate_checksum: bool = False) -> tuple[Path, tempfile.TemporaryDirectory]:
        """Downloads a file from the S3-compatible service."""
        bucket_name, key = self._parse_uri(uri)
        if not key:
            raise ValueError("Invalid URI for download. Must specify an object key.")

        temp_dir = tempfile.TemporaryDirectory()
        local_path = Path(temp_dir.name) / Path(key).name

        try:
            cloud_metadata = self.client.head_object(Bucket=bucket_name, Key=key)
            cloud_etag = cloud_metadata.get('ETag', "").strip('"')

            self.client.download_file(bucket_name, key, str(local_path))

            if validate_checksum and cloud_etag and '-' not in cloud_etag:
                local_md5_hex = base64.b64decode(calculate_md5_hash(local_path)).hex()
                if cloud_etag.lower() != local_md5_hex.lower():
                    raise StorageException(f"Checksum mismatch for {uri}. Cloud ETag: {cloud_etag} vs Local MD5: {local_md5_hex}")
            elif validate_checksum:
                print(f"Warning: Checksum validation via ETag skipped for {uri}. ETag is not a simple MD5 hash.", file=sys.stderr)

        except ClientError as e:
            temp_dir.cleanup()
            if e.response['Error']['Code'] in ('404', 'NoSuchKey'):
                raise ObjectNotFound(f"Object not found at URI: {uri}")
            raise StorageException(f"Failed to download from {self.endpoint_url}. Error: {e}")
        return local_path, temp_dir

    @retry_on_exception(exceptions=(ClientError,))
    def upload(self, local_path: Path, dest_uri: str, make_public: bool = False, validate_checksum: bool = False) -> str:
        """Uploads a local file to the S3-compatible service."""
        if not local_path.is_file():
            raise FileNotFoundError(f"Local file not found at {local_path}")
        bucket_name, key = self._parse_uri(dest_uri)

        extra_args = {'ACL': 'public-read'} if make_public else {}
        if validate_checksum:
            extra_args['ContentMD5'] = calculate_md5_hash(local_path)

        self.client.upload_file(str(local_path), bucket_name, key, ExtraArgs=extra_args)
        return self.get_public_url(dest_uri)

    def get_public_url(self, uri: str) -> str:
        """Constructs a public URL based on the endpoint."""
        bucket_name, key = self._parse_uri(uri)
        return f"{self.endpoint_url}/{bucket_name}/{key}"

    # ... All other required interface methods are fully implemented here ...
    # (delete_prefix, list_objects, object_exists, is_public, etc.)
    # Their implementation is identical to the robust versions in the aws.py client.
    def delete_prefix(self, prefix_uri: str):
        bucket_name, prefix = self._parse_uri(prefix_uri)
        paginator = self.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' in page:
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                if objects_to_delete:
                    self.client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})

    def list_objects(self, prefix_uri: str) -> list[str]:
        bucket_name, prefix = self._parse_uri(prefix_uri)
        paginator = self.client.get_paginator('list_objects_v2')
        object_uris = []
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    object_uris.append(f"s3://{bucket_name}/{obj['Key']}")
        return object_uris

    def object_exists(self, uri: str) -> bool:
        try:
            bucket_name, key = self._parse_uri(uri)
            if not key: return False
            self.client.head_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise StorageException(f"Error checking object existence: {e}")
        return False
        
    def is_public(self, uri: str) -> bool:
        try:
            bucket_name, key = self._parse_uri(uri)
            acl = self.client.get_object_acl(Bucket=bucket_name, Key=key)
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                if grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    if grant.get('Permission') in ['READ', 'FULL_CONTROL']:
                        return True
            return False
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise ObjectNotFound(f"Object not found at URI for ACL check: {uri}")
            return False

    def get_bucket_location(self, uri: str) -> str:
        try:
            bucket_name, _ = self._parse_uri(uri)
            response = self.client.get_bucket_location(Bucket=bucket_name)
            return response.get('LocationConstraint') or 'us-east-1'
        except ClientError as e:
            raise StorageException(f"Could not get location for bucket '{bucket_name}'. Error: {e}")
            
    def get_bucket_info(self, uri: str) -> dict:
        raise OperationNotSupported("get_bucket_info is not supported by the generic S3-compatible client.")