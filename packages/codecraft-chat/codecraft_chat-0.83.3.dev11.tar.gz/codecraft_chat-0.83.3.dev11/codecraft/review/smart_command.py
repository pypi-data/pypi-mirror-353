"""
Smart review command implementation.
"""

import argparse
import datetime
import os
from pathlib import Path
from fnmatch import fnmatch
from typing import List, Tuple, Set, Dict, Any, Optional
from collections import defaultdict
import json

from .config_manager import ConfigManager
from .context_manager import ReviewContext
from .smart_analyzer import SmartAnalyzer
from .file_analyzer import FileAnalyzer
from .batch_processor import BatchProcessor
from .report_generator import ReportGenerator

class SmartReviewCommand:
    """Improved review command with better handling of large codebases."""
    
    def __init__(self, io, coder):
        """Initialize the smart review command.
        
        Args:
            io: The IO interface for interacting with the user.
            coder: The Coder instance for accessing repository information.
        """
        # Set up basic parameters
        self.io = io
        self.coder = coder
        self.workspace_root = self.coder.root if self.coder.root else os.getcwd()
        
        # Initialize components
        self.file_analyzer = FileAnalyzer(self.io, self.coder)
        self.report_generator = ReportGenerator(self.io, self.workspace_root)
        self.smart_analyzer = SmartAnalyzer(self.workspace_root, io, self.config_manager)
        self.context = ReviewContext(self.io, self.workspace_root)
        self.config_manager = ConfigManager(self.io, self.workspace_root)
        
        # Check if the requests package is available for Kanban integration
        try:
            import requests
            from .kanban_integration import export_todos_to_kanban
            self.export_todos_to_kanban = export_todos_to_kanban
            self.kanban_available = True
        except ImportError:
            self.kanban_available = False
    
    def execute(self, args: str = "") -> None:
        """Execute the smart review command with the given arguments."""
        # Parse command arguments first, before any output
        parsed_args = self._parse_arguments(args)
        
        # Now proceed with normal review process
        self.io.tool_output("\nStarting smart code review process...")
        
        # Check if args starts with a quote - indicating a natural language query
        direct_nl_query = None
        if isinstance(args, str) and args.startswith('"') and '"' in args[1:]:
            # Extract the quoted part
            end_quote_idx = args.find('"', 1)
            direct_nl_query = args[1:end_quote_idx]
            # Remove the quoted part from args
            args = args[end_quote_idx+1:].strip()
            self.io.tool_output(f"\nUsing natural language filter: \"{direct_nl_query}\"")
        
        # If we have a direct NL query, add it to focus_args
        if direct_nl_query:
            if parsed_args.focus_args:
                parsed_args.focus_args = f"{direct_nl_query} {parsed_args.focus_args}"
            else:
                parsed_args.focus_args = direct_nl_query
        
        # Show configuration being used
        self._show_config_info(parsed_args)
        
        # Check if this is a diff-based review
        if parsed_args.diff or parsed_args.diff_branch or parsed_args.diff_commit:
            self._handle_diff_review(parsed_args)
            return
        
        # Handle progress report
        if parsed_args.progress:
            self._show_progress_report()
            return
        
        # Handle continue operation
        if parsed_args.continue_review:
            self._continue_review(parsed_args)
            return
        
        # Regular file-based review
        self.io.tool_output("\nGathering files to review...")
        
        # Get files to review
        files_to_review = self._get_files_to_review(parsed_args)
        
        if not files_to_review:
            self.io.tool_error("No files found to review.")
            return
        
        self.io.tool_output(f"\nFound {len(files_to_review)} files to review.")
        
        # Use the smart analyzer to prioritize files
        prioritized_files = self.smart_analyzer.prioritize_files(files_to_review)
        
        # Apply natural language filtering if a query exists
        nl_query = ""
        if hasattr(parsed_args, 'focus_args') and parsed_args.focus_args:
            nl_query = parsed_args.focus_args
        if hasattr(parsed_args, 'focus') and parsed_args.focus:
            if nl_query:
                nl_query = f"{parsed_args.focus} {nl_query}"
            else:
                nl_query = parsed_args.focus
        
        if nl_query.strip():
            prioritized_files = self.smart_analyzer.filter_by_natural_language(prioritized_files, nl_query)
            self.context.set_recent_focus(nl_query.strip())
        
        if not prioritized_files:
            self.io.tool_error("No files matched your criteria after filtering.")
            return
        
        # Update context with total files count
        self.context.set_total_files(len(prioritized_files))
        
        # Remove score from prioritized files for backward compatibility
        files_for_processing = [(rel_path, abs_path) for rel_path, abs_path, _ in prioritized_files]
        
        # Get token limits
        model_token_limit = self._get_model_token_limit()
        max_token_per_batch = parsed_args.max_token_per_batch or self.config_manager.get_token_limits()["per_batch"]
        max_token_per_batch = self._calculate_token_limit(model_token_limit, max_token_per_batch)
        
        # Separate large files from normal files
        large_files, normal_files = self.file_analyzer.analyze_files(files_for_processing, max_token_per_batch)
        
        # Process the files in batches
        if parsed_args.no_batch or (len(normal_files) + len(large_files) <= parsed_args.batch_size):
            # Process all files in a single batch
            self._process_single_batch(files_for_processing, parsed_args)
        else:
            # Process files in multiple batches
            self._process_in_batches(large_files, normal_files, parsed_args, max_token_per_batch)
        
        # Show progress after this review session
        self._show_progress_report()
    
    def _parse_arguments(self, args: str) -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description="Advanced code review options")
        parser.add_argument(
            "--exclude", help="Glob patterns to exclude, comma-separated (e.g., 'tests/*,docs/*')")
        parser.add_argument(
            "--include", help="Glob patterns to include, comma-separated (e.g., 'src/*.py')")
        parser.add_argument("--max-files", type=int, help="Maximum number of files to review")
        parser.add_argument("--focus", help="Aspects to focus on (e.g., 'security,performance')")
        parser.add_argument("--output", help="Output file path (default: uses config)")
        parser.add_argument("--format", choices=['md', 'json',
                            'html'], help="Output format (default: uses config)")
        parser.add_argument("--no-batch", action='store_true',
                            help="Disable automatic batch processing")
        parser.add_argument("--batch-size", type=int, help="Number of files per batch when batching (default: uses config)")
        parser.add_argument("--max-token-per-batch", type=int, help="Maximum tokens per batch (default: uses config)")
        parser.add_argument("--exclude-large", action='store_true', help="Exclude very large files")
        parser.add_argument("--auto", action='store_true', help="Automatically proceed without confirmation prompts")
        parser.add_argument("--code-only", action='store_true', help="Focus only on main code files")
        
        # Add diff-based review options
        parser.add_argument("--diff", action='store_true', help="Review only changes since last commit")
        parser.add_argument("--diff-branch", help="Review changes compared to specified branch")
        parser.add_argument("--diff-commit", help="Review changes compared to specified commit")
        
        # Add TODO tracking option
        parser.add_argument("--track-todos", action='store_true', help="Track TODOs from previous review")
        parser.add_argument("--todo-file", help="Specify the previous TODO file to track (default: auto-detect)")
        
        # Add smart review options
        parser.add_argument("--smart", action='store_true', help="Use smart prioritization (default: True)")
        parser.add_argument("--no-smart", action='store_true', help="Disable smart prioritization")
        parser.add_argument("--progress", action='store_true', help="Show review progress report and exit")
        parser.add_argument("--continue", action='store_true', dest='continue_review', help="Continue previous review session")
        parser.add_argument("--reset", action='store_true', help="Reset review context and start fresh")
        parser.add_argument("--save-config", action='store_true', help="Save current settings as default configuration")
        
        try:
            parsed_args, remaining = parser.parse_known_args(args.split())
            parsed_args.focus_args = " ".join(remaining) if remaining else ""
        except Exception:
            # If parsing fails, use defaults
            parsed_args = argparse.Namespace(
                exclude=None, include=None, max_files=None,
                focus=None, output=None, format='md',
                no_batch=False, batch_size=10, max_token_per_batch=None,
                exclude_large=False, auto=False, code_only=False,
                diff=False, diff_branch=None, diff_commit=None,
                track_todos=False, todo_file=None,
                smart=True, no_smart=False, progress=False,
                continue_review=False, reset=False, save_config=False,
                focus_args=args
            )
        
        # If --no-smart is specified, set smart=False
        if parsed_args.no_smart:
            parsed_args.smart = False
        
        # Reset context if requested
        if parsed_args.reset:
            self.context.reset_context()
            self.io.tool_output("Review context has been reset.")
        
        # Save config if requested
        if parsed_args.save_config:
            self._save_current_config(parsed_args)
        
        return parsed_args
    
    def _show_config_info(self, args: argparse.Namespace) -> None:
        """Show configuration information."""
        self.io.tool_output("\n--- Configuration ---")
        self.io.tool_output(f"Smart prioritization: {'Enabled' if args.smart else 'Disabled'}")
        self.io.tool_output(f"Batch processing: {'Disabled' if args.no_batch else 'Enabled'}")
        
        if not args.no_batch:
            self.io.tool_output(f"Batch size: {args.batch_size} files")
            
        token_limits = self.config_manager.get_token_limits()
        self.io.tool_output(f"Token limit per batch: {args.max_token_per_batch or token_limits['per_batch']}")
        
        # Show exclude patterns
        exclude_patterns = args.exclude.split(',') if args.exclude else self.config_manager.get_exclude_patterns()
        if exclude_patterns:
            self.io.tool_output(f"Excluding: {len(exclude_patterns)} patterns")
        
        # Show focus
        has_focus = hasattr(args, 'focus') and args.focus
        has_focus_args = hasattr(args, 'focus_args') and args.focus_args
        
        if has_focus or has_focus_args:
            focus = []
            if has_focus:
                focus.append(args.focus)
            if has_focus_args:
                if isinstance(args.focus_args, str):
                    focus.append(args.focus_args)
                else:
                    focus.append(str(args.focus_args))
            self.io.tool_output(f"Focus: {' '.join(focus)}")
        
        self.io.tool_output("-------------------")
    
    def _save_current_config(self, args: argparse.Namespace) -> None:
        """Save current command-line arguments as default configuration."""
        # Convert command-line args to config format
        config_updates = {}
        
        if args.exclude:
            config_updates["exclude_patterns"] = args.exclude.split(',')
            
        if args.batch_size and args.batch_size != 10:  # Only if different from default
            config_updates["batch_size"] = args.batch_size
            
        if args.max_token_per_batch:
            config_updates["tokens_per_batch"] = args.max_token_per_batch
            
        if args.output:
            config_updates["output_file"] = args.output
            
        if args.format and args.format != 'md':  # Only if different from default
            config_updates["output_format"] = args.format
        
        # Update the config
        for key, value in config_updates.items():
            self.config_manager.update_config(key, value)
            
        self.io.tool_output("Configuration saved as defaults.")
    
    def _get_model_token_limit(self) -> int:
        """Get the model's token limit."""
        model_token_limit = self.coder.main_model.info.get('max_input_tokens', 0)
        if model_token_limit <= 0:
            # If we can't determine the model's limit, use a conservative default
            model_token_limit = 4096
        return model_token_limit
    
    def _calculate_token_limit(self, model_token_limit: int, max_token_per_batch: int = None) -> int:
        """Calculate the safe token limit per batch."""
        token_reserve = self.config_manager.get_token_limits()["reserve"]
        
        # Reserve tokens for the prompt and overhead
        reserved_tokens = token_reserve + 2000  # Additional overhead
        
        # Calculate safe token limit (70% of available tokens after reserving for prompt)
        safe_token_limit = int((model_token_limit - reserved_tokens) * 0.7)
        
        # Use the specified max_token_per_batch or calculate based on model
        max_token_per_batch = max_token_per_batch or safe_token_limit
        
        # Ensure max_token_per_batch is reasonable
        max_token_per_batch = min(max_token_per_batch, safe_token_limit)
        max_token_per_batch = max(max_token_per_batch, 1000)  # Ensure minimum reasonable size
        
        return max_token_per_batch
    
    def _get_files_to_review(self, args: argparse.Namespace) -> List[Tuple[str, str]]:
        """Get the list of files to review."""
        # If smart mode is enabled, use the smart analyzer
        if args.smart:
            if self.coder.repo:
                # If we have a Git repository, use that for tracking files
                tracked_files = self.smart_analyzer.find_git_tracked_files()
                if tracked_files:
                    # Convert to absolute paths
                    tracked_files = [(f, str(Path(self.coder.abs_root_path(f)))) for f in tracked_files]
                    
                    # Apply include/exclude patterns if provided
                    if args.include or args.exclude:
                        include_patterns = args.include.split(',') if args.include else None
                        exclude_patterns = args.exclude.split(',') if args.exclude else []
                        
                        # Add default exclusions from config if using code-only
                        if args.code_only and not exclude_patterns:
                            exclude_patterns = self.config_manager.get_exclude_patterns()
                        
                        filtered_files = []
                        for rel_path, abs_path in tracked_files:
                            # Apply include/exclude patterns
                            if exclude_patterns and any(fnmatch(rel_path, pat) for pat in exclude_patterns):
                                continue
                                
                            if include_patterns and not any(fnmatch(rel_path, pat) for pat in include_patterns):
                                continue
                                
                            filtered_files.append((rel_path, abs_path))
                        
                        tracked_files = filtered_files
                    
                    # Filter by extensions from config if using code-only
                    if args.code_only:
                        include_extensions = self.config_manager.get_include_extensions()
                        tracked_files = [(rel_path, abs_path) for rel_path, abs_path in tracked_files 
                                        if any(rel_path.lower().endswith(ext) for ext in include_extensions)]
                    
                    return tracked_files
            
            # If no Git repo or no tracked files, scan workspace for source files
            return self.smart_analyzer.find_source_files()
        else:
            # If smart mode is disabled, use the original method
            nl_query = ""
            if hasattr(args, 'focus_args') and args.focus_args:
                nl_query = args.focus_args
            if hasattr(args, 'focus') and args.focus:
                if nl_query:
                    nl_query = f"{args.focus} {nl_query}"
                else:
                    nl_query = args.focus
            
            # If no files are in chat, add relevant code files from repository
            if not self.coder.abs_fnames and not self.coder.abs_read_only_fnames:
                if not self.coder.repo:
                    self.io.tool_output("No repository found and no files in chat")
                    return []
                
                files = self.coder.repo.get_tracked_files()
                if not files:
                    self.io.tool_output("No tracked files found in repository")
                    return []
                
                # Filter files based on extensions and patterns
                filtered_files = self._legacy_filter_files(files, args)
                raw_files = [(f, str(Path(self.coder.abs_root_path(f)))) for f in filtered_files]
                
                # Apply natural language filtering if a query exists
                if nl_query.strip():
                    nl_filtered_files = self.file_analyzer.filter_files_by_natural_language(raw_files, nl_query)
                    if nl_filtered_files:  # Only use filtered files if we got some back
                        return nl_filtered_files
                    return raw_files  # Fall back to all files if filtering returned none
                
                return raw_files
            else:
                # Use files that are already in the chat
                raw_files = []
                for fname in self.coder.abs_read_only_fnames:
                    rel_fname = self.coder.get_rel_fname(fname)
                    raw_files.append((rel_fname, fname))
                
                # Apply natural language filtering if a query exists
                if nl_query.strip():
                    nl_filtered_files = self.file_analyzer.filter_files_by_natural_language(raw_files, nl_query)
                    if nl_filtered_files:  # Only use filtered files if we got some back
                        return nl_filtered_files
                    return raw_files  # Fall back to all files if filtering returned none
                
                return raw_files
    
    def _legacy_filter_files(self, files: List[str], args: argparse.Namespace) -> List[str]:
        """Legacy filter files based on command arguments."""
        # Common code file extensions
        code_extensions = set(self.config_manager.get_include_extensions())
        
        # Process include/exclude patterns
        include_patterns = args.include.split(',') if args.include else None
        exclude_patterns = args.exclude.split(',') if args.exclude else []
        
        # Add config file patterns to exclude if --code-only is specified
        if args.code_only:
            if not exclude_patterns:
                exclude_patterns = self.config_manager.get_exclude_patterns()
            else:
                exclude_patterns.extend(self.config_manager.get_exclude_patterns())
        
        filtered_files = []
        
        for file in files:
            # Skip if not a code file
            if args.code_only and not any(file.lower().endswith(ext) for ext in code_extensions):
                continue
            
            # Apply include/exclude patterns
            if exclude_patterns and any(fnmatch(file, pat) for pat in exclude_patterns):
                continue
                
            if include_patterns and not any(fnmatch(file, pat) for pat in include_patterns):
                continue
            
            filtered_files.append(file)
            
            # Check max files limit
            if args.max_files and len(filtered_files) >= args.max_files:
                break
        
        return filtered_files
    
    def _process_in_batches(
        self,
        large_files: List[Tuple[str, str]],
        normal_files: List[Tuple[str, str]],
        args: argparse.Namespace,
        max_token_per_batch: int
    ) -> None:
        """Process files in optimized batches."""
        # Total files to review
        total_files = len(large_files) + len(normal_files)
        
        # Analyze file dependencies and get batch related info
        file_tokens, file_imports, file_imported_by, directory_groups, file_types = \
            self.file_analyzer.analyze_dependencies(normal_files)
        
        # Create optimized batches
        batches = self.batch_processor.create_batches(
            large_files, normal_files, file_tokens, file_imports, file_imported_by,
            directory_groups, file_types, max_token_per_batch, args.batch_size
        )
        
        if not batches:
            self.io.tool_error("Failed to create batches for review.")
            return
        
        # Create metadata for the review
        metadata = self._create_metadata(args, total_files, len(batches))
        
        # Initialize report
        output_path = args.output or self.config_manager.get_output_settings()["file"]
        output_path = Path(self.workspace_root) / output_path
        
        self.report_generator.generate_report(
            output_path=output_path,
            format=args.format or self.config_manager.get_output_settings()["format"],
            review_content="",
            metadata=metadata
        )
        
        # Check for previous TODOs if tracking is enabled
        previous_todos_with_status = []
        if hasattr(args, 'track_todos') and args.track_todos:
            # Get previous TODOs
            todo_file_path = None
            if args.todo_file:
                todo_file_path = Path(self.workspace_root) / args.todo_file
            else:
                # Try to find the most recent TODO file
                default_path = Path(self.workspace_root) / "TODO.md"
                if default_path.exists():
                    todo_file_path = default_path
            
            if todo_file_path:
                # Use the legacy method to parse previous TODOs
                from .command import ReviewCommand
                review_cmd = ReviewCommand(self.io, self.coder)
                previous_todos = review_cmd._parse_previous_todos(todo_file_path)
                
                if previous_todos:
                    # Get content of files to be reviewed for status checking
                    files_to_review = large_files + normal_files
                    files_content = {}
                    for rel_path, abs_path in files_to_review:
                        try:
                            with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                                files_content[rel_path] = f.read()
                        except Exception:
                            pass
                    
                    # Check status of previous TODOs
                    for todo in previous_todos:
                        is_resolved, comment = review_cmd._check_todo_resolution(todo, files_content)
                        todo['resolved'] = is_resolved
                        todo['resolution_comment'] = comment
                        previous_todos_with_status.append(todo)
        
        # Process batches
        all_review_content = ""
        for batch_idx, batch in enumerate(batches, 1):
            self.io.tool_output(f"\nProcessing batch {batch_idx} of {len(batches)}...")
            
            # Get batch description
            batch_description = self._get_batch_description(batch)
            
            # Create batch info
            batch_info = {
                'batch_idx': batch_idx,
                'total_batches': len(batches),
                'description': batch_description,
                'files': [rel_path for rel_path, _, _ in batch]
            }
            
            # Log batch to context
            self.context.add_batch(batch_info)
            
            # Disable file mention prompting during review
            original_check_for_file_mentions = self.coder.check_for_file_mentions
            self.coder.check_for_file_mentions = lambda content: None
            
            try:
                # Review this batch
                review_content = self._review_batch(
                    batch, args, batch_idx, len(batches), 
                    previous_todos_with_status if hasattr(args, 'track_todos') and args.track_todos else None
                )
                
                # Check if we actually got content back
                if not review_content or not isinstance(review_content, str):
                    self.io.tool_error(f"Failed to generate review content for batch {batch_idx}.")
                    continue
                
                # Accumulate review content for potential Kanban export
                all_review_content += review_content + "\n\n"
                
                # Generate or update the report
                self.report_generator.generate_report(
                    output_path=output_path,
                    format=args.format or self.config_manager.get_output_settings()["format"],
                    review_content=review_content,
                    batch_info=batch_info
                )
                
                # Mark files as reviewed
                self.context.update_files_reviewed([rel_path for rel_path, _, _ in batch])
                
                # Parse and store TODOs in context
                self._parse_and_store_todos(review_content, batch_info)
            finally:
                # Restore original file mention function
                self.coder.check_for_file_mentions = original_check_for_file_mentions
            
            # Check if user wants to continue
            if not args.auto and batch_idx < len(batches):
                if not self.io.confirm_ask(f"Continue with batch {batch_idx+1}?", True):
                    self.io.tool_output("Review paused. You can continue later with: @review --continue")
                    break
        
        # Export TODOs to Kanban board if requested (after all batches are processed)
        if args.export_kanban and self.kanban_available and all_review_content:
            self._export_to_kanban(all_review_content, args)
    
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
        
        # Get batch description
        batch_description = self._get_batch_description(batch_with_tokens)
        
        # Initialize the report
        output_path = args.output or self.config_manager.get_output_settings()["file"]
        output_path = Path(self.workspace_root) / output_path
        
        self.report_generator.generate_report(
            output_path=output_path,
            format=args.format or self.config_manager.get_output_settings()["format"],
            review_content="",
            metadata=metadata
        )
        
        # Check for previous TODOs if tracking is enabled
        previous_todos_with_status = None
        if hasattr(args, 'track_todos') and args.track_todos:
            # Similar logic as in _process_in_batches, but abbreviated for brevity
            todo_file_path = None
            if args.todo_file:
                todo_file_path = Path(self.workspace_root) / args.todo_file
            else:
                default_path = Path(self.workspace_root) / "TODO.md"
                if default_path.exists():
                    todo_file_path = default_path
            
            if todo_file_path:
                from .command import ReviewCommand
                review_cmd = ReviewCommand(self.io, self.coder)
                previous_todos = review_cmd._parse_previous_todos(todo_file_path)
                
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
                        is_resolved, comment = review_cmd._check_todo_resolution(todo, files_content)
                        todo['resolved'] = is_resolved
                        todo['resolution_comment'] = comment
                        previous_todos_with_status.append(todo)
        
        # Create batch info
        batch_info = {
            'batch_idx': 1,
            'total_batches': 1,
            'description': batch_description,
            'files': [rel_path for rel_path, _, _ in batch_with_tokens]
        }
        
        # Log batch to context
        self.context.add_batch(batch_info)
        
        # Disable file mention prompting during review
        original_check_for_file_mentions = self.coder.check_for_file_mentions
        self.coder.check_for_file_mentions = lambda content: None
        
        try:
            # Review this batch
            review_content = self._review_batch(batch_with_tokens, args, 1, 1, previous_todos_with_status)
            
            # Check if we actually got content back
            if not review_content or not isinstance(review_content, str):
                self.io.tool_error("Failed to generate review content.")
                return
            
            # Generate the final report
            self.report_generator.generate_report(
                output_path=output_path,
                format=args.format or self.config_manager.get_output_settings()["format"],
                review_content=review_content,
                metadata=metadata
            )
            
            # Mark files as reviewed
            self.context.update_files_reviewed([rel_path for rel_path, _, _ in batch_with_tokens])
            
            # Parse and store TODOs in context
            self._parse_and_store_todos(review_content, batch_info)
            
            # Export TODOs to Kanban board if requested
            if args.export_kanban and self.kanban_available:
                self._export_to_kanban(review_content, args)
        finally:
            # Restore original file mention function
            self.coder.check_for_file_mentions = original_check_for_file_mentions
    
    def _create_metadata(self, args: argparse.Namespace, total_files: int, total_batches: int) -> dict:
        """Create metadata for the review report."""
        metadata = {
            'Workspace': self.workspace_root,
            'Date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Files reviewed': total_files,
            'Batches': total_batches,
        }
        
        # Add focus information if available
        focus = []
        if hasattr(args, 'focus') and args.focus:
            focus.append(args.focus)
        if hasattr(args, 'focus_args') and args.focus_args:
            focus.append(args.focus_args)
        
        if focus:
            metadata['Focus'] = ' '.join(focus)
        
        # Add smart mode info
        metadata['Smart prioritization'] = 'Enabled' if args.smart else 'Disabled'
        
        return metadata
    
    def _get_batch_description(self, batch: List[Tuple[str, str, int]]) -> str:
        """Get a descriptive summary of the batch contents."""
        if not batch:
            return "Empty batch"
        
        # Count file types in this batch
        file_types = defaultdict(int)
        for rel_path, _, _ in batch:
            _, ext = os.path.splitext(rel_path.lower())
            if ext:
                file_types[ext] += 1
        
        # Get most common directories
        directories = defaultdict(int)
        for rel_path, _, _ in batch:
            directory = os.path.dirname(rel_path)
            if directory:
                directories[directory] += 1
        
        top_dirs = sorted(directories.items(), key=lambda x: x[1], reverse=True)[:2]
        
        # Create description
        description = ""
        if top_dirs:
            top_dir_names = [d for d, _ in top_dirs]
            description += f"Files from {', '.join(top_dir_names)}"
        else:
            description += "Files from root directory"
        
        if file_types:
            top_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:3]
            type_desc = ", ".join(f"{count} {ext}" for ext, count in top_types)
            description += f" ({type_desc})"
        
        return description
    
    def _review_batch(
        self,
        batch: List[Tuple[str, str, int]],
        args: argparse.Namespace,
        batch_idx: int,
        total_batches: int,
        previous_todos: List[dict] = None
    ) -> str:
        """Review a batch of files and return the review content."""
        # Prepare coder state for review
        self._prepare_coder_for_review(batch)
        
        # Create review prompt
        prompt = self._create_review_prompt(args, batch_idx, total_batches, previous_todos)
        
        # Disable file mention prompting during review
        original_check_for_file_mentions = self.coder.check_for_file_mentions
        self.coder.check_for_file_mentions = lambda content: None
        
        try:
            # Run the review
            if args.auto:
                original_confirm_ask = self.io.confirm_ask
                self.io.confirm_ask = lambda q, d=None: True
                try:
                    self.io.tool_output(f"Running automated review for batch {batch_idx}...")
                    self.coder.run(prompt)
                finally:
                    self.io.confirm_ask = original_confirm_ask
            else:
                self.io.tool_output(f"Starting review for batch {batch_idx} (press Enter to continue)...")
                self.coder.run(prompt)
            
            # Get the review content from the model response
            messages = self.coder.done_messages + self.coder.cur_messages
            assistant_messages = [msg for msg in reversed(messages) if msg["role"] == "assistant"]
            
            if not assistant_messages:
                self.io.tool_error("No review response generated by the model")
                return ""
                
            content = assistant_messages[0].get("content", "")
            if not content or not isinstance(content, str):
                self.io.tool_error("Invalid content returned from the model")
                return ""
                
            return content
        except Exception as e:
            self.io.tool_error(f"Error during review: {str(e)}")
            return ""
        finally:
            # Restore original file mention function
            self.coder.check_for_file_mentions = original_check_for_file_mentions
    
    def _prepare_coder_for_review(self, batch: List[Tuple[str, str, int]]) -> None:
        """Prepare the coder for review by adding files to be reviewed."""
        # Save original coder state
        original_read_only = self.coder.abs_read_only_fnames.copy()
        
        # Clear previous state
        self.coder.abs_read_only_fnames.clear()
        
        # Add files to review
        for _, abs_path, _ in batch:
            self.coder.abs_read_only_fnames.add(abs_path)
    
    def _create_review_prompt(self, args: argparse.Namespace, batch_idx: int, total_batches: int, previous_todos=None) -> str:
        """Create a review prompt for the batch."""
        base_prompt = """Please review the following code files focusing on:

- Code quality and best practices
- Potential bugs or issues
- Security implications
- Performance considerations
- Documentation needs
- Test coverage

Format each issue as an actionable TODO item:
- [ ] **Issue**: [Brief description]
      **Location**: [File path and line numbers]
      **Priority**: [High/Medium/Low]
      **Details**: [Detailed explanation and how to fix]
      **Category**: [Code Quality/Security/Performance/etc.]
      **Effort**: [Small/Medium/Large]

"""
        # Add previous TODO status if tracked
        if previous_todos:
            base_prompt += "## Previous TODOs Status\n\nThe following issues were identified in previous reviews. Please verify if they've been resolved properly:\n\n"
            
            for todo in previous_todos:
                status_marker = "x" if todo['resolved'] else " "
                base_prompt += f"- [{status_marker}] **Previous Issue**: {todo['issue']}\n"
                if todo.get('location'):
                    base_prompt += f"      **Location**: {todo['location']}\n"
                base_prompt += f"      **Status**: {todo.get('resolution_comment', 'Unknown')}\n"
                base_prompt += f"      **Original Priority**: {todo.get('priority', 'Unknown')}\n\n"
                
            base_prompt += """Please carefully verify all previous TODOs listed above:
1. For TODOs that are actually resolved, keep them marked with [x]
2. For TODOs that are still present, update them in your review with current details
3. IMPORTANT: Do not duplicate issues - each finding should appear exactly once in your review
4. Include any new issues you find that weren't in the previous TODO list

Your final report should include a consolidated list where:
- Previously resolved TODOs show with [x]
- Still-present TODOs keep their original status (resolved or not)
- New TODOs are added with [ ]
"""

        # Add specific focus areas if specified
        focus_areas = []
        if hasattr(args, 'focus') and args.focus:
            focus_areas.extend(args.focus.split(','))
        if hasattr(args, 'focus_args') and args.focus_args:
            if isinstance(args.focus_args, str):
                focus_areas.append(args.focus_args)
            else:
                # Handle case where focus_args is not a string
                focus_areas.append(str(args.focus_args))
        
        if focus_areas:
            base_prompt += f"\nPlease pay special attention to: {', '.join(focus_areas)}"

        # Add batch information
        if total_batches > 1:
            base_prompt += f"\n\nThis is batch {batch_idx} of {total_batches}."
        
        return base_prompt
    
    def _parse_and_store_todos(self, review_content: str, batch_info: Dict[str, Any]) -> None:
        """Parse TODOs from review content and store them in context."""
        import re
        
        # Parse TODOs
        todo_pattern = r'- \[([ xX])\] \*\*Issue\*\*: (.*?)(?:\n\s+\*\*Location\*\*: (.*?))?(?:\n\s+\*\*Priority\*\*: (.*?))?(?:\n\s+\*\*Details\*\*: (.*?))?(?:\n\s+\*\*Category\*\*: (.*?))?(?:\n\s+\*\*Effort\*\*: (.*?))?(?:\n\s+\*\*Dependencies\*\*: (.*?))?(?=\n- \[|$)'
        
        matches = re.findall(todo_pattern, review_content, re.DOTALL)
        for match in matches:
            status, issue, location, priority, details, category, effort, dependencies = match
            resolved = status.strip().lower() in ['x']
            
            todo_item = {
                'issue': issue.strip(),
                'location': location.strip() if location else '',
                'resolved': resolved,
                'details': details.strip() if details else '',
                'priority': priority.strip() if priority else '',
                'category': category.strip() if category else '',
                'effort': effort.strip() if effort else '',
                'dependencies': dependencies.strip() if dependencies else '',
                'batch': batch_info['batch_idx'],
                'batch_description': batch_info['description'],
                'found_at': datetime.datetime.now().isoformat()
            }
            
            # Add to context
            self.context.add_todo_item(todo_item)
    
    def _show_progress_report(self) -> None:
        """Show a progress report for the review."""
        progress = self.context.get_progress()
        session_info = self.context.get_session_info()
        
        self.io.tool_output("\n=== Review Progress Report ===")
        self.io.tool_output(f"Session ID: {session_info['session_id']}")
        self.io.tool_output(f"Started: {session_info['created']}")
        self.io.tool_output(f"Last updated: {session_info['last_updated']}")
        
        self.io.tool_output(f"\nFiles: {progress['reviewed_files']} of {progress['total_files']} reviewed ({progress['completion_percentage']}%)")
        self.io.tool_output(f"Batches completed: {session_info['batches_count']}")
        
        self.io.tool_output(f"\nIssues found:")
        self.io.tool_output(f"  High priority: {progress['high_priority_issues']}")
        self.io.tool_output(f"  Medium priority: {progress['medium_priority_issues']}")
        self.io.tool_output(f"  Low priority: {progress['low_priority_issues']}")
        self.io.tool_output(f"  Total: {session_info['todo_items_count']}")
        
        if session_info['todo_items_count'] > 0:
            # Show the most recent focus area if available
            recent_focus = self.context.get_recent_focus()
            if recent_focus:
                self.io.tool_output(f"\nMost recent focus: {recent_focus}")
        
        # Provide guidance for continuing
        if progress['completion_percentage'] < 100:
            self.io.tool_output("\nTo continue the review, run: @review --continue")
        else:
            self.io.tool_output("\nReview complete! All files have been reviewed.")
    
    def _continue_review(self, args: argparse.Namespace) -> None:
        """Continue a previous review session."""
        # Get reviewed files
        reviewed_files = self.context.get_reviewed_files()
        
        if not reviewed_files:
            self.io.tool_output("No previous review session found. Starting a new review.")
            # Remove --continue flag and run normally
            args.continue_review = False
            self.execute(" ".join([f"--{k}" for k, v in vars(args).items() if v is True and k != 'continue_review']))
            return
        
        self.io.tool_output(f"Continuing previous review session with {len(reviewed_files)} files already reviewed.")
        
        # Get files to review
        all_files = self._get_files_to_review(args)
        
        # Filter out already reviewed files
        files_to_review = [(rel_path, abs_path) for rel_path, abs_path in all_files 
                           if rel_path not in reviewed_files]
        
        if not files_to_review:
            self.io.tool_output("All files have already been reviewed! Run with --reset to start a new review.")
            return
        
        self.io.tool_output(f"Found {len(files_to_review)} remaining files to review.")
        
        # Continue with normal processing using the remaining files
        # Use the smart analyzer to prioritize files
        prioritized_files = self.smart_analyzer.prioritize_files(files_to_review)
        
        # Apply natural language filtering if a query exists
        nl_query = ""
        if hasattr(args, 'focus_args') and args.focus_args:
            nl_query = args.focus_args
        if hasattr(args, 'focus') and args.focus:
            if nl_query:
                nl_query = args.focus + " " + nl_query
            else:
                nl_query = args.focus
                
        if nl_query.strip():
            prioritized_files = self.smart_analyzer.filter_by_natural_language(prioritized_files, nl_query)
            self.context.set_recent_focus(nl_query.strip())
        
        if not prioritized_files:
            self.io.tool_error("No files matched your criteria after filtering.")
            return
        
        # Remove score from prioritized files for backward compatibility
        files_for_processing = [(rel_path, abs_path) for rel_path, abs_path, _ in prioritized_files]
        
        # Get token limits
        model_token_limit = self._get_model_token_limit()
        max_token_per_batch = args.max_token_per_batch or self.config_manager.get_token_limits()["per_batch"]
        max_token_per_batch = self._calculate_token_limit(model_token_limit, max_token_per_batch)
        
        # Separate large files from normal files
        large_files, normal_files = self.file_analyzer.analyze_files(files_for_processing, max_token_per_batch)
        
        # Process the files in batches
        if args.no_batch or (len(normal_files) + len(large_files) <= args.batch_size):
            # Process all files in a single batch
            self._process_single_batch(files_for_processing, args)
        else:
            # Process files in multiple batches
            self._process_in_batches(large_files, normal_files, args, max_token_per_batch)
        
        # Show progress after this review session
        self._show_progress_report()
    
    def _handle_diff_review(self, args: argparse.Namespace) -> None:
        """Handle diff-based review."""
        # For now, use the legacy implementation from ReviewCommand
        from .command import ReviewCommand
        review_cmd = ReviewCommand(self.io, self.coder)
        review_cmd.execute(" ".join([f"--{k}" for k, v in vars(args).items() if v is True and k != 'smart']))

    def _export_to_kanban(self, review_content: str, args: argparse.Namespace) -> None:
        """Export TODOs to a Kanban board.
        
        Args:
            review_content: The content of the review
            args: Command-line arguments
        """
        if not self.kanban_available:
            self.io.tool_error("Kanban integration is not available. Make sure the required dependencies are installed.")
            return
        
        platform = args.export_kanban
        config = {}
        
        # Load config from file if specified
        if args.kanban_config:
            config_path = Path(self.workspace_root) / args.kanban_config
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                self.io.tool_error(f"Failed to load Kanban configuration: {str(e)}")
                return
        
        # Export TODOs to Kanban board
        board_info = {
            'include_resolved': hasattr(args, 'track_todos') and args.track_todos,  # Include resolved TODOs if tracking is enabled
            'auto_create_database': True  # Automatically create database if it doesn't exist
        }
        
        success = self.export_todos_to_kanban(
            self.io, review_content, platform, config, board_info
        )
        
        if success:
            self.io.tool_output(f"Successfully exported TODOs to {platform.capitalize()} board.")
        else:
            self.io.tool_error(f"Failed to export TODOs to {platform.capitalize()} board.") 