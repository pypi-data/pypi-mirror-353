# blockbridge/operations/sync.py
import os
import sys
import json
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from .. import get_client, BlockBridgeInterface
from ..exceptions import StorageException


class SyncManager:
    """
    Manages high-level, rsync-style synchronization operations between
    storage providers.

    This class orchestrates the process of comparing a source and destination
    prefix and only transferring new or modified files. It can optionally delete
    extraneous files from the destination. It incorporates Tier 2 (Stateful Sync)
    and Tier 3 (Native Server-Side Copy) optimizations.
    """

    def _get_clients(self, source_uri: str, dest_uri: str,
                     source_creds: dict | None = None,
                     dest_creds: dict | None = None) -> tuple[BlockBridgeInterface, BlockBridgeInterface]:
        """Instantiates clients for source and destination."""
        source_client = get_client(source_uri, creds=source_creds)
        dest_client = get_client(dest_uri, creds=dest_creds)
        return source_client, dest_client

    def _load_state_from_dest(self, client: BlockBridgeInterface, bucket_uri: str) -> dict:
        """Downloads and loads the .blockbridge_state.json manifest from the destination."""
        state_file_uri = bucket_uri + ".blockbridge_state.json"
        temp_dir = None
        try:
            if client.object_exists(state_file_uri):
                print(f"Info: Found existing state file at destination.", file=sys.stderr)
                local_path, temp_dir = client.download(state_file_uri)
                with open(local_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception:
            print(f"Warning: Could not read state file. Forcing full sync.", file=sys.stderr)
            return {}
        finally:
            if temp_dir:
                temp_dir.cleanup()

    def _save_state_to_dest(self, client: BlockBridgeInterface, bucket_uri: str, state_data: dict):
        """Uploads the new state manifest to the destination bucket."""
        state_file_uri = bucket_uri + ".blockbridge_state.json"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)
            local_path = Path(f.name)
        try:
            client.upload(local_path, state_file_uri)
            print(f"Info: Saved updated state file to destination.", file=sys.stderr)
        finally:
            os.remove(local_path)

    def _compute_sync_plan(self, source_map: dict, dest_map: dict, delete: bool) -> dict:
        """Compares metadata maps to determine which files to transfer or delete."""
        plan = {"transfer": [], "delete": []}
        source_keys, dest_keys = set(source_map.keys()), set(dest_map.keys())

        for key, source_versions in source_map.items():
            source_latest = source_versions[0]
            if key not in dest_map:
                plan["transfer"].append(source_latest)
                continue

            dest_latest = dest_map[key][0]
            source_etag = source_latest.get('etag')
            dest_etag = dest_latest.get('etag')

            is_different = False
            if source_etag and dest_etag and source_etag != dest_etag:
                is_different = True
            elif source_latest.get('size') != dest_latest.get('size') or \
                 source_latest.get('last_modified') > dest_latest.get('last_modified'):
                is_different = True
            if is_different:
                plan["transfer"].append(source_latest)

        if delete:
            keys_to_delete = dest_keys - source_keys
            plan["delete"].extend([dest_map[key][0]['uri'] for key in keys_to_delete])
            
        return plan

    def _execute_sync_plan(self, plan: dict, source_uri: str, dest_uri: str,
                           source_client: BlockBridgeInterface, dest_client: BlockBridgeInterface, **kwargs):
        """Takes a plan and executes all copy and delete operations concurrently."""
        concurrency = kwargs.get('concurrency', 8)
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            
            for source_meta in plan['transfer']:
                relative_key = source_meta['uri'][len(source_uri):]
                dest_obj_uri = dest_uri + relative_key
                task = lambda s_uri=source_meta['uri'], d_uri=dest_obj_uri: \
                    self._copy_object(source_client, s_uri, dest_client, d_uri, **kwargs)
                futures.append(executor.submit(task))

            for dest_obj_uri in plan['delete']:
                task = lambda d_uri=dest_obj_uri: dest_client.delete_object(d_uri)
                futures.append(executor.submit(task))
            
            self._process_futures(futures, len(plan['transfer']) + len(plan['delete']))

    def _copy_object(self, source_client, source_uri, dest_client, dest_uri, **kwargs):
        """Helper that decides between native copy and streaming."""
        if type(source_client) is type(dest_client):
            try:
                source_client.native_copy(source_uri, dest_uri)
                return
            except OperationNotSupported:
                pass
        
        temp_dir = None
        try:
            local_path, temp_dir = source_client.download(source_uri, validate_checksum=kwargs.get('validate_checksum', False))
            dest_client.upload(local_path, dest_uri, make_public=False, validate_checksum=kwargs.get('validate_checksum', False))
        finally:
            if temp_dir:
                temp_dir.cleanup()
                
    def _process_futures(self, futures: list, total_ops: int):
        """Processes futures from the executor, tracks progress, and handles errors."""
        completed_count, failed_count = 0, 0
        for future in as_completed(futures):
            try:
                future.result()
                completed_count += 1
                sys.stderr.write(f"\r  Progress: {completed_count}/{total_ops} operations completed...")
                sys.stderr.flush()
            except Exception as e:
                failed_count += 1
                print(f"\n  ERROR: A sync operation failed: {e}", file=sys.stderr)
        
        print(f"\n" + "-" * 20, file=sys.stderr)
        if failed_count > 0:
            raise StorageException(f"{failed_count} sync operation(s) failed.")

    def run(self, source_uri: str, dest_uri: str, delete: bool = False,
             stateful: bool = True, source_creds: dict = None, dest_creds: dict = None, **kwargs):
        """Executes the one-way synchronization from source to destination."""
        if not source_uri.endswith('/'): source_uri += '/'
        if not dest_uri.endswith('/'): dest_uri += '/'

        source_client, dest_client = self._get_clients(source_uri, dest_uri, source_creds, dest_creds)

        print("Gathering metadata...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_source = executor.submit(source_client.list_objects_with_metadata, source_uri, **kwargs)
            future_dest = executor.submit(self._load_state_from_dest, dest_client, dest_uri) if stateful else executor.submit(dest_client.list_objects_with_metadata, dest_uri, **kwargs)
            source_map, dest_map = future_source.result(), future_dest.result()
        
        print(f"Found {len(source_map)} source objects and {len(dest_map)} destination objects/records.", file=sys.stderr)
        plan = self._compute_sync_plan(source_map, dest_map, delete)

        if not plan['transfer'] and not plan['delete']:
            print("✅ Source and destination are already in sync.", file=sys.stderr)
            return

        print(f"Sync Plan: {len(plan['transfer'])} to transfer, {len(plan['delete'])} to delete.", file=sys.stderr)
        self._execute_sync_plan(plan, source_uri, dest_uri, source_client, dest_client, **kwargs)
        
        if stateful:
            self._save_state_to_dest(dest_client, dest_uri, source_map)

        print("✅ Sync operation complete.", file=sys.stderr)