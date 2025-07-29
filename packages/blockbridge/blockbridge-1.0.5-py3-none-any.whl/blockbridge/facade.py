# blockbridge/facade.py
import os
import sys
import uuid
import json
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import providers
from .base import BlockBridgeInterface
from .exceptions import StorageException, DestinationNotEmptyError, VerificationError, SourceModifiedError


class BlockBridge:
    """
    The primary facade for the BlockBridge library.

    This class provides a simple, high-level API for performing storage
    operations that feel like local OS commands (e.g., copy, move, sync),
    while seamlessly handling interactions between different cloud providers.
    """

    def _get_client(self, uri: str, creds: dict | None = None) -> BlockBridgeInterface:
        """
        Internal factory to get the correct provider client based on the URI
        and instantiate it with the provided credentials.
        """
        creds = creds or {}

        if uri.startswith("gs://"):
            return providers.GCSStorage(**creds)
        elif uri.startswith("s3://"):
            # The application provides provider-specific credentials.
            # We instantiate the client best suited for those credentials.
            if creds.get("account_id"):  # Cloudflare R2
                return providers.Cloudflare_R2_Storage(**creds)
            # Wasabi needs a region and its endpoint URL is derived from it
            elif "wasabisys.com" in creds.get("endpoint_url", "") or "wasabi" in creds.get("provider_hint", ""):
                return providers.Wasabi_Storage(**creds)
            # Generic S3-compatibles require an endpoint
            elif creds.get("endpoint_url"):
                return providers.S3_Compatible_Storage(**creds)
            else:  # Default to AWS S3
                return providers.AWS_S3_Storage(**creds)
        elif "blob.core.windows.net" in uri:
            return providers.AzureBlobStorage(**creds)
        elif uri.startswith(("https://", "http://")):
            return providers.HTTPS_Storage(**creds)

        raise ValueError(f"Unsupported storage URI scheme or host in: {uri}")

    def copy(self, source_uri: str, dest_uri: str, source_creds: dict = None, dest_creds: dict = None, **kwargs):
        """
        Copies an object or a prefix (folder) from source to destination.

        Args:
            source_uri: The full URI of the source object or prefix (e.g., "gs://bucket/folder/").
            dest_uri: The full URI of the destination object or prefix.
            source_creds (dict, optional): Explicit credentials for the source.
            dest_creds (dict, optional): Explicit credentials for the destination.
            **kwargs: Additional options like `concurrency`, `max_objects`, `validate_checksum`.
        """
        source_client = self._get_client(source_uri, source_creds)
        dest_client = self._get_client(dest_uri, dest_creds)

        if source_uri.endswith('/'):
            self._execute_prefix_copy(source_client, source_uri, dest_client, dest_uri, is_clone=False, **kwargs)
        else:
            self._execute_object_copy(source_client, source_uri, dest_client, dest_uri, **kwargs)

    def move(self, source_uri: str, dest_uri: str, source_creds: dict = None, dest_creds: dict = None, **kwargs):
        """
        Moves an object or a prefix (folder) from source to destination.
        This is a transactional copy-then-delete operation.
        """
        source_client = self._get_client(source_uri, source_creds)

        print(f"Starting move from {source_uri} to {dest_uri}...", file=sys.stderr)
        self.copy(source_uri, dest_uri, source_creds, dest_creds, **kwargs)

        print(f"✅ Copy successful. Deleting source: {source_uri}", file=sys.stderr)
        if not source_uri.endswith('/'):
            source_client.delete_object(source_uri)
        else:
            source_client.delete_prefix(source_uri)
        print("✅ Move operation complete.", file=sys.stderr)

    def clone_bucket(self, source_uri: str, dest_uri: str, source_creds: dict = None, dest_creds: dict = None, **kwargs):
        """
        Clones an entire bucket using a transactional workflow, requiring the destination to be empty.
        It copies to a staging area, verifies consistency, then commits the changes.
        """
        if not source_uri.endswith('/'): source_uri += '/'
        if not dest_uri.endswith('/'): dest_uri += '/'

        source_client, dest_client = self._get_client(source_uri, source_creds), self._get_client(dest_uri, dest_creds)
        staging_uri = f"{dest_uri}.blockbridge_stage_{uuid.uuid4().hex[:8]}/"

        print(f"Verifying final destination '{dest_uri}' is empty before cloning...", file=sys.stderr)
        if next(iter(dest_client.list_objects(dest_uri)), None):
            raise DestinationNotEmptyError(f"Clone failed: Final destination '{dest_uri}' is not empty.")
        print("✅ Final destination is empty.", file=sys.stderr)

        try:
            print(f"Scanning source bucket '{source_uri}'...", file=sys.stderr)
            source_before_map = source_client.list_objects_with_metadata(source_uri)

            self._execute_prefix_copy(source_client, source_uri, dest_client, staging_uri, is_clone=True, **kwargs)

            print("Verifying transfer integrity...", file=sys.stderr)
            source_after_map = source_client.list_objects_with_metadata(source_uri)
            staging_map = dest_client.list_objects_with_metadata(staging_uri)

            self._verify_clone_consistency(source_before_map, source_after_map, staging_map)
            print("✅ Verification successful.", file=sys.stderr)

            print(f"Committing transfer from staging to '{dest_uri}'...", file=sys.stderr)
            self._commit_staging_to_final(dest_client, staging_uri, dest_uri, **kwargs)

        finally:
            print("Cleaning up staging area...", file=sys.stderr)
            dest_client.delete_prefix(staging_uri)
        
        print("✅ Clone operation complete.", file=sys.stderr)

    def sync(self, source_uri: str, dest_uri: str, delete: bool = False, stateful: bool = True,
             source_creds: dict = None, dest_creds: dict = None, **kwargs):
        """Performs a one-way, high-performance, rsync-style sync from source to destination."""
        if not source_uri.endswith('/'): source_uri += '/'
        if not dest_uri.endswith('/'): dest_uri += '/'

        source_client, dest_client = self._get_client(source_uri, source_creds), self._get_client(dest_uri, dest_creds)

        print("Gathering metadata from source and destination...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_source = executor.submit(source_client.list_objects_with_metadata, source_uri, **kwargs)
            future_dest = executor.submit(self._load_state_from_dest, dest_client, dest_uri) if stateful else executor.submit(dest_client.list_objects_with_metadata, dest_uri, **kwargs)
            source_map, dest_map = future_source.result(), future_dest.result()
        print(f"Found {len(source_map)} source objects and {len(dest_map)} destination objects/records.", file=sys.stderr)

        plan = self._compute_sync_plan(source_map, dest_map, delete)
        if not plan['transfer'] and not plan['delete']:
            print("✅ Source and destination are already in sync. Nothing to do.", file=sys.stderr)
            return

        print(f"Sync Plan: {len(plan['transfer'])} to transfer, {len(plan['delete'])} to delete.", file=sys.stderr)
        self._execute_sync_plan(plan, source_uri, dest_uri, source_client, dest_client, **kwargs)

        if stateful:
            self._save_state_to_dest(dest_client, dest_uri, source_map)

        print("✅ Sync operation complete.", file=sys.stderr)

    def list_objects(self, uri: str, creds: dict = None, **kwargs) -> list[str]:
        """Lists all object URIs under a given prefix."""
        client = self._get_client(uri, creds)
        return client.list_objects(uri, **kwargs)

    def object_exists(self, uri: str, creds: dict = None) -> bool:
        """Checks if an object exists at the given URI."""
        client = self._get_client(uri, creds)
        return client.object_exists(uri)

    # --- Internal Helper Methods ---

    def _execute_object_copy(self, source_client, source_uri, dest_client, dest_uri, **kwargs):
        """Helper to copy a single object, deciding between native and streaming."""
        validate = kwargs.get('validate_checksum', False)
        
        if type(source_client) is type(dest_client):
            try:
                source_client.native_copy(source_uri, dest_uri)
                return
            except exceptions.OperationNotSupported:
                pass

        temp_dir = None
        try:
            local_path, temp_dir = source_client.download(source_uri, validate_checksum=validate)
            dest_client.upload(local_path, dest_uri, make_public=kwargs.get('make_public', False), validate_checksum=validate)
        finally:
            if temp_dir: temp_dir.cleanup()

    def _execute_prefix_copy(self, source_client, source_uri, dest_client, dest_uri, is_clone: bool, **kwargs):
        """Helper to copy a prefix concurrently."""
        concurrency = kwargs.get('concurrency', 8)
        max_objects = kwargs.get('max_objects')

        objects = source_client.list_objects(source_uri)
        if not objects: return

        if max_objects and len(objects) > max_objects:
            raise exceptions.StorageException(f"Object count ({len(objects)}) exceeds max_objects limit.")

        op_name = "Cloning" if is_clone else "Copying"
        print(f"Found {len(objects)} objects. Starting concurrent {op_name.lower()} with {concurrency} workers...", file=sys.stderr)

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_uri = {
                executor.submit(self._execute_object_copy, source_client, obj_uri, dest_client, f"{dest_uri.rstrip('/')}/{obj_uri[len(source_uri):]}", **kwargs): obj_uri
                for obj_uri in objects
            }
            self._process_futures(future_to_uri, f"{op_name} object")

    def _verify_clone_consistency(self, source_before, source_after, staging_map):
        """Verifies integrity after a clone operation."""
        if set(source_before.keys()) != set(source_after.keys()):
            raise SourceModifiedError("Source was modified during clone operation. Aborting.")
        
        if len(source_after) != len(staging_map):
            raise VerificationError(f"Item count mismatch. Source: {len(source_after)}, Staging: {len(staging_map)}.")
        
        for key, source_versions in source_after.items():
            source_latest = source_versions[0]
            if key not in staging_map:
                raise VerificationError(f"Missing object {key} in staging area.")
            
            staging_latest = staging_map[key][0]
            if source_latest.get('etag') and staging_latest.get('etag') and source_latest['etag'] != staging_latest['etag']:
                raise VerificationError(f"Checksum mismatch for object {key}.")

    def _commit_staging_to_final(self, client, staging_uri, final_uri, **kwargs):
        """Moves files from the staging area to the final destination."""
        objects_to_move = client.list_objects(staging_uri)
        concurrency = kwargs.get('concurrency', 16)
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_uri = {
                executor.submit(client.native_rename, obj_uri, f"{final_uri.rstrip('/')}/{obj_uri[len(staging_uri):]}"): obj_uri
                for obj_uri in objects_to_move
            }
            self._process_futures(future_to_uri, "Committing object")

    def _compute_sync_plan(self, source_map, dest_map, delete):
        """Compares metadata maps to determine which files to transfer or delete."""
        plan = {"transfer": [], "delete": []}
        source_keys, dest_keys = set(source_map.keys()), set(dest_map.keys())

        for key, source_versions in source_map.items():
            source_latest = source_versions[0]
            if key not in dest_map:
                plan["transfer"].append(source_latest)
                continue
            
            dest_latest = dest_map[key][0]
            source_etag, dest_etag = source_latest.get('etag'), dest_latest.get('etag')

            is_different = False
            if source_etag and dest_etag and source_etag != dest_etag:
                is_different = True
            elif source_latest.get('size') != dest_latest.get('size') or source_latest.get('last_modified') > dest_latest.get('last_modified'):
                is_different = True
            if is_different:
                plan["transfer"].append(source_latest)

        if delete:
            plan["delete"].extend([dest_map[key][0]['uri'] for key in (dest_keys - source_keys)])
        return plan

    def _execute_sync_plan(self, plan, source_uri, dest_uri, source_client, dest_client, **kwargs):
        """Takes a plan and executes all copy and delete operations concurrently."""
        concurrency = kwargs.get('concurrency', 8)
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for source_meta in plan['transfer']:
                dest_obj_uri = f"{dest_uri.rstrip('/')}/{source_meta['uri'][len(source_uri):]}"
                futures.append(executor.submit(self._execute_object_copy, source_client, source_meta['uri'], dest_client, dest_obj_uri, **kwargs))
            for dest_obj_uri in plan['delete']:
                futures.append(executor.submit(dest_client.delete_object, dest_obj_uri))
            
            self._process_futures(futures, "Sync operation")
            
    def _process_futures(self, future_to_uri_map: dict, operation_name: str):
        """Generic helper to process futures from a thread pool and report progress."""
        completed_count, failed_count = 0, 0
        total_ops = len(future_to_uri_map)
        
        if total_ops == 0: return

        for future in as_completed(future_to_uri_map):
            uri = future_to_uri_map[future]
            try:
                future.result()
                completed_count += 1
                sys.stderr.write(f"\r  Progress: {completed_count}/{total_ops} {operation_name}s completed...")
                sys.stderr.flush()
            except Exception as e:
                failed_count += 1
                print(f"\n  ERROR: {operation_name} failed for {uri}. Reason: {e}", file=sys.stderr)

        print(f"\n" + "-" * 20, file=sys.stderr)
        if failed_count > 0:
            raise StorageException(f"{failed_count} {operation_name}(s) failed.")

    def _load_state_from_dest(self, client, bucket_uri):
        """Downloads and loads the state file from the destination bucket."""
        state_file_uri = f"{bucket_uri.rstrip('/')}/.blockbridge_state.json"
        temp_dir = None
        try:
            if client.object_exists(state_file_uri):
                local_path, temp_dir = client.download(state_file_uri)
                with open(local_path, 'r') as f: return json.load(f)
            return {}
        except exceptions.ObjectNotFound: return {}
        except Exception: return {}
        finally:
            if temp_dir: temp_dir.cleanup()

    def _save_state_to_dest(self, client, bucket_uri, state_data):
        """Uploads the new state file to the destination bucket."""
        state_file_uri = f"{bucket_uri.rstrip('/')}/.blockbridge_state.json"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as f:
            json.dump(state_data, f, indent=2)
            local_path = Path(f.name)
        try:
            client.upload(local_path, state_file_uri)
        finally:
            os.remove(local_path)