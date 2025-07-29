# blockbridge/providers/wasabi.py
import base64
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from ..base import BlockBridgeInterface
from ..exceptions import (InitializationError, ObjectNotFound,
                          StorageException)
from ..utils import calculate_md5_hash, retry_on_exception


class Wasabi_Storage(BlockBridgeInterface):
    """
    Client specifically for Wasabi Hot Cloud Storage.

    Wasabi is an S3-compatible service that requires specifying the correct
    regional endpoint URL. This client handles that construction automatically.
    """

    def __init__(self, region_name: str,
                 access_key_id: str,
                 secret_access_key: str):
        """
        Initializes the Wasabi client.

        Args:
            region_name: The specific Wasabi region, e.g., 'us-east-1', 'eu-central-1'.
                         This is used to construct the endpoint URL.
            access_key_id: Your Wasabi Access Key ID.
            secret_access_key: Your Wasabi Secret Access Key.
        """
        if not all([region_name, access_key_id, secret_access_key]):
            raise InitializationError("Wasabi_Storage requires region_name, access_key_id, and secret_access_key.")

        # Construct the Wasabi-specific endpoint URL
        endpoint_url = f"https://s3.{region_name}.wasabisys.com"

        try:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                endpoint_url=endpoint_url,
                region_name=region_name,
                config=BotoConfig(signature_version='s3v4')
            )
            self.endpoint_url = endpoint_url
            self.region = region_name
        except Exception as e:
            raise InitializationError(f"Failed to initialize Wasabi client. Error: {e}")

    def _parse_uri(self, uri: str) -> tuple[str, str]:
        """Parses an s3:// URI into bucket and object key."""
        if not uri.startswith("s3://"):
            raise ValueError("Invalid Wasabi URI. Must start with 's3://'.")
        parts = uri.replace("s3://", "").split("/", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""

    @retry_on_exception(exceptions=(ClientError,))
    def download(self, uri: str, validate_checksum: bool = False) -> tuple[Path, tempfile.TemporaryDirectory]:
        """Downloads a file from Wasabi to a local temporary file."""
        bucket_name, key = self._parse_uri(uri)
        if not key:
            raise ValueError("Invalid URI for download. Must specify an object key.")

        temp_dir = tempfile.TemporaryDirectory()
        local_path = Path(temp_dir.name) / Path(key).name
        try:
            cloud_metadata = self.client.head_object(Bucket=bucket_name, Key=key)
            cloud_etag = cloud_metadata.get('ETag', "").strip('"')

            print(f"Downloading {uri} to {local_path}...", file=sys.stderr)
            self.client.download_file(bucket_name, key, str(local_path))

            if validate_checksum and cloud_etag and '-' not in cloud_etag:
                local_md5_hex = base64.b64decode(calculate_md5_hash(local_path)).hex()
                if cloud_etag.lower() != local_md5_hex.lower():
                    raise StorageException(f"Checksum mismatch for {uri}. Cloud ETag: {cloud_etag} vs Local MD5: {local_md5_hex}")
                print(f"✅ Checksum validated for {uri}", file=sys.stderr)
            elif validate_checksum:
                print(f"Warning: Checksum validation via ETag skipped for {uri}; ETag is not an MD5 hash (likely a multipart upload).", file=sys.stderr)

        except ClientError as e:
            temp_dir.cleanup()
            if e.response['Error']['Code'] in ('404', 'NoSuchKey'):
                raise ObjectNotFound(f"Object not found at Wasabi URI: {uri}")
            raise StorageException(f"Failed to download from Wasabi. Error: {e}")
        return local_path, temp_dir

    @retry_on_exception(exceptions=(ClientError,))
    def upload(self, local_path: Path, dest_uri: str, make_public: bool = False, validate_checksum: bool = False) -> str:
        """Uploads a local file to Wasabi."""
        if not local_path.is_file():
            raise FileNotFoundError(f"Local file not found at {local_path}")
        bucket_name, key = self._parse_uri(dest_uri)

        extra_args = {'ACL': 'public-read'} if make_public else {}
        if validate_checksum:
            extra_args['ContentMD5'] = calculate_md5_hash(local_path)

        print(f"Uploading {local_path} to {dest_uri}...", file=sys.stderr)
        self.client.upload_file(str(local_path), bucket_name, key, ExtraArgs=extra_args)
        return self.get_public_url(dest_uri)

    @retry_on_exception(exceptions=(ClientError,))
    def delete_prefix(self, prefix_uri: str):
        """Deletes all objects under a given Wasabi prefix."""
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
            for i in range(0, len(objects_to_delete), 1000):
                chunk = objects_to_delete[i:i + 1000]
                self.client.delete_objects(Bucket=bucket_name, Delete={'Objects': chunk})
            print(f"Deleted {len(objects_to_delete)} objects under prefix {prefix_uri}", file=sys.stderr)

    def list_objects(self, prefix_uri: str) -> list[str]:
        """Lists all object URIs under a given Wasabi prefix."""
        bucket_name, prefix = self._parse_uri(prefix_uri)
        paginator = self.client.get_paginator('list_objects_v2')
        object_uris = []
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    object_uris.append(f"s3://{bucket_name}/{obj['Key']}")
        return object_uris

    def list_objects_with_metadata(self, prefix_uri: str) -> dict[str, dict]:
        """Lists Wasabi objects under a prefix, returning a map of their metadata."""
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
        """Constructs the public URL for a Wasabi object."""
        bucket_name, key = self._parse_uri(uri)
        # Wasabi supports both virtual-hosted and path-style, but path-style is simple and reliable.
        return f"{self.endpoint_url}/{bucket_name}/{key}"

    def object_exists(self, uri: str) -> bool:
        """Checks if an object exists at the given Wasabi URI."""
        try:
            bucket_name, key = self._parse_uri(uri)
            if not key: return False
            self.client.head_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise StorageException(f"Error checking if object exists on Wasabi: {e}")
        return False

    def is_public(self, uri: str) -> bool:
        """Checks if a Wasabi object is publicly readable via its ACL."""
        try:
            bucket_name, key = self._parse_uri(uri)
            acl = self.client.get_object_acl(Bucket=bucket_name, Key=key)
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                permission = grant.get('Permission')
                if grantee.get('Type') == 'Group' and \
                   grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers' and \
                   permission in ['READ', 'FULL_CONTROL']:
                    return True
            return False
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise ObjectNotFound(f"Object not found for ACL check: {uri}")
            print(f"Warning: Could not determine public status for {uri} due to Wasabi error: {e.response['Error']['Code']}", file=sys.stderr)
            return False

    def get_bucket_location(self, uri: str) -> str:
        """Gets the region of a Wasabi bucket."""
        # For Wasabi, the region is part of the endpoint and provided at initialization.
        return self.region
            
    def get_bucket_info(self, uri: str) -> dict:
        """Gets metadata for a Wasabi bucket."""
        try:
            bucket_name, _ = self._parse_uri(uri)
            acl = self.client.get_bucket_acl(Bucket=bucket_name)
            return {
                "provider": "wasabi",
                "bucket_name": bucket_name,
                "region": self.region,
                "endpoint": self.endpoint_url,
                "owner": acl.get("Owner"),
                "grants": acl.get("Grants")
            }
        except ClientError as e:
            raise StorageException(f"Could not get info for Wasabi bucket '{bucket_name}'. Error: {e}")