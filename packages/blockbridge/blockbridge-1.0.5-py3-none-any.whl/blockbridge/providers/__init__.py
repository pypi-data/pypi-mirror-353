# blockbridge/providers/__init__.py

"""
BlockBridge Providers Sub-package

This package contains the specific client implementations for each major,
named cloud storage provider, each adhering to the BlockBridgeInterface.
"""

from .aws import AWS_S3_Storage
from .azure import AzureBlobStorage
from .cloudflare import Cloudflare_R2_Storage
from .gcs import GCSStorage
from .wasabi import Wasabi_Storage

# Define what is publicly available when a user does 'from blockbridge.providers import *'
# This creates a clean public API for this sub-package.
__all__ = [
    "AWS_S3_Storage",
    "AzureBlobStorage",
    "Cloudflare_R2_Storage",
    "GCSStorage",
    "Wasabi_Storage",
]