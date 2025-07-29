# blockbridge/operations/clone.py
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from .. import get_client, BlockBridgeInterface
from ..exceptions import StorageException, DestinationNotEmptyError, VerificationError, SourceModifiedError

class CloneManager:
    """
    Manages high-level, safe bucket and prefix cloning operations.

    This class orchestrates a transactional workflow to ensure data is cloned
    with the highest degree of integrity, even for very large datasets.
    """

    def _get_clients(self, source_uri: str, dest_uri: str,
                     source_creds: dict | None = None,
                     dest_creds: dict | None = None) -> tuple[BlockBridgeInterface, BlockBridgeInterface]:
        """Instantiates clients for source and destination."""
        source_client = get_client(source_uri, creds=source_creds)
        dest_client = get_client(dest_uri, creds=dest_creds)
        return source_client, dest_client

    def _verify_destination_is_empty(self, client: BlockBridgeInterface, uri: str):
        """Checks if the target destination prefix is empty before starting."""
        print(f"Verifying final destination '{uri}' is empty...", file=sys.stderr)
        if next(iter(client.list_objects(uri)), None):
            raise DestinationNotEmptyError(f"Clone failed: Final destination '{uri}' is not empty.")
        print("✅ Final destination is empty.", file=sys.stderr)

    def _scan_prefix(self, client: BlockBridgeInterface, uri: str, all_versions: bool) -> dict:
        """Scans a prefix and returns a detailed metadata map."""
        print(f"Scanning metadata at '{uri}' (versions={all_versions})...", file=sys.stderr)
        return client.list_objects_with_metadata(uri, all_versions=all_versions)

    def _verify_clone_consistency(self, source_before_map: dict, source_after_map: dict, staging_map: dict):
        """Performs a post-flight verification to ensure data integrity."""
        print("Verifying transfer integrity...", file=sys.stderr)
        
        # 1. Check if source was modified during the operation
        if set(source_before_map.keys()) != set(source_after_map.keys()):
            raise SourceModifiedError("Source was modified during clone operation (files added/removed). Aborting.")
        
        for key, before_versions in source_before_map.items():
            after_versions = source_after_map.get(key, [])
            if len(before_versions) != len(after_versions):
                raise SourceModifiedError(f"Source object '{key}' had version history modified during clone. Aborting.")

        # 2. Check if the staged copy matches the final state of the source
        if len(source_after_map) != len(staging_map):
            raise VerificationError(f"Item count mismatch. Source: {len(source_after_map)}, Staging: {len(staging_map)}.")

        for key, source_versions in source_after_map.items():
            if key not in staging_map:
                raise VerificationError(f"Missing object '{key}' in staging area.")
            
            # Compare checksums of latest versions for a quick check
            source_latest = source_versions[0]
            staging_latest = staging_map[key][0]
            if source_latest.get('etag') and staging_latest.get('etag') and source_latest['etag'] != staging_latest['etag']:
                raise VerificationError(f"Checksum mismatch for object '{key}'.")
        
        print("✅ Verification successful.", file=sys.stderr)

    def _commit_staging_to_final(self, client: BlockBridgeInterface, staging_uri: str, final_uri: str, **kwargs):
        """Atomically moves files from the staging area to the final destination."""
        print(f"Committing transfer from staging to '{final_uri}'...", file=sys.stderr)
        objects_to_move = client.list_objects(staging_uri, all_versions=True) # Move all versions if they exist
        concurrency = kwargs.get('concurrency', 16) # Use higher concurrency for fast rename
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_uri = {
                executor.submit(client.native_rename, obj_uri, f"{final_uri.rstrip('/')}/{obj_uri[len(staging_uri):]}"): obj_uri
                for obj_uri in objects_to_move
            }
            self._process_futures(future_to_uri, "Committing object")

    def run(self, source_uri: str, dest_uri: str,
            clone_all_versions: bool = False, source_creds: dict | None = None, dest_creds: dict | None = None,
            **kwargs):
        """
        Executes the transactional bucket/prefix cloning operation.

        Args:
            source_uri: The URI of the source prefix (e.g., "s3://source-bucket/folder/").
            dest_uri: The URI of the destination prefix.
            clone_all_versions: If True, clones every historical version of each object.
            source_creds: Optional explicit credentials for the source client.
            dest_creds: Optional explicit credentials for the destination client.
            **kwargs: Additional options like `concurrency`, `max_objects`, `validate_checksum`.
        """
        if not source_uri.endswith('/'): source_uri += '/'
        if not dest_uri.endswith('/'): dest_uri += '/'

        source_client, dest_client = self._get_clients(source_uri, dest_uri, source_creds, dest_creds)
        staging_uri = f"{dest_uri}.blockbridge_stage_{uuid.uuid4().hex[:8]}/"

        try:
            # 1. Pre-flight Check
            self._verify_destination_is_empty(dest_client, dest_uri)

            # 2. Initial Scan
            source_before_map = self._scan_prefix(source_client, source_uri, clone_all_versions)
            if not source_before_map:
                print("✅ Source is empty. Nothing to clone.", file=sys.stderr)
                return

            # 3. Execute Transfer to Staging Area
            self._execute_prefix_copy(source_client, source_uri, dest_client, staging_uri, clone_all_versions, **kwargs)

            # 4. Post-flight Verification
            source_after_map = self._scan_prefix(source_client, source_uri, clone_all_versions)
            staging_map = self._scan_prefix(dest_client, staging_uri, clone_all_versions)
            self._verify_clone_consistency(source_before_map, source_after_map, staging_map)
            
            # 5. Commit Phase
            self._commit_staging_to_final(dest_client, staging_uri, dest_uri, **kwargs)

        finally:
            # 6. Cleanup Staging Area
            print("Cleaning up staging area...", file=sys.stderr)
            dest_client.delete_prefix(staging_uri)
        
        print("✅ Clone operation complete.", file=sys.stderr)

    # --- Internal Concurrent Execution Logic ---
    def _execute_prefix_copy(self, source_client, source_uri, dest_client, dest_uri, all_versions, **kwargs):
        concurrency = kwargs.get('concurrency', 8)
        max_objects = kwargs.get('max_objects')

        objects_map = source_client.list_objects_with_metadata(source_uri, all_versions=all_versions)
        tasks_to_run = [version_meta for versions in objects_map.values() for version_meta in versions]

        if not tasks_to_run: return

        if max_objects and len(tasks_to_run) > max_objects:
            raise StorageException(f"Object count ({len(tasks_to_run)}) exceeds max_objects limit of {max_objects}.")

        print(f"Found {len(tasks_to_run)} total object versions to copy. Starting concurrent transfer...", file=sys.stderr)
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_uri = {
                executor.submit(
                    self._execute_object_copy, source_client, task['uri'], dest_client,
                    f"{dest_uri.rstrip('/')}/{task['uri'][len(source_uri):]}",
                    task.get('version_id'), **kwargs
                ): task['uri']
                for task in tasks_to_run
            }
            self._process_futures(future_to_uri, "Copying object")
    
    def _execute_object_copy(self, source_client, source_uri, dest_client, dest_uri, source_version_id, **kwargs):
        if type(source_client) is type(dest_client):
            try:
                source_client.native_copy(source_uri, dest_uri, source_version_id=source_version_id)
                return
            except OperationNotSupported:
                pass
        
        temp_dir = None
        try:
            local_path, temp_dir = source_client.download(source_uri, validate_checksum=kwargs.get('validate_checksum', False))
            dest_client.upload(local_path, dest_uri, make_public=False, validate_checksum=kwargs.get('validate_checksum', False))
        finally:
            if temp_dir: temp_dir.cleanup()
            
    def _process_futures(self, future_to_uri_map: dict, operation_name: str):
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
            raise StorageException(f"{failed_count} {operation_name}(s) failed during execution.")