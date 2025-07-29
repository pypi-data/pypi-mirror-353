# blockbridge/providers/azure.py
import base64
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings, PublicAccess

from ..base import BlockBridgeInterface
from ..exceptions import (InitializationError, ObjectNotFound,
                          OperationNotSupported, StorageException)
from ..utils import calculate_md5_hash, retry_on_exception


class AzureBlobStorage(BlockBridgeInterface):
    """
    Client for Microsoft Azure Blob Storage.

    This client supports authentication via a connection string (recommended for simplicity
    in many environments) or via DefaultAzureCredential, which is ideal for production
    workloads using Managed Identity, an `az login` session, or service principals.
    """

    def __init__(self, connection_string: str | None = None, account_url: str | None = None):
        """
        Initializes the Azure Blob Storage client.

        Priority is given to the connection_string. If it's not provided,
        account_url must be provided, and authentication will be attempted using
        DefaultAzureCredential (e.g., Managed Identity, `az login`).

        Args:
            connection_string: The full connection string for the storage account.
            account_url: The blob service endpoint URL, e.g., "https://<account>.blob.core.windows.net".
                         Required if not using a connection string.
        """
        try:
            if connection_string:
                self.client = BlobServiceClient.from_connection_string(connection_string)
            elif account_url:
                self.client = BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
            else:
                raise InitializationError("Azure client requires either a 'connection_string' or an 'account_url'.")
            self.account_url = self.client.url
        except Exception as e:
            raise InitializationError(f"Failed to initialize Azure Blob client. Check credentials/config. Error: {e}")

    def _parse_uri(self, uri: str) -> tuple[str, str, str]:
        """Parses an Azure Blob HTTPS URI to get account, container, and blob names."""
        parsed_url = urlparse(uri)
        account_name = parsed_url.netloc.split(".")[0]
        # e.g., /container/path/to/blob.txt -> ('container', 'path/to/blob.txt')
        path_parts = parsed_url.path.strip('/').split('/', 1)
        if len(path_parts) == 0 or not path_parts[0]:
            raise ValueError(f"Invalid Azure Blob URI format. URI must specify a container: {uri}")
        
        container_name = path_parts[0]
        blob_name = path_parts[1] if len(path_parts) > 1 else ""
        return account_name, container_name, blob_name

    @retry_on_exception(exceptions=(HttpResponseError,))
    def download(self, uri: str, validate_checksum: bool = False) -> tuple[Path, tempfile.TemporaryDirectory]:
        """Downloads a file from Azure Blob Storage to a local temporary file."""
        _, container_name, blob_name = self._parse_uri(uri)
        if not blob_name:
            raise ValueError("Invalid URI for download. Must specify an object.")

        blob_client = self.client.get_blob_client(container=container_name, blob=blob_name)

        temp_dir = tempfile.TemporaryDirectory()
        local_path = Path(temp_dir.name) / Path(blob_name).name

        try:
            properties = blob_client.get_blob_properties()
            cloud_md5_hash = base64.b64encode(properties.content_settings.content_md5).decode('utf-8') if properties.content_settings.content_md5 else None

            print(f"Downloading {uri} to {local_path}...", file=sys.stderr)
            with open(local_path, "wb") as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())

            if validate_checksum and cloud_md5_hash:
                local_md5_hash = calculate_md5_hash(local_path)
                if cloud_md5_hash != local_md5_hash:
                    raise StorageException(f"Checksum mismatch for {uri}. Cloud: {cloud_md5_hash} vs Local: {local_md5_hash}")
                print(f"✅ Checksum validated for {uri}", file=sys.stderr)
            elif validate_checksum:
                 print(f"Warning: Checksum validation skipped for {uri}; no MD5 hash available on cloud object.", file=sys.stderr)

        except ResourceNotFoundError:
            temp_dir.cleanup()
            raise ObjectNotFound(f"Object not found at Azure URI: {uri}")
        except Exception as e:
            temp_dir.cleanup()
            raise StorageException(f"Failed to download from Azure. Error: {e}")

        return local_path, temp_dir

    @retry_on_exception(exceptions=(HttpResponseError,))
    def upload(self, local_path: Path, dest_uri: str, make_public: bool = False, validate_checksum: bool = False) -> str:
        """Uploads a local file to Azure Blob Storage."""
        if not local_path.is_file():
            raise FileNotFoundError(f"Local file not found at {local_path}")

        _, container_name, blob_name = self._parse_uri(dest_uri)
        if not blob_name:
            raise ValueError("Invalid URI for upload. Must specify an object destination.")

        blob_client = self.client.get_blob_client(container=container_name, blob=blob_name)

        content_settings = None
        if validate_checksum:
            # Azure SDK expects the raw bytes of the hash.
            md5_digest = base64.b64decode(calculate_md5_hash(local_path))
            content_settings = ContentSettings(content_md5=md5_digest)
        
        if make_public:
            print("Info: For public access in Azure, ensure the container's public access level is set to 'Blob' or 'Container'.", file=sys.stderr)

        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
        
        return self.get_public_url(dest_uri)

    @retry_on_exception(exceptions=(HttpResponseError,))
    def delete_prefix(self, prefix_uri: str):
        """Deletes all blobs under a given URI prefix."""
        _, container_name, prefix = self._parse_uri(prefix_uri)
        if not prefix:
            raise ValueError("Prefix deletion requires a non-empty prefix.")
            
        container_client = self.client.get_container_client(container_name)
        blobs_to_delete = [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]
        
        if blobs_to_delete:
            print(f"Deleting {len(blobs_to_delete)} objects under prefix {prefix_uri}...", file=sys.stderr)
            container_client.delete_blobs(*blobs_to_delete)

    def list_objects(self, prefix_uri: str) -> list[str]:
        """Lists all object URIs under a given prefix."""
        _, container_name, prefix = self._parse_uri(prefix_uri)
        container_client = self.client.get_container_client(container_name)
        blob_uris = []
        for blob in container_client.list_blobs(name_starts_with=prefix):
            blob_uris.append(f"{self.account_url.rstrip('/')}/{container_name}/{blob.name}")
        return blob_uris

    def list_objects_with_metadata(self, prefix_uri: str) -> dict[str, dict]:
        """Lists objects under a prefix, returning a map of their metadata."""
        _, container_name, prefix = self._parse_uri(prefix_uri)
        container_client = self.client.get_container_client(container_name)
        metadata_map = {}
        for blob in container_client.list_blobs(name_starts_with=prefix):
            uri = f"{self.account_url.rstrip('/')}/{container_name}/{blob.name}"
            relative_key = blob.name[len(prefix):] if prefix else blob.name
            metadata_map[relative_key] = {
                'uri': uri,
                'size': blob.size,
                'last_modified': blob.last_modified
            }
        return metadata_map

    def get_public_url(self, uri: str) -> str:
        """Returns the native HTTPS URL for the blob."""
        return uri

    def object_exists(self, uri: str) -> bool:
        """Checks if a blob exists at the given URI."""
        try:
            _, container_name, blob_name = self._parse_uri(uri)
            if not blob_name: return False
            blob_client = self.client.get_blob_client(container=container_name, blob=blob_name)
            return blob_client.exists()
        except Exception:
            return False

    def is_public(self, uri: str) -> bool:
        """Checks if the blob's container allows public access."""
        try:
            _, container_name, blob_name = self._parse_uri(uri)
            if not self.object_exists(uri):
                return False

            container_client = self.client.get_container_client(container_name)
            properties = container_client.get_container_properties()
            public_access = properties.public_access
            return public_access in [PublicAccess.Blob, PublicAccess.Container]
        except (ResourceNotFoundError, HttpResponseError):
            return False
        except Exception as e:
            print(f"Could not determine public status for {uri}. Error: {e}", file=sys.stderr)
            return False

    def get_bucket_location(self, uri: str) -> str:
        """Gets the primary location of the storage account."""
        try:
            account_info = self.client.get_account_information()
            if account_info and 'geo_replication' in account_info and account_info['geo_replication']:
                return account_info['geo_replication'].get('primary_region', 'unknown')
            return 'unknown'
        except Exception as e:
            raise StorageException(f"Could not determine location for Azure account. Error: {e}")
            
    def get_bucket_info(self, uri: str) -> dict:
        """Gets raw metadata for an Azure Storage Container."""
        _, container_name, _ = self._parse_uri(uri)
        try:
            container_client = self.client.get_container_client(container_name)
            props = container_client.get_container_properties()
            return {
                "provider": "azure_blob",
                "account_url": self.account_url,
                "container_name": props.name,
                "last_modified_utc": props.last_modified,
                "lease_status": props.lease.status,
                "public_access": props.public_access
            }
        except ResourceNotFoundError:
            raise ObjectNotFound(f"Container '{container_name}' not found.")
        except Exception as e:
            raise StorageException(f"Could not get info for container '{container_name}'. Error: {e}")