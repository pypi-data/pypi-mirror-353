# blockbridge/operations/__init__.py

"""
BlockBridge Operations Sub-package

This package contains high-level, multi-cloud operation managers that
orchestrate complex workflows, such as cloning and synchronization, between
different storage providers.

These managers use the provider-specific clients to perform their tasks.
"""

from .clone import CloneManager
from .sync import SyncManager

# Define what is publicly available when a user does 'from blockbridge.operations import *'
# This creates a clean public API for this sub-package.
__all__ = [
    "CloneManager",
    "SyncManager",
]