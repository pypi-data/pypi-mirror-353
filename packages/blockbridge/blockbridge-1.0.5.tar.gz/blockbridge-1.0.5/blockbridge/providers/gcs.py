# blockbridge/providers/gcs.py
import base64
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from google.api_core.exceptions import Forbidden, NotFound
from google.cloud import storage

from ..base import BlockBridgeInterface
from ..exceptions import (InitializationError, ObjectNotFound,
                          StorageException)
from ..utils import calculate_md5_hash, retry_on_exception


class GCSStorage(BlockBridgeInterface):
    """
    Google Cloud Storage implementation of the storage interface.

    This client uses native GCS authentication (Application Default Credentials).
    It assumes you have authenticated via the gcloud CLI (`gcloud auth application-default login`),
    are using a service account file (via GOOGLE_APPLICATION_CREDENTIALS env var),
    or are running on a GCP compute resource with an appropriate IAM role.
    """

    def __init__(self, project: str | None = None):
        """
        Initializes the GCS client.

        Args:
            project: An optional GCP project ID to associate with the client.
                     If None, the project is inferred from the environment.
        """
        try:
            self.client = storage.Client(project=project)
        except Exception as e:
            raise InitializationError(
                "Failed to initialize GCS client. Ensure you are authenticated "
                "(e.g., run 'gcloud auth application-default login'). Error: "
                f"{e}"
            )

    def _parse_uri(self, uri: str) -> tuple[str, str]:
        """Parses a gs:// URI into bucket and object key."""
        if not uri.startswith("gs://"):
            raise ValueError("Invalid GCS URI. Must start with 'gs://'.")
        parts = uri.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        blob_name = parts[1] if len(parts) > 1 else ""
        return bucket_name, blob_name

    @retry_on_exception(exceptions=(ConnectionError, Forbidden))
    def download(self, uri: str, validate_checksum: bool = False) -> tuple[Path, tempfile.TemporaryDirectory]:
        """Downloads a file from GCS to a local temporary file with optional checksum validation."""
        bucket_name, blob_name = self._parse_uri(uri)
        if not blob_name:
            raise ValueError("Invalid GCS URI for download. URI must specify an object.")

        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        temp_dir = tempfile.TemporaryDirectory()
        # Sanitize filename to prevent directory traversal issues
        safe_filename = "".join(c for c in Path(blob_name).name if c.isalnum() or c in '._-')
        local_path = Path(temp_dir.name) / safe_filename

        try:
            # Fetch metadata first to get checksum if needed
            blob.reload()
            cloud_md5_hash = blob.md5_hash  # This is already base64 encoded by the SDK

            print(f"Downloading {uri} to {local_path}...", file=sys.stderr)
            blob.download_to_filename(str(local_path))

            if validate_checksum:
                if not cloud_md5_hash:
                    print(f"Warning: Checksum validation skipped for {uri}; no MD5 hash available on cloud object.", file=sys.stderr)
                else:
                    local_md5_hash = calculate_md5_hash(local_path)
                    if cloud_md5_hash != local_md5_hash:
                        raise StorageException(f"Checksum mismatch for {uri}. Cloud: {cloud_md5_hash} vs Local: {local_md5_hash}")
                    print(f"✅ Checksum validated for {uri}", file=sys.stderr)

        except NotFound:
            temp_dir.cleanup()
            raise ObjectNotFound(f"Object not found at GCS URI: {uri}")
        except Exception as e:
            temp_dir.cleanup()
            raise StorageException(f"Failed to download from GCS. Error: {e}")

        return local_path, temp_dir

    @retry_on_exception(exceptions=(ConnectionError, Forbidden))
    def upload(self, local_path: Path, dest_uri: str, make_public: bool = False, validate_checksum: bool = False) -> str:
        """Uploads a local file to GCS with optional checksum validation."""
        if not local_path.is_file():
            raise FileNotFoundError(f"Local file not found at {local_path}")

        bucket_name, blob_name = self._parse_uri(dest_uri)
        if not blob_name:
            raise ValueError("Invalid GCS URI for upload. URI must specify an object destination.")

        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # GCS SDK handles large files with resumable/multipart uploads automatically.
        if validate_checksum:
            # The SDK expects the raw bytes for the hash, not base64.
            md5_digest = base64.b64decode(calculate_md5_hash(local_path))
            blob.md5_hash = md5_digest
        
        print(f"Uploading {local_path} to {dest_uri}...", file=sys.stderr)
        blob.upload_from_filename(str(local_path))

        if make_public:
            blob.make_public()
            
        return self.get_public_url(dest_uri)

    @retry_on_exception(exceptions=(Forbidden,))
    def delete_prefix(self, prefix_uri: str):
        """Deletes all objects under a given GCS prefix efficiently."""
        bucket_name, prefix = self._parse_uri(prefix_uri)
        if not prefix:
            raise ValueError("Prefix deletion requires a non-empty prefix.")
            
        bucket = self.client.bucket(bucket_name)
        blobs_to_delete = list(bucket.list_blobs(prefix=prefix))
        
        if not blobs_to_delete:
            return

        print(f"Deleting {len(blobs_to_delete)} objects under prefix {prefix_uri}...", file=sys.stderr)
        # GCS client library recommends batching for very large numbers of deletes.
        with self.client.batch():
            for blob in blobs_to_delete:
                blob.delete()

    def list_objects(self, prefix_uri: str) -> list[str]:
        """Lists all object URIs under a given GCS prefix."""
        bucket_name, prefix = self._parse_uri(prefix_uri)
        bucket = self.client.bucket(bucket_name)
        object_uris = []
        for blob in bucket.list_blobs(prefix=prefix):
            object_uris.append(f"gs://{bucket_name}/{blob.name}")
        return object_uris
        
    def list_objects_with_metadata(self, prefix_uri: str) -> dict[str, dict]:
        """Lists GCS objects under a prefix, returning a map of their metadata."""
        bucket_name, prefix = self._parse_uri(prefix_uri)
        bucket = self.client.bucket(bucket_name)
        metadata_map = {}
        for blob in bucket.list_blobs(prefix=prefix):
            uri = f"gs://{bucket_name}/{blob.name}"
            # GCS's equivalent of last_modified is 'updated'
            relative_key = blob.name[len(prefix):] if prefix else blob.name
            metadata_map[relative_key] = {
                'uri': uri,
                'size': blob.size,
                'last_modified': blob.updated
            }
        return metadata_map

    def get_public_url(self, uri: str) -> str:
        """Constructs the standard public HTTPS URL for a GCS object."""
        bucket_name, blob_name = self._parse_uri(uri)
        return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"

    def object_exists(self, uri: str) -> bool:
        """Checks if an object exists at the given URI."""
        try:
            bucket_name, blob_name = self._parse_uri(uri)
            if not blob_name: return False # A URI to a bucket is not an object
            
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            return blob.exists()
        except Exception:
            return False

    def is_public(self, uri: str) -> bool:
        """Checks if a GCS object is publicly accessible via its IAM policy."""
        try:
            bucket_name, blob_name = self._parse_uri(uri)
            if not blob_name: return False

            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            if not blob.exists():
                return False

            policy = blob.get_iam_policy(requested_policy_version=3)
            public_principals = {'allUsers', 'allAuthenticatedUsers'}

            for binding in policy.bindings:
                if 'roles/storage.objectViewer' in binding['role']:
                    if public_principals.intersection(binding['members']):
                        return True
            return False
        except (NotFound, Forbidden):
            return False
        except Exception as e:
            print(f"Could not determine public status for {uri}. Error: {e}", file=sys.stderr)
            return False

    def get_bucket_location(self, uri: str) -> str:
        """Gets the configured location of a GCS bucket."""
        try:
            bucket_name, _ = self._parse_uri(uri)
            bucket = self.client.get_bucket(bucket_name)
            return bucket.location.lower()
        except Exception as e:
            raise StorageException(f"Could not retrieve location for GCS bucket '{bucket_name}'. Error: {e}")
            
    def get_bucket_info(self, uri: str) -> dict:
        """Gets raw, provider-specific metadata for a GCS bucket."""
        bucket_name, _ = self._parse_uri(uri)
        try:
            bucket = self.client.get_bucket(bucket_name)
            # Convert the bucket object to a dictionary of its simple properties
            info = {prop: getattr(bucket, prop) for prop in dir(bucket) 
                    if not prop.startswith('_') 
                    and not callable(getattr(bucket, prop))
                    and isinstance(getattr(bucket, prop), (str, int, float, bool, type(None), datetime))}
            info['provider'] = 'gcs'
            return info
        except NotFound:
            raise ObjectNotFound(f"Bucket '{bucket_name}' not found.")
        except Exception as e:
            raise StorageException(f"Could not get info for GCS bucket '{bucket_name}'. Error: {e}")