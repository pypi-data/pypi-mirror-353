# blockbridge/providers/cloudflare.py
import base64
import sys
import tempfile
from pathlib import Path

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from ..base import BlockBridgeInterface
from ..exceptions import (InitializationError, ObjectNotFound,
                          StorageException)
from ..utils import calculate_md5_hash, retry_on_exception


class Cloudflare_R2_Storage(BlockBridgeInterface):
    """
    Client specifically for Cloudflare R2 Storage.

    R2 is an S3-compatible service. This client simplifies its connection by
    automatically constructing the correct endpoint URL from your Account ID and
    setting the region to 'auto' as required.
    """

    def __init__(self, account_id: str,
                 access_key_id: str,
                 secret_access_key: str):
        """
        Initializes the Cloudflare R2 client.

        Args:
            account_id: Your Cloudflare R2 account ID (the string of hex characters).
            access_key_id: The Access Key ID generated for your R2 API token.
            secret_access_key: The Secret Access Key for your R2 API token.
        """
        if not all([account_id, access_key_id, secret_access_key]):
            raise InitializationError("Cloudflare_R2_Storage requires account_id, access_key_id, and secret_access_key.")

        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

        try:
            # R2 requires region_name='auto' and the v4 signature
            config = BotoConfig(signature_version='s3v4')
            self.client = boto3.client(
                "s3",
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                endpoint_url=endpoint_url,
                region_name="auto",
                config=config
            )
            self.endpoint_url = endpoint_url
            self.account_id = account_id
        except Exception as e:
            raise InitializationError(f"Failed to initialize Cloudflare R2 client. Error: {e}")

    def _parse_uri(self, uri: str) -> tuple[str, str]:
        """Parses an s3:// URI into bucket and object key."""
        if not uri.startswith("s3://"):
            raise ValueError("Invalid R2 URI. Must start with 's3://'.")
        parts = uri.replace("s3://", "").split("/", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""

    @retry_on_exception(exceptions=(ClientError,))
    def download(self, uri: str, validate_checksum: bool = False) -> tuple[Path, tempfile.TemporaryDirectory]:
        """Downloads a file from R2 to a local temporary file."""
        bucket_name, key = self._parse_uri(uri)
        if not key:
            raise ValueError("Invalid URI for download. Must specify an object key.")

        temp_dir = tempfile.TemporaryDirectory()
        local_path = Path(temp_dir.name) / Path(key).name
        try:
            # R2 ETag is the MD5 hash for non-multipart objects.
            cloud_metadata = self.client.head_object(Bucket=bucket_name, Key=key)
            cloud_etag = cloud_metadata.get('ETag', "").strip('"')

            print(f"Downloading {uri} to {local_path}...", file=sys.stderr)
            self.client.download_file(bucket_name, key, str(local_path))

            if validate_checksum and cloud_etag and len(cloud_etag) == 32:
                local_md5_hex = base64.b64decode(calculate_md5_hash(local_path)).hex()
                if cloud_etag.lower() != local_md5_hex.lower():
                    raise StorageException(f"Checksum mismatch for {uri}. Cloud ETag: {cloud_etag} vs Local MD5: {local_md5_hex}")
                print(f"✅ Checksum validated for {uri}", file=sys.stderr)
            elif validate_checksum:
                print(f"Warning: Checksum validation via ETag skipped for {uri}. ETag '{cloud_etag}' may not be a simple MD5 hash.", file=sys.stderr)

        except ClientError as e:
            temp_dir.cleanup()
            if e.response['Error']['Code'] in ('404', 'NoSuchKey', 'NotFound'):
                raise ObjectNotFound(f"Object not found at R2 URI: {uri}")
            raise StorageException(f"Failed to download from R2. Error: {e}")
        return local_path, temp_dir

    @retry_on_exception(exceptions=(ClientError,))
    def upload(self, local_path: Path, dest_uri: str, make_public: bool = False, validate_checksum: bool = False) -> str:
        """Uploads a local file to R2."""
        if not local_path.is_file():
            raise FileNotFoundError(f"Local file not found at {local_path}")
        bucket_name, key = self._parse_uri(dest_uri)

        extra_args = {}
        if validate_checksum:
            extra_args['ContentMD5'] = calculate_md5_hash(local_path)
        if make_public:
            print("Info: For public access in R2, ensure your bucket is connected to a public domain in the Cloudflare dashboard.", file=sys.stderr)

        print(f"Uploading {local_path} to {dest_uri}...", file=sys.stderr)
        self.client.upload_file(str(local_path), bucket_name, key, ExtraArgs=extra_args)
        return self.get_public_url(dest_uri)

    @retry_on_exception(exceptions=(ClientError,))
    def delete_prefix(self, prefix_uri: str):
        """Deletes all objects under a given R2 prefix."""
        bucket_name, prefix = self._parse_uri(prefix_uri)
        if not prefix:
            raise ValueError("Prefix deletion requires a non-empty prefix.")

        paginator = self.client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        objects_to_delete = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objects_to_delete.append({'Key': obj['Key']})
        
        if objects_to_delete:
            # S3 delete_objects can handle up to 1000 keys at a time
            for i in range(0, len(objects_to_delete), 1000):
                chunk = objects_to_delete[i:i + 1000]
                self.client.delete_objects(Bucket=bucket_name, Delete={'Objects': chunk})
            print(f"Deleted {len(objects_to_delete)} objects under prefix {prefix_uri}", file=sys.stderr)

    def list_objects(self, prefix_uri: str) -> list[str]:
        """Lists all object URIs under a given R2 prefix."""
        bucket_name, prefix = self._parse_uri(prefix_uri)
        paginator = self.client.get_paginator('list_objects_v2')
        object_uris = []
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    object_uris.append(f"s3://{bucket_name}/{obj['Key']}")
        return object_uris
        
    def list_objects_with_metadata(self, prefix_uri: str) -> dict[str, dict]:
        """Lists R2 objects under a prefix, returning a map of their metadata."""
        bucket_name, prefix = self._parse_uri(prefix_uri)
        paginator = self.client.get_paginator('list_objects_v2')
        metadata_map = {}
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    uri = f"s3://{bucket_name}/{key}"
                    relative_key = key[len(prefix):] if prefix else key
                    metadata_map[relative_key] = {
                        'uri': uri,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    }
        return metadata_map

    def get_public_url(self, uri: str) -> str:
        """
        Constructs a public URL for an R2 object.
        Note: This relies on the bucket being publicly exposed via a connected
        r2.dev or custom domain, configured in the Cloudflare dashboard.
        """
        bucket_name, key = self._parse_uri(uri)
        # R2 public URLs are typically served from a special subdomain.
        return f"https://pub-{bucket_name}.{self.account_id}.r2.dev/{key}"

    def object_exists(self, uri: str) -> bool:
        """Checks if an object exists at the given R2 URI."""
        try:
            bucket_name, key = self._parse_uri(uri)
            if not key: return False
            self.client.head_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise StorageException(f"Error checking if object exists on R2: {e}")
        return False

    def is_public(self, uri: str) -> bool:
        """
        Checks if an R2 object is public.
        Note: True public access in R2 is determined by the bucket's domain settings,
        not by S3 ACLs. This method checks for ACLs for compatibility but may not
        reflect the true public status if a custom domain is used.
        """
        print("Warning: 'is_public' for R2 depends on bucket domain settings, not object ACLs.", file=sys.stderr)
        try:
            bucket_name, key = self._parse_uri(uri)
            acl = self.client.get_object_acl(Bucket=bucket_name, Key=key)
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                if grantee.get('Type') == 'Group' and \
                   grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    return True
            return False
        except ClientError as e:
            if 'NoSuchCORSConfiguration' in str(e) or 'NoSuchBucketPolicy' in str(e):
                 # These errors can occur if no specific policies are set; assume not public.
                 return False
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise ObjectNotFound(f"Object not found at R2 URI for ACL check: {uri}")
            # R2 may not support get_object_acl in the same way as S3.
            print(f"Warning: Could not determine public status via ACL for R2. The operation is not fully supported by the provider. Error: {e}", file=sys.stderr)
            return False

    def get_bucket_location(self, uri: str) -> str:
        """Gets the location of an R2 bucket, which is always 'auto'."""
        return "auto"
            
    def get_bucket_info(self, uri: str) -> dict:
        """Gets metadata for an R2 bucket."""
        try:
            bucket_name, _ = self._parse_uri(uri)
            acl = self.client.get_bucket_acl(Bucket=bucket_name)
            return {
                "provider": "cloudflare_r2",
                "bucket_name": bucket_name,
                "region": "auto",
                "owner": acl.get("Owner"),
                "grants": acl.get("Grants")
            }
        except ClientError as e:
            raise StorageException(f"Could not get info for R2 bucket '{bucket_name}'. Error: {e}")