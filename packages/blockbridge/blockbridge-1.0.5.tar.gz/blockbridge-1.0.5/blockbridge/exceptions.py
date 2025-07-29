# blockbridge/exceptions.py

"""
BlockBridge Custom Exceptions

This module contains all custom exceptions raised by the BlockBridge library.

Using custom exceptions allows applications to gracefully handle specific errors
originating from storage operations without needing to catch broad, generic
exceptions. All exceptions inherit from a common StorageException base class.
"""


class StorageException(Exception):
    """
    Base exception for all storage-related errors in the BlockBridge library.

    Catching this exception will catch any error originating from any client
    or operation within the library.
    """
    pass


class InitializationError(StorageException):
    """
    Raised when a storage client fails to initialize.

    This typically occurs due to missing or invalid credentials, an
    unreachable endpoint URL, or insufficient permissions to access the
    storage service.
    """
    pass


class ObjectNotFound(StorageException):
    """
    Raised when a requested object (file) or container (bucket) does not exist.

    This provides a provider-agnostic way to handle '404 Not Found' errors
    from any cloud storage provider.
    """
    pass


class OperationNotSupported(StorageException):
    """
    Raised when a storage backend does not support a specific operation.

    For example, attempting to call `upload` on a read-only HTTPS client
    or `native_rename` on a service without that capability.
    """
    pass


class DestinationNotEmptyError(StorageException):
    """
    Raised by a clone operation when the destination is required
    to be empty but is not.

    This is a critical safety measure to prevent accidental data overwrites.
    """
    pass


class VerificationError(StorageException):
    """
    Raised during a post-flight check if the destination's state does not
    verifiably match the source's state after a transfer. This can be due to
    a checksum mismatch or differing object counts.
    """
    pass


class SourceModifiedError(VerificationError):
    """
    A specific type of VerificationError raised if the source was modified
    during a long-running transfer operation, invalidating the integrity
    of the clone or sync.
    """
    pass