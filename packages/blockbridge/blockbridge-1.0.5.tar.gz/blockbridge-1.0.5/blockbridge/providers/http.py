import sys
import tempfile
from pathlib import Path
import requests

from ..base import BlockBridgeInterface
from ..exceptions import ObjectNotFound, OperationNotSupported, StorageException
from ..utils import retry_on_exception

class HTTPS_Storage(BlockBridgeInterface):
    """A read-only client for downloading files from public HTTPS URLs."""

    def __init__(self, **kwargs):
        """Initializes a new requests session."""
        self.session = requests.Session()

    @retry_on_exception(exceptions=(requests.exceptions.ConnectionError, requests.exceptions.Timeout))
    def download(self, uri: str, validate_checksum: bool = False) -> tuple[Path, tempfile.TemporaryDirectory]:
        """
        Downloads a file from a public URL to a temporary local path.

        Args:
            uri: The full HTTPS URL of the object to download.
            validate_checksum: This parameter is ignored as checksums are not available.

        Returns:
            A tuple containing the Path to the downloaded file and the TemporaryDirectory object
            that holds it, which must be cleaned up by the caller.
        """
        if validate_checksum:
            print("Warning: Checksum validation is not supported for HTTPS sources.", file=sys.stderr)

        temp_dir = tempfile.TemporaryDirectory()
        local_path = Path(temp_dir.name) / Path(uri).name

        try:
            with self.session.get(uri, stream=True) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.exceptions.HTTPError as e:
            temp_dir.cleanup()
            if e.response.status_code == 404:
                raise ObjectNotFound(f"Object not found at URL: {uri}")
            raise StorageException(f"Failed to download from {uri}. HTTP Status: {e.response.status_code}") from e
        except Exception as e:
            temp_dir.cleanup()
            raise StorageException(f"A critical error occurred while downloading from {uri}: {e}") from e

        return local_path, temp_dir

    def object_exists(self, uri: str) -> bool:
        """
        Checks if an object exists at the given URL using a HEAD request.

        Args:
            uri: The full HTTPS URL to check.

        Returns:
            True if the object exists (HTTP 200), False otherwise.
        """
        try:
            response = self.session.head(uri, allow_redirects=True)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            # Covers connection errors, timeouts, invalid URLs, etc.
            return False

    # --- Operations not supported by this read-only client ---

    def upload(self, local_path: Path, uri: str):
        """Operation not supported."""
        raise OperationNotSupported("Uploading files is not supported for generic HTTPS endpoints.")

    def delete(self, uri: str):
        """Operation not supported."""
        raise OperationNotSupported("Deleting files is not supported for generic HTTPS endpoints.")

    def list_objects(self, uri: str, recursive: bool = False):
        """Operation not supported."""
        raise OperationNotSupported("Listing objects is not supported for generic HTTPS endpoints.")

    def copy(self, source_uri: str, dest_uri: str):
        """Operation not supported."""
        raise OperationNotSupported("Copying files is not supported for generic HTTPS endpoints.")

    def move(self, source_uri: str, dest_uri: str):
        """Operation not supported."""
        raise OperationNotSupported("Moving files is not supported for generic HTTPS endpoints.")