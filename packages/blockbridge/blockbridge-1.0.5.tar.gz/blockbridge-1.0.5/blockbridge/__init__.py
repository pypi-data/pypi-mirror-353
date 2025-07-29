# blockbridge/__init__.py
"""
BlockBridge: The Multi-Cloud Storage & Operations SDK
"""
# Import the universal interface and exceptions first
from .base import BlockBridgeInterface
from .exceptions import *

# Import the main facade
from .facade import BlockBridge

# --- CORRECTED IMPORTS ---
# Import the generic clients from their top-level modules
from .s3_compatible import S3_Compatible_Storage
from .providers.http import HTTPS_Storage # Assuming http.py is in providers

# Import the specific, named provider clients from the 'providers' sub-package
from .providers.aws import AWS_S3_Storage
from .providers.azure import AzureBlobStorage
from .providers.cloudflare import Cloudflare_R2_Storage
from .providers.gcs import GCSStorage
from .providers.wasabi import Wasabi_Storage

# Define what is publicly available
__all__ = [
    "BlockBridge", "BlockBridgeInterface", "AWS_S3_Storage", "AzureBlobStorage",
    "Cloudflare_R2_Storage", "GCSStorage", "Wasabi_Storage", "S3_Compatible_Storage",
    "HTTPS_Storage", "StorageException", "InitializationError", "ObjectNotFound",
    "OperationNotSupported", "DestinationNotEmptyError", "VerificationError", "SourceModifiedError",
]

__version__ = "1.0.5" # Incremented version for the bug fix