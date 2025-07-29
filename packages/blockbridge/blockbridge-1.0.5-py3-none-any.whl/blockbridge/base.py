# blockbridge/base.py
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path


class BlockBridgeInterface(ABC):
    """
    Abstract Base Class defining the universal contract for all cloud storage clients.

    This interface ensures that every supported storage provider (GCS, S3, Azure, etc.)
    exposes a consistent, predictable set of methods for all common and advanced
    object storage operations. Applications should code against this interface to
    remain cloud-agnostic.
    """

    @abstractmethod
    def download(self, uri: str, validate_checksum: bool = False) -> tuple[Path, tempfile.TemporaryDirectory]:
        """
        Downloads an object from a cloud URI to a local temporary file.

        This method is responsible for handling network requests, error checking,
        and optional data integrity validation.

        Args:
            uri: The full cloud URI of the object (e.g., 'gs://bucket/key', 's3://bucket/key').
            validate_checksum: If True, performs an MD5 checksum validation after
                               download to ensure data integrity.

        Returns:
            A tuple containing:
                - A Path object to the local temporary file.
                - The TemporaryDirectory object managing the file's lifecycle.
                  The caller is responsible for calling `.cleanup()` on this object.

        Raises:
            ObjectNotFound: If the specified object does not exist at the source URI.
            StorageException: For other download-related errors (e.g., network issues, permissions).
        """
        pass

    @abstractmethod
    def upload(self, local_path: Path, dest_uri: str, make_public: bool = False, validate_checksum: bool = False) -> str:
        """
        Uploads a local file to a destination cloud URI.

        This method should handle large files gracefully through managed multipart uploads
        and provide options for setting public accessibility and data integrity checks.

        Args:
            local_path: The local Path object of the file to upload.
            dest_uri: The full cloud destination URI for the object.
            make_public: If True, makes the uploaded object publicly readable.
                         Note: Behavior may vary based on provider's permission model.
            validate_checksum: If True, calculates the MD5 hash of the local file
                               and provides it to the cloud provider for server-side validation.

        Returns:
            The public HTTPS URL of the uploaded object.

        Raises:
            FileNotFoundError: If the local_path does not exist.
            StorageException: For upload-related errors (e.g., network issues, permissions).
        """
        pass
    
    @abstractmethod
    def delete_object(self, uri: str) -> None:
        """
        Deletes a single object from the cloud.

        Args:
            uri: The full cloud URI of the object to delete.
        
        Raises:
            ObjectNotFound: If the object does not exist.
            StorageException: For other deletion-related errors.
        """
        pass

    @abstractmethod
    def delete_prefix(self, prefix_uri: str) -> None:
        """
        Deletes all objects under a given URI prefix (simulating folder deletion).

        This operation should be performed as efficiently as possible, using batch
        deletion APIs where available.

        Args:
            prefix_uri: The URI prefix (folder) to delete. Must end with '/'.
        """
        pass

    @abstractmethod
    def list_objects(self, prefix_uri: str, all_versions: bool = False) -> list[str]:
        """
        Lists all object URIs under a given prefix.

        This method should handle pagination automatically to return a complete
        list of all objects matching the prefix.

        Args:
            prefix_uri: The URI prefix (folder) to list, e.g., 'gs://bucket/folder/'.
            all_versions: If True, returns URIs for every version of each object
                          in a versioned bucket. The URI may include version-specific identifiers.

        Returns:
            A list of full object URIs (strings).
        """
        pass

    @abstractmethod
    def list_objects_with_metadata(self, prefix_uri: str, all_versions: bool = False) -> dict[str, list[dict]]:
        """
        Lists objects under a prefix, returning a map of their metadata. Essential for sync operations.

        Args:
            prefix_uri: The URI prefix (folder) to list.
            all_versions: If True, the list for each key will contain the metadata
                          for every historical version of that object.

        Returns:
            A dictionary mapping each object's relative key to a list of its versions' metadata.
            For non-versioned objects, the list will contain a single dictionary.
            e.g., {'path/to/file.txt': [{'version_id': 'v1', 'size': 1024, 'last_modified': datetime(...), 'etag': '...'}]}
        """
        pass

    @abstractmethod
    def native_copy(self, source_uri: str, dest_uri: str, source_version_id: str | None = None) -> None:
        """
        Performs a provider-native, server-side copy. This is significantly faster
        than downloading and re-uploading. Assumes source and dest are on the same provider.

        Args:
            source_uri: The full URI of the source object.
            dest_uri: The full URI of the destination object.
            source_version_id: The specific version of the source object to copy. If None,
                               the latest version is copied.
        
        Raises:
            OperationNotSupported: If the provider does not support server-side copy.
            StorageException: For any copy-related errors.
        """
        pass

    @abstractmethod
    def native_rename(self, old_uri: str, new_uri: str) -> None:
        """
        Performs a provider-native, server-side rename. This is typically implemented
        as a native copy followed by a delete of the source object.

        Args:
            old_uri: The current URI of the object.
            new_uri: The desired new URI of the object.
        """
        pass

    @abstractmethod
    def object_exists(self, uri: str) -> bool:
        """
        Checks if an object exists at the given URI efficiently.

        Args:
            uri: The full cloud URI of the object to check.

        Returns:
            True if the object exists, False otherwise.
        """
        pass

    @abstractmethod
    def is_public(self, uri: str) -> bool:
        """

        Checks if a given object is publicly accessible over the internet.

        This method performs a live check against the object's permissions or
        its container's public access policy.

        Args:
            uri: The full cloud URI of the object.

        Returns:
            True if the object is publicly readable, False otherwise.
        """
        pass

    @abstractmethod
    def get_bucket_location(self, uri: str) -> str:
        """
        Gets the physical region or location of a bucket.

        Args:
            uri: A URI pointing to the bucket (e.g., 'gs://my-bucket/').

        Returns:
            A string representing the bucket's location (e.g., 'us-east-1', 'US-CENTRAL1').
        """
        pass

    @abstractmethod
    def get_bucket_info(self, uri: str) -> dict:
        """
        Gets raw, provider-specific metadata about a bucket.

        The structure of the returned dictionary will vary between cloud providers.
        This is intended for advanced use cases where provider-specific details are needed.

        Args:
            uri: A URI pointing to the bucket (e.g., 's3://my-bucket/').

        Returns:
            A dictionary containing provider-specific metadata about the bucket.
        """
        pass