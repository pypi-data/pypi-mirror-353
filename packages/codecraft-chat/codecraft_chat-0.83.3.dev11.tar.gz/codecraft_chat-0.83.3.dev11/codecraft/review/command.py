"""
Main review command implementation.
"""

import argparse
import datetime
from pathlib import Path
from fnmatch import fnmatch
from typing import List, Tuple, Set, Dict

from .file_analyzer import FileAnalyzer
from .batch_processor import BatchProcessor
from .report_generator import ReportGenerator


class ReviewCommand:
    def __init__(self, io, coder):
        self.io = io
        self.coder = coder
        self.file_analyzer = FileAnalyzer(io)
        self.batch_processor = BatchProcessor(io)
        self.report_generator = ReportGenerator(io)

    def execute(self, args: str = "") -> None:
        """Execute the review command with the given arguments."""
        self.io.tool_output("\nStarting code review process...")

        # Check if args starts with a quote - indicating a natural language query
        direct_nl_query = None
        if args.startswith('"') and '"' in args[1:]:
            # Extract the quoted part
            end_quote_idx = args.find('"', 1)
            direct_nl_query = args[1:end_quote_idx]
            # Remove the quoted part from args
            args = args[end_quote_idx + 1:].strip()
            self.io.tool_output(f"\nUsing natural language filter: \"{direct_nl_query}\"")

        # Parse command arguments
        parsed_args = self._parse_arguments(args)

        # If we have a direct NL query, add it to focus_args
        if direct_nl_query:
            if parsed_args.focus_args:
                parsed_args.focus_args = direct_nl_query + " " + parsed_args.focus_args
            else:
                parsed_args.focus_args = direct_nl_query

        # Check if this is a diff-based review
        if parsed_args.diff or parsed_args.diff_branch or parsed_args.diff_commit:
            self.io.tool_output("\nPerforming diff-based review...")
            diff_files = self._get_diff_files(parsed_args)

            if not diff_files:
                self.io.tool_error("No changes found to review.")
                return

            self.io.tool_output(f"\nFound {len(diff_files)} files with changes:")
            for rel_path, _, _ in diff_files:
                self.io.tool_output(f"  - {rel_path}")

            # Check for previous TODOs if tracking is enabled
            previous_todos_with_status = []
            if parsed_args.track_todos:
                # Get previous TODOs
                todo_file_path = None
                if parsed_args.todo_file:
                    todo_file_path = Path(self.coder.root) / parsed_args.todo_file
                else:
                    # Try to find the most recent TODO file
                    default_path = Path(self.coder.root) / "TODO.md"
                    if default_path.exists():
                        todo_file_path = default_path

                if todo_file_path:
                    # Parse previous TODOs
                    previous_todos = self._parse_previous_todos(todo_file_path)

                    # Read content of files to be reviewed
                    files_content = {}
                    for rel_path, abs_path, _ in diff_files:
                        try:
                            with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                                files_content[rel_path] = f.read()
                        except Exception:
                            pass

                    # Check resolution status of each TODO
                    self.io.tool_output("\nAnalyzing status of previous TODOs...")
                    for todo in previous_todos:
                        is_resolved, comment = self._check_todo_resolution(todo, files_content)
                        todo['resolved'] = is_resolved
                        todo['resolution_comment'] = comment
                        previous_todos_with_status.append(todo)

                    resolved_count = sum(1 for t in previous_todos_with_status if t['resolved'])
                    total_count = len(previous_todos_with_status)
                    self.io.tool_output(
                        f"Status: {resolved_count} of {total_count} previous TODOs appear to be resolved")

            # Create a special batch for diff review
            output_path = Path(self.coder.root) / (parsed_args.output or "DIFF-REVIEW.md")
            metadata = {
                'Review type': 'Diff-based review',
                'Base': parsed_args.diff_commit or parsed_args.diff_branch or 'HEAD',
                'Files changed': len(diff_files),
                'Review started': datetime.datetime.now().isoformat()
            }

            # Add TODO tracking info to metadata
            if parsed_args.track_todos:
                metadata['TODO tracking'] = 'Enabled'
                metadata['Previous TODOs'] = len(previous_todos_with_status)
                metadata['Resolved TODOs'] = sum(
                    1 for t in previous_todos_with_status if t['resolved'])

            # If we have a natural language query, add it to metadata
            nl_query = parsed_args.focus_args if not parsed_args.focus else parsed_args.focus + " " + parsed_args.focus_args
            if nl_query.strip():
                metadata['Natural language filter'] = nl_query.strip()

            # Initialize the report
            self.report_generator.generate_report(
                output_path=output_path,
                format=parsed_args.format,
                review_content="",
                metadata=metadata
            )

            # Save original coder state
            original_read_only = self.coder.abs_read_only_fnames.copy()
            original_messages = {
                'done': self.coder.done_messages.copy(),
                'cur': self.coder.cur_messages.copy()
            }

            try:
                # Clear previous state
                self.coder.abs_read_only_fnames.clear()
                self.coder.done_messages = []
                self.coder.cur_messages = []

                # Add files to review
                for _, abs_path, _ in diff_files:
                    self.coder.abs_read_only_fnames.add(abs_path)

                # Create and run the review
                prompt = self._create_review_prompt_with_diff(
                    parsed_args,
                    1,
                    1,
                    diff_files,
                    previous_todos_with_status if parsed_args.track_todos else None
                )

                # Disable file mention prompting during review
                original_check_for_file_mentions = self.coder.check_for_file_mentions
                self.coder.check_for_file_mentions = lambda content: None

                try:
                    if parsed_args.auto:
                        original_confirm_ask = self.io.confirm_ask
                        self.io.confirm_ask = lambda q, d=None: True
                        try:
                            self.io.tool_output("Running automated diff review...")
                            self.coder.run(prompt)
                        finally:
                            self.io.confirm_ask = original_confirm_ask
                    else:
                        self.io.tool_output("Starting diff review (press Enter to continue)...")
                        self.coder.run(prompt)
                finally:
                    pass
                # Get the review content
                messages = self.coder.done_messages + self.coder.cur_messages
                assistant_messages = [msg for msg in reversed(
                    messages) if msg["role"] == "assistant"]

                if not assistant_messages:
                    raise ValueError("No review response generated by the model")

                review_content = assistant_messages[0]["content"]

                # Generate the final report
                self.report_generator.generate_report(
                    output_path=output_path,
                    format=parsed_args.format,
                    review_content=review_content,
                    metadata=metadata
                )

                self.io.tool_output(f"\nDiff review completed! Results saved to: {output_path}")
                if parsed_args.format == 'html':
                    self.io.tool_output(
                        f"HTML report available at: {output_path.with_suffix('.html')}")
                elif parsed_args.format == 'json':
                    self.io.tool_output(
                        f"JSON report available at: {output_path.with_suffix('.json')}")

                # Restore original file mention function
                self.coder.check_for_file_mentions = original_check_for_file_mentions

            finally:
                # Restore original state
                self.coder.abs_read_only_fnames = original_read_only
                self.coder.done_messages = original_messages['done']
                self.coder.cur_messages = original_messages['cur']

            return

        # Regular file-based review
        self.io.tool_output("\nGathering files to review...")

        # Debug info about files in chat
        chat_files_count = len(self.coder.abs_read_only_fnames)
        if chat_files_count > 0:
            self.io.tool_output(f"Found {chat_files_count} files in chat")

        files = self._get_files_to_review(parsed_args)
        if not files:
            self.io.tool_error("No files found to review. Please either:")
            self.io.tool_output("1. Add files to the chat using /add")
            self.io.tool_output("2. Ensure you're in a git repository with tracked files")
            self.io.tool_output("3. Specify files using --include pattern")
            self.io.tool_output("4. Use a natural language query to select specific file types")
            return

        # Show files that will be reviewed
        self.io.tool_output("\nFiles to be reviewed:")
        for rel_path, _ in files:
            self.io.tool_output(f"  - {rel_path}")

        # Analyze files and create batches
        self.io.tool_output("\nAnalyzing files for smart grouping...")
        large_files, normal_files = self.file_analyzer.analyze_files(
            files, parsed_args.max_token_per_batch)

        # Get model's token limit and adjust batch size
        model_token_limit = self._get_model_token_limit()
        max_token_per_batch = self._calculate_token_limit(
            model_token_limit, parsed_args.max_token_per_batch)

        # Process files in batches or single batch
        total_tokens = self._estimate_total_tokens(files)
        needs_batching = (
            not parsed_args.no_batch and (
                len(files) > parsed_args.batch_size
                or total_tokens > max_token_per_batch
            )
        )

        # Show processing strategy
        if needs_batching:
            self.io.tool_output(f"\nTotal estimated tokens: {total_tokens:,}")
            self.io.tool_output(f"Maximum tokens per batch: {max_token_per_batch:,}")
            self.io.tool_output("Using batch processing for optimal review...")

            self._process_in_batches(
                large_files, normal_files,
                parsed_args, max_token_per_batch
            )
        else:
            self.io.tool_output("\nProcessing all files in a single review...")
            self._process_single_batch(
                files, parsed_args
            )

        # Show completion message
        output_path = Path(self.coder.root) / (parsed_args.output or "TODO.md")
        self.io.tool_output(f"\nReview completed! Results saved to: {output_path}")
        if parsed_args.format == 'html':
            self.io.tool_output(f"HTML report available at: {output_path.with_suffix('.html')}")
        elif parsed_args.format == 'json':
            self.io.tool_output(f"JSON report available at: {output_path.with_suffix('.json')}")

    def _parse_arguments(self, args: str) -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description="Code review options")
        parser.add_argument(
            "--exclude", help="Glob patterns to exclude, comma-separated (e.g., 'tests/*,docs/*')")
        parser.add_argument(
            "--include", help="Glob patterns to include, comma-separated (e.g., 'src/*.py')")
        parser.add_argument("--max-files", type=int, help="Maximum number of files to review")
        parser.add_argument("--focus", help="Aspects to focus on (e.g., 'security,performance')")
        parser.add_argument("--output", help="Output file path (default: TODO.md)")
        parser.add_argument("--format", choices=['md', 'json',
                            'html'], default='md', help="Output format")
        parser.add_argument("--no-batch", action='store_true',
                            help="Disable automatic batch processing")
        parser.add_argument("--batch-size", type=int, default=10,
                            help="Number of files per batch when batching")
        parser.add_argument("--max-token-per-batch", type=int, help="Maximum tokens per batch")
        parser.add_argument("--exclude-large", action='store_true', help="Exclude very large files")
        parser.add_argument("--auto", action='store_true',
                            help="Automatically proceed without confirmation prompts")
        parser.add_argument("--code-only", action='store_true',
                            help="Focus only on main code files")

        # Add diff-based review options
        parser.add_argument("--diff", action='store_true',
                            help="Review only changes since last commit")
        parser.add_argument("--diff-branch", help="Review changes compared to specified branch")
        parser.add_argument("--diff-commit", help="Review changes compared to specified commit")

        # Add TODO tracking option
        parser.add_argument("--track-todos", action='store_true',
                            help="Track TODOs from previous review")
        parser.add_argument(
            "--todo-file", help="Specify the previous TODO file to track (default: auto-detect)")

        try:
            parsed_args, remaining = parser.parse_known_args(args.split())
            parsed_args.focus_args = " ".join(remaining) if remaining else ""
        except Exception:
            # If parsing fails, use defaults
            parsed_args = argparse.Namespace(
                exclude=None, include=None, max_files=None,
                focus=None, output="TODO.md", format='md',
                no_batch=False, batch_size=10, max_token_per_batch=None,
                exclude_large=False, auto=False, code_only=False,
                diff=False, diff_branch=None, diff_commit=None,
                track_todos=False, todo_file=None,
                focus_args=args
            )

        return parsed_args

    def _get_files_to_review(self, args: argparse.Namespace) -> List[Tuple[str, str]]:
        """Get the list of files to review."""
        # Handle natural language query if provided
        nl_query = args.focus_args if not args.focus else args.focus + " " + args.focus_args

        # Add debug info
        self.io.tool_output("\n--- DEBUG: File Discovery ---")
        self.io.tool_output(f"Repository path: {self.coder.root if self.coder.root else 'Not set'}")
        self.io.tool_output(f"Chat files count: {len(self.coder.abs_read_only_fnames)}")
        repo_status = "Available" if self.coder.repo else "Not available"
        self.io.tool_output(f"Git repository: {repo_status}")

        # If no files are in chat, add relevant code files from repository
        if not self.coder.abs_fnames and not self.coder.abs_read_only_fnames:
            if not self.coder.repo:
                self.io.tool_output("No repository found and no files in chat")
                return []

            files = self.coder.repo.get_tracked_files()
            self.io.tool_output(f"Git tracked files count: {len(files)}")
            if len(files) > 0:
                self.io.tool_output(f"First 5 files: {', '.join(files[:5])}")

            if not files:
                self.io.tool_output("No tracked files found in repository")
                return []

            # Filter files based on extensions and patterns
            filtered_files = self._filter_files(files, args)
            self.io.tool_output(f"After filtering: {len(filtered_files)} files")
            raw_files = [(f, str(Path(self.coder.abs_root_path(f)))) for f in filtered_files]

            # Apply natural language filtering if a query exists
            if nl_query.strip():
                self.io.tool_output(f"Applying NL query: '{nl_query}'")
                nl_filtered_files = self.file_analyzer.filter_files_by_natural_language(
                    raw_files, nl_query)
                if nl_filtered_files:  # Only use filtered files if we got some back
                    self.io.tool_output(f"After NL filtering: {len(nl_filtered_files)} files")
                    return nl_filtered_files
                self.io.tool_output("NL filtering returned no files, using all filtered files")
                return raw_files  # Fall back to all files if filtering returned none

            self.io.tool_output("--- End DEBUG ---")
            return raw_files
        else:
            # Use files that are already in the chat
            self.io.tool_output("Using files from chat")
            raw_files = []
            for fname in self.coder.abs_read_only_fnames:
                rel_fname = self.coder.get_rel_fname(fname)
                raw_files.append((rel_fname, fname))

            # Safeguard to make sure we have files to review
            if not raw_files:
                self.io.tool_error(
                    "No files found in the chat. Please add files with the /add command.")
                return []

            # Apply natural language filtering if a query exists
            if nl_query.strip():
                self.io.tool_output(f"Applying NL query to chat files: '{nl_query}'")
                nl_filtered_files = self.file_analyzer.filter_files_by_natural_language(
                    raw_files, nl_query)
                if nl_filtered_files:  # Only use filtered files if we got some back
                    self.io.tool_output(f"After NL filtering chat files: {len(nl_filtered_files)}")
                    return nl_filtered_files
                self.io.tool_output("NL filtering returned no files, using all chat files")
                return raw_files  # Fall back to all files if filtering returned none

            self.io.tool_output(f"Using {len(raw_files)} files from chat")
            self.io.tool_output("--- End DEBUG ---")
            return raw_files

    def _filter_files(self, files: List[str], args: argparse.Namespace) -> List[str]:
        """Filter files based on command arguments."""
        # Common code file extensions
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.rs', '.sql', '.sh',
            '.bash', '.html', '.css', '.scss', '.sass', '.less', '.vue', '.json',
            '.xml', '.yaml', '.yml', '.toml', '.ini', '.conf', '.gradle', '.maven',
            '.dockerfile', '.tf', '.hcl'
        }

        self.io.tool_output("\n--- DEBUG: File Filtering ---")
        self.io.tool_output(f"Starting with {len(files)} files")

        # Check if this is a general "review entire codebase" query
        is_general_review = False
        if args.focus_args and "entire" in args.focus_args.lower() and "codebase" in args.focus_args.lower():
            is_general_review = True
            self.io.tool_output(
                "Detected 'entire codebase' review request - using more inclusive filtering")

        # Config and build files to exclude when using --code-only
        config_file_patterns = [
            '**/package.json', '**/package-lock.json', '**/tsconfig*.json',
            '**/angular.json', '**/.postcssrc.json', '**/tailwind.config.js',
            '**/.eslintrc.*', '**/.prettierrc.*', '**/webpack.config.*',
            '**/babel.config.*', '**/jest.config.*', '**/karma.conf.*',
            '**/.vscode/*', '**/node_modules/**', '**/dist/**', '**/build/**',
            '**/*.md', '**/*.lock', '**/Dockerfile', '**/docker-compose.*',
            '**/.gitignore', '**/.env*', '**/yarn.lock'
        ]

        # Process include/exclude patterns
        include_patterns = args.include.split(',') if args.include else None
        exclude_patterns = args.exclude.split(',') if args.exclude else []

        # Add config file patterns to exclude if --code-only is specified
        if args.code_only and not is_general_review:
            if not exclude_patterns:
                exclude_patterns = config_file_patterns
            else:
                exclude_patterns.extend(config_file_patterns)
            self.io.tool_output("Code-only mode: excluding configuration and build files")

        # Default exclusions for very large files
        large_file_patterns = ['**/package-lock.json', '**/yarn.lock', '**/node_modules/**']
        if args.exclude_large and not is_general_review:
            if not exclude_patterns:
                exclude_patterns = large_file_patterns
            else:
                exclude_patterns.extend(large_file_patterns)

        # Show patterns being used
        if include_patterns:
            self.io.tool_output(f"Include patterns: {include_patterns}")
        if exclude_patterns:
            self.io.tool_output(f"Exclude patterns: {exclude_patterns}")

        filtered_files = []
        excluded_by_extension = 0
        excluded_by_pattern = 0

        for file in files:
            # Skip if not a code file
            if not is_general_review and not any(file.lower().endswith(ext) for ext in code_extensions):
                excluded_by_extension += 1
                continue

            # Apply include/exclude patterns
            if exclude_patterns and any(fnmatch(file, pat) for pat in exclude_patterns):
                excluded_by_pattern += 1
                continue

            if include_patterns and not any(fnmatch(file, pat) for pat in include_patterns):
                excluded_by_pattern += 1
                continue

            filtered_files.append(file)

            # Check max files limit
            if args.max_files and len(filtered_files) >= args.max_files:
                self.io.tool_output(f"Reached maximum file limit ({args.max_files})")
                break

        self.io.tool_output(f"Excluded {excluded_by_extension} files by extension")
        self.io.tool_output(f"Excluded {excluded_by_pattern} files by pattern")
        self.io.tool_output(f"Kept {len(filtered_files)} files after filtering")

        # Display a sample of the files being reviewed
        if filtered_files:
            sample_size = min(5, len(filtered_files))
            self.io.tool_output(f"Sample files: {', '.join(filtered_files[:sample_size])}")

        self.io.tool_output("--- End Filtering DEBUG ---")
        return filtered_files

    def _get_model_token_limit(self) -> int:
        """Get the model's token limit."""
        model_token_limit = self.coder.main_model.info.get('max_input_tokens', 0)
        if model_token_limit <= 0:
            # If we can't determine the model's limit, use a conservative default
            model_token_limit = 4096
        return model_token_limit

    def _calculate_token_limit(self, model_token_limit: int, max_token_per_batch: int = None) -> int:
        """Calculate the safe token limit per batch."""
        # Reserve tokens for the prompt and overhead
        prompt_tokens = 2000  # Rough estimate for prompt
        reserved_tokens = prompt_tokens + 2000  # Additional overhead

        # Calculate safe token limit (70% of available tokens after reserving for prompt)
        safe_token_limit = int((model_token_limit - reserved_tokens) * 0.7)

        # Use the specified max_token_per_batch or calculate based on model
        max_token_per_batch = max_token_per_batch or safe_token_limit

        # Ensure max_token_per_batch is reasonable
        max_token_per_batch = min(max_token_per_batch, safe_token_limit)
        max_token_per_batch = max(max_token_per_batch, 1000)  # Ensure minimum reasonable size

        return max_token_per_batch

    def _estimate_total_tokens(self, files: List[Tuple[str, str]]) -> int:
        """Estimate total tokens for all files."""
        total_tokens = 0
        for rel_path, abs_path in files:
            try:
                file_size = Path(abs_path).stat().st_size
                if file_size > 1000000:  # Files over 1MB
                    total_tokens += min(file_size // 3, 50000)  # Cap at 50k tokens
                else:
                    with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                        total_tokens += len(content.split()) * 1.5  # Rough estimate
            except Exception:
                total_tokens += 1000  # Default estimate

        return int(total_tokens)

    def _process_in_batches(
        self,
        large_files: List[Tuple[str, str]],
        normal_files: List[Tuple[str, str]],
        args: argparse.Namespace,
        max_token_per_batch: int
    ) -> None:
        """Process files in batches."""
        # Check for previous TODOs if tracking is enabled
        previous_todos_with_status = []
        if args.track_todos:
            # Determine the TODO file path
            todo_file_path = None
            if args.todo_file:
                todo_file_path = Path(self.coder.root) / args.todo_file
            else:
                # Try to find the most recent TODO file
                default_path = Path(self.coder.root) / "TODO.md"
                if default_path.exists():
                    todo_file_path = default_path

            if todo_file_path:
                # Parse previous TODOs
                previous_todos = self._parse_previous_todos(todo_file_path)

                # Read content of files to be reviewed
                files_content = {}
                for rel_path, abs_path in large_files + normal_files:
                    try:
                        with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                            files_content[rel_path] = f.read()
                    except Exception:
                        pass

                # Check resolution status of each TODO
                self.io.tool_output("\nAnalyzing status of previous TODOs...")
                for todo in previous_todos:
                    is_resolved, comment = self._check_todo_resolution(todo, files_content)
                    todo['resolved'] = is_resolved
                    todo['resolution_comment'] = comment
                    previous_todos_with_status.append(todo)

                resolved_count = sum(1 for t in previous_todos_with_status if t['resolved'])
                total_count = len(previous_todos_with_status)
                self.io.tool_output(
                    f"Status: {resolved_count} of {total_count} previous TODOs appear to be resolved")

        # Analyze dependencies and create batches
        self.io.tool_output("\nAnalyzing file dependencies...")
        file_tokens, file_imports, file_imported_by, directory_groups, file_types = (
            self.file_analyzer.analyze_dependencies(normal_files)
        )

        self.io.tool_output("Creating optimized review batches...")
        batches = self.batch_processor.create_batches(
            large_files, normal_files,
            file_tokens, file_imports, file_imported_by,
            directory_groups, file_types,
            max_token_per_batch, args.batch_size
        )

        self.io.tool_output(f"\nOrganized review into {len(batches)} smart batches")

        # Process each batch
        output_path = Path(self.coder.root) / (args.output or "TODO.md")
        metadata = self._create_metadata(args, len(normal_files) + len(large_files), len(batches))

        # Add TODO tracking info to metadata
        if args.track_todos:
            metadata['TODO tracking'] = 'Enabled'
            metadata['Previous TODOs'] = len(previous_todos_with_status)
            metadata['Resolved TODOs'] = sum(1 for t in previous_todos_with_status if t['resolved'])

        # Initialize the report
        self.report_generator.generate_report(
            output_path=output_path,
            format=args.format,
            review_content="",
            metadata=metadata
        )

        # Process each batch
        for batch_idx, batch in enumerate(batches, 1):
            batch_files = [f[0] for f in batch]
            batch_info = {
                'batch_idx': batch_idx,
                'description': self._get_batch_description(batch),
                'files': batch_files
            }

            self.io.tool_output(f"\nProcessing batch {batch_idx}/{len(batches)}:")
            for rel_path in batch_files:
                self.io.tool_output(f"  - {rel_path}")

            try:
                # Pass previous TODOs to review prompt if tracking is enabled
                # Disable file mention prompting during review
                original_check_for_file_mentions = self.coder.check_for_file_mentions
                self.coder.check_for_file_mentions = lambda content: None

                try:
                    review_content = self._review_batch(
                        batch,
                        args,
                        batch_idx,
                        len(batches),
                        previous_todos_with_status if args.track_todos else None
                    )

                    # Generate report for this batch
                    self.report_generator.generate_report(
                        output_path=output_path,
                        format=args.format,
                        review_content=review_content,
                        batch_info=batch_info,
                        metadata=metadata
                    )

                    self.io.tool_output(f"✓ Completed batch {batch_idx}")
                finally:
                    # Restore original file mention function
                    self.coder.check_for_file_mentions = original_check_for_file_mentions

            except Exception as e:
                self.io.tool_error(f"Error processing batch {batch_idx}: {str(e)}")
                self.io.tool_output("Continuing with next batch...")
                continue

    def _process_single_batch(self, files: List[Tuple[str, str]], args: argparse.Namespace) -> None:
        """Process all files in a single batch."""
        # Create metadata for the review
        metadata = self._create_metadata(args, len(files), 1)

        # Estimate tokens for all files
        batch_with_tokens = []
        for rel_path, abs_path in files:
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                token_estimate = len(content) // 3  # Rough estimate
                batch_with_tokens.append((rel_path, abs_path, token_estimate))
            except Exception:
                # If we can't read the file, use a default estimate
                batch_with_tokens.append((rel_path, abs_path, 1000))

        # Initialize the report
        output_path = Path(self.coder.root) / (args.output or "TODO.md")
        self.report_generator.generate_report(
            output_path=output_path,
            format=args.format,
            review_content="",
            metadata=metadata
        )

        # Check for previous TODOs if tracking is enabled
        previous_todos_with_status = None
        if args.track_todos:
            todo_file_path = None
            if args.todo_file:
                todo_file_path = Path(self.coder.root) / args.todo_file
            else:
                default_path = Path(self.coder.root) / "TODO.md"
                if default_path.exists():
                    todo_file_path = default_path

            if todo_file_path:
                previous_todos = self._parse_previous_todos(todo_file_path)

                if previous_todos:
                    files_content = {}
                    for rel_path, abs_path in files:
                        try:
                            with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                                files_content[rel_path] = f.read()
                        except Exception:
                            pass

                    previous_todos_with_status = []
                    for todo in previous_todos:
                        is_resolved, comment = self._check_todo_resolution(todo, files_content)
                        todo['resolved'] = is_resolved
                        todo['resolution_comment'] = comment
                        previous_todos_with_status.append(todo)

        # Disable file mention prompting during review
        original_check_for_file_mentions = self.coder.check_for_file_mentions
        self.coder.check_for_file_mentions = lambda content: None

        try:
            # Review the batch
            review_content = self._review_batch(
                batch_with_tokens, args, 1, 1, previous_todos_with_status)

            # Generate the final report
            self.report_generator.generate_report(
                output_path=output_path,
                format=args.format,
                review_content=review_content,
                metadata=metadata
            )

            self.io.tool_output(f"\nReview completed successfully!")
            self.io.tool_output(f"Report saved to: {output_path}")

            if args.format == 'html':
                self.io.tool_output(f"HTML report available at: {output_path.with_suffix('.html')}")
            elif args.format == 'json':
                self.io.tool_output(f"JSON report available at: {output_path.with_suffix('.json')}")
        finally:
            # Restore original file mention function
            self.coder.check_for_file_mentions = original_check_for_file_mentions

    def _create_metadata(self, args: argparse.Namespace, total_files: int, total_batches: int) -> dict:
        """Create metadata for the report."""
        metadata = {
            'Total files': total_files,
            'Number of batches': total_batches
        }

        if args.exclude:
            metadata['Excluded patterns'] = args.exclude.split(',')
        if args.include:
            metadata['Included patterns'] = args.include.split(',')

        focus_areas = []
        if args.focus:
            focus_areas.extend(args.focus.split(','))
        if args.focus_args:
            focus_areas.append(args.focus_args)
        if focus_areas:
            metadata['Focus areas'] = focus_areas

        metadata['Review started'] = datetime.datetime.now().isoformat()
        return metadata

    def _get_batch_description(self, batch: List[Tuple[str, str, int]]) -> str:
        """Get a description for a batch of files."""
        # Get unique directories and file types in the batch
        dirs = set(Path(rel_path).parent for rel_path, _, _ in batch)
        types = set(Path(rel_path).suffix for rel_path, _, _ in batch)

        if len(dirs) == 1:
            return f"files from {next(iter(dirs))}"
        elif len(types) == 1:
            return f"{next(iter(types))} files"
        else:
            return "related files"

    def _review_batch(
        self,
        batch: List[Tuple[str, str, int]],
        args: argparse.Namespace,
        batch_idx: int,
        total_batches: int,
        previous_todos: List[dict] = None
    ) -> str:
        """Review a batch of files and return the review content."""
        # Save original coder state
        original_read_only = self.coder.abs_read_only_fnames.copy()
        original_messages = {
            'done': self.coder.done_messages.copy(),
            'cur': self.coder.cur_messages.copy()
        }

        # Disable file mention prompting during review
        original_check_for_file_mentions = self.coder.check_for_file_mentions
        self.coder.check_for_file_mentions = lambda content: None

        try:
            # Clear previous batch state
            self.coder.abs_read_only_fnames.clear()
            self.coder.done_messages = []
            self.coder.cur_messages = []

            # Add files to review
            for rel_path, abs_path, _ in batch:
                try:
                    # Verify file still exists and is readable
                    if not Path(abs_path).is_file():
                        self.io.tool_error(f"File not found or not accessible: {rel_path}")
                        continue

                    self.coder.abs_read_only_fnames.add(abs_path)
                except Exception as e:
                    self.io.tool_error(f"Error adding file {rel_path}: {str(e)}")
                    continue

            if not self.coder.abs_read_only_fnames:
                raise ValueError("No valid files to review in this batch")

            # Create review prompt
            prompt = self._create_review_prompt(args, batch_idx, total_batches, previous_todos)

            # Run the review
            if args.auto:
                original_confirm_ask = self.io.confirm_ask
                self.io.confirm_ask = lambda q, d=None: True
                try:
                    self.io.tool_output("Running automated review...")
                    self.coder.run(prompt)
                finally:
                    self.io.confirm_ask = original_confirm_ask
            else:
                self.io.tool_output("Starting review")
                self.coder.run(prompt)

            # Get the review content
            messages = self.coder.done_messages + self.coder.cur_messages
            assistant_messages = [msg for msg in reversed(messages) if msg["role"] == "assistant"]

            if not assistant_messages:
                raise ValueError("No review response generated by the model")

            return assistant_messages[0]["content"]

        except Exception as e:
            error_msg = f"Error during batch review: {str(e)}"
            self.io.tool_error(error_msg)
            return f"Error: {error_msg}"

        finally:
            # Restore original state
            self.coder.abs_read_only_fnames = original_read_only
            self.coder.done_messages = original_messages['done']
            self.coder.cur_messages = original_messages['cur']

            # Restore original file mention function
            self.coder.check_for_file_mentions = original_check_for_file_mentions

    def _create_review_prompt(self, args: argparse.Namespace, batch_idx: int, total_batches: int, previous_todos=None) -> str:
        """Create the review prompt for a batch."""
        prompt = """Please conduct a comprehensive code review focusing on:

- Code quality (readability, maintainability, structure)
- Best practices (naming conventions, modularity, design patterns)
- Performance considerations
- Security vulnerabilities
- Scalability and architecture
- API design and usage
- Dependency management
- Documentation and comments

IMPORTANT: Your review should be exhaustive and detailed. For each file, carefully examine the code and identify issues, including:

1. Specific bugs or logic errors
2. Security vulnerabilities or unsafe practices
3. Performance bottlenecks or inefficient code
4. Non-idiomatic or difficult to maintain patterns
5. Missing error handling or edge cases
6. Architectural issues or design flaws
7. Documentation gaps

Format each issue as an actionable TODO item:
- [ ] **Issue**: [Brief description]
      **Location**: [File path and/or function name]
      **Priority**: [High/Medium/Low]
      **Details**: [Detailed explanation and how to fix]
      **Category**: [Code Quality/Security/Performance/etc.]
      **Effort**: [Small/Medium/Large]
      **Dependencies**: [Any dependencies or prerequisites]

Your review should contain multiple detailed TODO items that provide actionable feedback."""

        # Add previous TODO status if tracked
        if previous_todos:
            prompt += "\n\n## Previous TODOs Status\n\nThe following issues were identified in previous reviews. Please verify if they've been resolved properly:\n\n"

            for todo in previous_todos:
                status_marker = "x" if todo['resolved'] else " "
                prompt += f"- [{status_marker}] **Previous Issue**: {todo['issue']}\n"
                if todo['location']:
                    prompt += f"      **Location**: {todo['location']}\n"
                prompt += f"      **Status**: {todo['resolution_comment']}\n"
                prompt += f"      **Original Priority**: {todo['priority']}\n\n"

            prompt += """Please carefully verify all previous TODOs listed above:
1. For TODOs that are actually resolved, keep them marked with [x]
2. For TODOs that are still present, update them in your review with current details, keeping the original [x] or [ ] status
3. IMPORTANT: Do not duplicate issues - each finding should appear exactly once in your review
4. Include any new issues you find that weren't in the previous TODO list

Your final report should include a consolidated list where:
- Previously resolved TODOs show with [x]
- Still-present TODOs keep their original status (resolved or not)
- New TODOs are added with [ ]
"""

        # Handle natural language filtering
        nl_query = args.focus_args
        if nl_query.strip() and not args.focus:
            prompt += f"\n\nThis review specifically focuses on: \"{nl_query.strip()}\"\n"
            prompt += "Pay special attention to aspects mentioned in the query above, while still covering other important issues you find."

        # Handle explicit focus areas
        elif args.focus or (args.focus and args.focus_args):
            focus_areas = []
            if args.focus:
                focus_areas.extend(args.focus.split(','))
            if args.focus_args:
                focus_areas.append(args.focus_args)
            prompt += f"\n\nAdditionally, please pay special attention to: {', '.join(focus_areas)}"

        if total_batches > 1:
            prompt += f"\n\nThis is batch {batch_idx} of {total_batches}."

        # Add final instructions
        prompt += """

IMPORTANT FINAL INSTRUCTIONS:
1. Provide a thorough and detailed review
2. Don't be overly brief - identify multiple issues
3. For each issue, provide specific locations and detailed explanations
4. If you find multiple issues, group them by file and priority
5. Do NOT just say "The file most likely to need changes" - provide actual TODOs
6. Do NOT leave out critical details - be comprehensive and thorough
"""

        return prompt

    def _get_diff_files(self, args: argparse.Namespace) -> List[Tuple[str, str, str]]:
        """Get files and their changes from git diff.
        Returns a list of tuples (relative_path, absolute_path, diff_content)
        """
        if not self.coder.repo:
            self.io.tool_error("No git repository found. Cannot perform diff-based review.")
            return []

        try:
            # Determine the comparison base
            base = None
            if args.diff_commit:
                base = args.diff_commit
            elif args.diff_branch:
                base = args.diff_branch
            elif args.diff:
                base = 'HEAD'

            if not base:
                return []

            # Get the diff
            if base == 'HEAD':
                # Get unstaged and staged changes
                diff_files = self.coder.repo.get_dirty_files()
                changes = []
                for file in diff_files:
                    try:
                        diff = self.coder.repo.repo.git.diff('HEAD', '--', file)
                        if diff.strip():
                            changes.append((file, diff))
                    except Exception as e:
                        self.io.tool_warning(f"Error getting diff for {file}: {str(e)}")
            else:
                # Get changes compared to specified base
                try:
                    diff_output = self.coder.repo.repo.git.diff(base, '--name-only')
                    diff_files = diff_output.splitlines()
                    changes = []
                    for file in diff_files:
                        try:
                            diff = self.coder.repo.repo.git.diff(base, '--', file)
                            if diff.strip():
                                changes.append((file, diff))
                        except Exception as e:
                            self.io.tool_warning(f"Error getting diff for {file}: {str(e)}")
                except Exception as e:
                    self.io.tool_error(f"Error comparing with {base}: {str(e)}")
                    return []

            # Convert to list of (rel_path, abs_path, diff_content)
            result = []
            for file, diff in changes:
                abs_path = str(Path(self.coder.abs_root_path(file)))
                result.append((file, abs_path, diff))

            return result

        except Exception as e:
            self.io.tool_error(f"Error getting diff: {str(e)}")
            return []

    def _create_review_prompt_with_diff(self, args: argparse.Namespace, batch_idx: int, total_batches: int, diffs: List[Tuple[str, str, str]], previous_todos: List[dict] = None) -> str:
        """Create a review prompt that includes diff information."""
        base_prompt = """Please review the following code changes focusing on:

- Code quality and best practices
- Potential bugs or issues
- Security implications
- Performance considerations
- Documentation needs
- Test coverage

For each file's changes, analyze:
1. The impact and scope of changes
2. Any potential side effects
3. Whether the changes follow project conventions
4. If there are better alternatives
5. If additional changes are needed

Format each issue as an actionable TODO item:
- [ ] **Issue**: [Brief description]
      **Location**: [File path and line numbers]
      **Priority**: [High/Medium/Low]
      **Details**: [Detailed explanation and how to fix]
      **Category**: [Code Quality/Security/Performance/etc.]
      **Effort**: [Small/Medium/Large]
      **Dependencies**: [Any dependencies or prerequisites]

"""
        # Add previous TODO status if tracked
        if previous_todos:
            base_prompt += "## Previous TODOs Status\n\nThe following issues were identified in previous reviews. Please verify if they've been resolved properly:\n\n"

            for todo in previous_todos:
                status_marker = "x" if todo['resolved'] else " "
                base_prompt += f"- [{status_marker}] **Previous Issue**: {todo['issue']}\n"
                if todo['location']:
                    base_prompt += f"      **Location**: {todo['location']}\n"
                base_prompt += f"      **Status**: {todo['resolution_comment']}\n"
                base_prompt += f"      **Original Priority**: {todo['priority']}\n\n"

            base_prompt += """Please carefully verify all previous TODOs listed above:
1. For TODOs that are actually resolved, keep them marked with [x]
2. For TODOs that are still present, update them in your review with current details, keeping the original [x] or [ ] status
3. IMPORTANT: Do not duplicate issues - each finding should appear exactly once in your review
4. Include any new issues you find that weren't in the previous TODO list

Your final report should include a consolidated list where:
- Previously resolved TODOs show with [x]
- Still-present TODOs keep their original status (resolved or not)
- New TODOs are added with [ ]
"""

        base_prompt += "\n## Changes to review:\n"
        # Add diff information
        for file, _, diff in diffs:
            base_prompt += f"\n### Changes in {file}:\n```diff\n{diff}\n```\n"

        if args.focus or args.focus_args:
            focus_areas = []
            if args.focus:
                focus_areas.extend(args.focus.split(','))
            if args.focus_args:
                focus_areas.append(args.focus_args)
            base_prompt += f"\nAdditionally, please pay special attention to: {', '.join(focus_areas)}"

        if total_batches > 1:
            base_prompt += f"\n\nThis is batch {batch_idx} of {total_batches}."

        return base_prompt

    def _parse_previous_todos(self, todo_file: Path) -> List[dict]:
        """Parse TODOs from a previous review file.

        Returns a list of TODO items, each containing:
            - issue: The issue description
            - location: The file path and line numbers
            - resolved: Boolean indicating if the issue appears to be resolved
            - details: Additional details about the issue
        """
        self.io.tool_output(f"Reading previous TODOs from {todo_file}...")
        todos = []

        try:
            if not todo_file.exists():
                self.io.tool_warning(f"Previous TODO file not found: {todo_file}")
                return []

            with open(todo_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse markdown TODO items
            import re
            todo_pattern = r'- \[([ xX])\] \*\*Issue\*\*: (.*?)(?:\n\s+\*\*Location\*\*: (.*?))?(?:\n\s+\*\*Priority\*\*: (.*?))?(?:\n\s+\*\*Details\*\*: (.*?))?(?:\n\s+\*\*Category\*\*: (.*?))?(?:\n\s+\*\*Effort\*\*: (.*?))?(?:\n\s+\*\*Dependencies\*\*: (.*?))?(?=\n- \[|$)'

            matches = re.findall(todo_pattern, content, re.DOTALL)
            for match in matches:
                status, issue, location, priority, details, category, effort, dependencies = match
                resolved = status.strip().lower() in ['x']

                todos.append({
                    'issue': issue.strip(),
                    'location': location.strip() if location else '',
                    'resolved': resolved,
                    'details': details.strip() if details else '',
                    'priority': priority.strip() if priority else '',
                    'category': category.strip() if category else '',
                    'effort': effort.strip() if effort else '',
                    'dependencies': dependencies.strip() if dependencies else '',
                })

            self.io.tool_output(
                f"Found {len(todos)} previous TODO items ({sum(1 for t in todos if t['resolved'])} resolved)")
            return todos

        except Exception as e:
            self.io.tool_warning(f"Error parsing previous TODOs: {str(e)}")
            return []

    def _check_todo_resolution(self, todo: dict, files_content: Dict[str, str]) -> Tuple[bool, str]:
        """Check if a TODO item has been resolved.

        Returns a tuple of (is_resolved, resolution_comment)
        """
        # If already marked as resolved in the TODO file, keep that status
        if todo['resolved']:
            return True, "Previously marked as resolved"

        # Extract the file path from the location
        location = todo['location']
        details = todo['details']

        # Try to parse the location to get the file
        import re
        file_match = re.search(r'`([^`]+)`', location)
        file_path = None
        if file_match:
            file_path = file_match.group(1)

        # If no explicit file path, try to find it in the details
        if not file_path and details:
            file_matches = re.findall(r'`([^`]+\.[a-zA-Z]+)`', details)
            if file_matches:
                file_path = file_matches[0]

        # Check all files in the review if we couldn't determine a specific file
        if not file_path:
            # Generic check based on issue description
            issue_keywords = set(todo['issue'].lower().split())
            resolution_likelihood = 0

            for file, content in files_content.items():
                content_lower = content.lower()
                matching_keywords = sum(
                    1 for kw in issue_keywords if kw in content_lower and len(kw) > 4)
                if matching_keywords > len(issue_keywords) / 2:
                    resolution_likelihood += 0.5

            if resolution_likelihood > 0.5:
                return True, "Issue likely resolved (based on keyword analysis)"
            else:
                return False, "Issue may still be present (couldn't find specific file reference)"

        # Check if the file exists and has been modified
        for file, content in files_content.items():
            if file_path in file:
                # Extract code snippets from details that might have been fixed
                code_snippets = re.findall(r'`([^`]+)`', details)

                if code_snippets:
                    # Check if problematic code snippets are still present
                    for snippet in code_snippets:
                        if len(snippet.strip()) > 5 and snippet.strip() in content:
                            return False, f"Issue still present - found code snippet '{snippet[:20]}...' in {file}"

                # Try to extract specific issues from the TODO
                if 'missing' in todo['issue'].lower():
                    missing_items = re.findall(r'missing ([a-zA-Z0-9_]+)', todo['issue'].lower())
                    for item in missing_items:
                        if item not in content.lower():
                            return False, f"Item '{item}' is still missing in {file}"

                if 'unused' in todo['issue'].lower() or 'unnecessary' in todo['issue'].lower():
                    unused_items = re.findall(r'unused ([a-zA-Z0-9_]+)', todo['issue'].lower())
                    unused_items.extend(re.findall(
                        r'unnecessary ([a-zA-Z0-9_]+)', todo['issue'].lower()))
                    for item in unused_items:
                        if item in content.lower():
                            return False, f"Unused item '{item}' still present in {file}"

                # Check based on issue category
                category = todo['category'].lower()
                if 'documentation' in category and '///' not in content and '"""' not in content:
                    return False, "Documentation issue may still be present"

                if 'security' in category and any(kw in content.lower() for kw in ['password', 'credential', 'token', 'auth']):
                    return False, "Security issue may still require verification"

                # Basic heuristic - if we couldn't find concrete evidence, assume it might be fixed
                return True, "Issue likely resolved (file has been modified)"

        return False, "Issue may still be present (couldn't analyze effectively)"
