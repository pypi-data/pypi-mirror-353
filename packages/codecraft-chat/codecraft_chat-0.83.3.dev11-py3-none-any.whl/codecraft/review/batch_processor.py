"""
Batch processing logic for code review.
"""

from collections import defaultdict
from typing import List, Set, Dict, Tuple, Any, DefaultDict
import os

class BatchProcessor:
    def __init__(self, io):
        self.io = io

    def create_batches(
        self,
        large_files: List[Tuple[str, str]],
        normal_files: List[Tuple[str, str]],
        file_tokens: Dict[str, int],
        file_imports: DefaultDict[str, Set[str]],
        file_imported_by: DefaultDict[str, Set[str]],
        directory_groups: DefaultDict[str, List],
        file_types: DefaultDict[str, List],
        max_token_per_batch: int,
        batch_size: int
    ) -> List[List[Tuple[str, str, int]]]:
        """Create optimized batches for review."""
        batches = []
        processed_files = set()

        # First, create individual batches for each large file
        for rel_path, abs_path in large_files:
            try:
                file_size = os.path.getsize(abs_path)
                token_estimate = file_size // 3  # Very conservative estimate
            except Exception:
                token_estimate = 50000  # Default for large files

            # If the file is too large for even a single batch, skip it
            if token_estimate > max_token_per_batch * 0.9:
                self.io.tool_warning(f"File {rel_path} is too large for review (estimated {token_estimate} tokens). Skipping.")
                continue

            # Create a batch with just this file
            batches.append([(rel_path, abs_path, token_estimate)])
            processed_files.add(rel_path)

        # Then create batches by directory (keeping related files together)
        for dir_name, dir_files in sorted(directory_groups.items(), key=lambda x: len(x[1]), reverse=True):
            if not dir_files or all(rel_path in processed_files for rel_path, _, _ in dir_files):
                continue

            # Create batches from this directory
            while True:
                batch = self._create_batch_with_limit(
                    dir_files, max_token_per_batch, batch_size, processed_files,
                    file_imports, file_imported_by
                )
                if not batch:
                    break
                batches.append(batch)

        # Then create batches by file type for remaining files
        for ext, type_files in sorted(file_types.items(), key=lambda x: len(x[1]), reverse=True):
            if not type_files or all(rel_path in processed_files for rel_path, _, _ in type_files):
                continue

            # Create batches from this file type
            while True:
                batch = self._create_batch_with_limit(
                    type_files, max_token_per_batch, batch_size, processed_files,
                    file_imports, file_imported_by
                )
                if not batch:
                    break
                batches.append(batch)

        # Finally, add any remaining files
        remaining_files = [(rel_path, abs_path, file_tokens.get(rel_path, 1000))
                          for rel_path, abs_path in normal_files
                          if rel_path not in processed_files]

        while remaining_files:
            batch = self._create_batch_with_limit(
                remaining_files, max_token_per_batch, batch_size, processed_files,
                file_imports, file_imported_by
            )
            if not batch:
                # If we can't create a batch with the current limits, force include at least one file
                if remaining_files:
                    rel_path, abs_path, tokens = remaining_files[0]
                    batch = [(rel_path, abs_path, tokens)]
                    processed_files.add(rel_path)
                    remaining_files = remaining_files[1:]

            if batch:
                batches.append(batch)
            else:
                break

        return batches

    def _create_batch_with_limit(
        self,
        file_list: List[Tuple[str, str, int]],
        token_limit: int,
        max_files: int,
        processed_files: Set[str],
        file_imports: DefaultDict[str, Set[str]],
        file_imported_by: DefaultDict[str, Set[str]]
    ) -> List[Tuple[str, str, int]]:
        """Create a batch of files respecting token and size limits."""
        batch = []
        current_tokens = 0

        for rel_path, abs_path, tokens in file_list:
            if rel_path in processed_files:
                continue

            # If adding this file would exceed the token limit, skip
            if current_tokens + tokens > token_limit:
                continue

            # If we've reached the max files per batch, stop
            if len(batch) >= max_files:
                break

            batch.append((rel_path, abs_path, tokens))
            current_tokens += tokens
            processed_files.add(rel_path)

            # Try to include directly related files (imports/imported by)
            related_files = []
            for related_rel in file_imports.get(rel_path, set()) | file_imported_by.get(rel_path, set()):
                for other_rel, other_abs, other_tokens in file_list:
                    if other_rel == related_rel and other_rel not in processed_files:
                        related_files.append((other_rel, other_abs, other_tokens))

            # Add related files if they fit
            for related_rel, related_abs, related_tokens in related_files:
                if current_tokens + related_tokens <= token_limit and len(batch) < max_files:
                    batch.append((related_rel, related_abs, related_tokens))
                    current_tokens += related_tokens
                    processed_files.add(related_rel)

        return batch if batch else None 