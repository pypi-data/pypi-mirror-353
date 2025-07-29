# blockbridge/utils.py

"""
Core Utilities for the BlockBridge Library.

This module provides low-level, reusable helper functions for resiliency,
data integrity, and other common tasks used by the storage clients.
"""

import base64
import functools
import hashlib
import sys
import time
from pathlib import Path


def retry_on_exception(retries: int = 3,
                       delay: float = 1,
                       backoff: float = 2,
                       exceptions: tuple[type[Exception], ...] = (ConnectionError,)):
    """
    A decorator for retrying a function call with exponential backoff.

    Args:
        retries: The maximum number of retries.
        delay: The initial delay between retries in seconds.
        backoff: The factor by which the delay should increase after each retry.
        exceptions: A tuple of exception types to catch and retry on.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _retries, _delay = retries, delay
            while _retries > 0:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if _retries == 1:
                        # Re-raise the last exception if all retries fail
                        raise
                    
                    print(
                        f"Function '{func.__name__}' failed with {type(e).__name__}. "
                        f"Retrying in {_delay:.2f}s... ({_retries-1} retries left).",
                        file=sys.stderr
                    )
                    time.sleep(_delay)
                    _retries -= 1
                    _delay *= backoff
        return wrapper
    return decorator


def calculate_md5_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """
    Calculates the base64-encoded MD5 hash of a local file.

    This function reads large files in chunks to avoid consuming excessive memory.
    The resulting hash is in the format required by many cloud provider APIs
    for server-side data integrity validation (e.g., S3's Content-MD5 header).

    Args:
        file_path: The Path object of the local file to hash.
        chunk_size: The size of chunks to read from the file.

    Returns:
        A string containing the base64-encoded MD5 hash.

    Raises:
        FileNotFoundError: If the file at file_path does not exist.
    """
    md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5.update(chunk)
        
        # Get the raw binary digest and then base64-encode it
        return base64.b64encode(md5.digest()).decode('utf-8')
    except FileNotFoundError:
        raise
    except Exception as e:
        # Catch other potential I/O errors
        raise IOError(f"Could not read file {file_path} to calculate hash. Error: {e}")