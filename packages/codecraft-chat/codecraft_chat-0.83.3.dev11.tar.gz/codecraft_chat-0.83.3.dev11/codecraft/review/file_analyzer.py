"""
File analysis and grouping logic for code review.
"""

import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, DefaultDict, Optional

class FileAnalyzer:
    def __init__(self, io):
        self.io = io
        self.import_patterns = {
            '.py': [r'import\s+(\w+)', r'from\s+(\w+)'],
            '.js': [r'import.*from\s+[\'"](.+)[\'"]', r'require\([\'"](.+)[\'"]\)'],
            '.jsx': [r'import.*from\s+[\'"](.+)[\'"]'],
            '.ts': [r'import.*from\s+[\'"](.+)[\'"]'],
            '.tsx': [r'import.*from\s+[\'"](.+)[\'"]'],
            '.java': [r'import\s+([\w\.]+)'],
            '.cpp': [r'#include\s+[<"](.+)[>"]'],
            '.c': [r'#include\s+[<"](.+)[>"]'],
        }
        
        # Common code concepts and their related keywords
        self.code_concepts = {
            'authentication': ['auth', 'login', 'password', 'credential', 'token', 'jwt', 'oauth', 'session', 'permission'],
            'database': ['database', 'sql', 'query', 'model', 'schema', 'orm', 'migration', 'db', 'mongo', 'redis'],
            'api': ['api', 'endpoint', 'rest', 'graphql', 'controller', 'route', 'http', 'request', 'response'],
            'security': ['security', 'encrypt', 'hash', 'protect', 'vulnerability', 'injection', 'xss', 'csrf'],
            'test': ['test', 'spec', 'assert', 'mock', 'stub', 'fixture', 'unit', 'integration'],
            'ui': ['component', 'view', 'render', 'template', 'style', 'css', 'html', 'dom', 'interface'],
            'config': ['config', 'setting', 'environment', 'env', 'option', 'parameter', 'preference'],
            'validation': ['validate', 'sanitize', 'check', 'input', 'form', 'schema', 'constraint'],
            'error': ['error', 'exception', 'handle', 'catch', 'try', 'throw', 'log', 'debug'],
            'performance': ['performance', 'optimize', 'cache', 'speed', 'memory', 'leak', 'bottleneck'],
        }

    def analyze_files(self, files: List[Tuple[str, str]], max_token_per_batch: int) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """Analyze files and separate into large and normal files."""
        large_files = []
        normal_files = []

        self.io.tool_output("\nAnalyzing files for smart grouping...")
        for rel_path, abs_path in files:
            try:
                file_size = os.path.getsize(abs_path)
                if file_size > 500000:  # Files over 500KB go into their own batches
                    large_files.append((rel_path, abs_path))
                else:
                    normal_files.append((rel_path, abs_path))
            except Exception:
                normal_files.append((rel_path, abs_path))

        if large_files:
            self.io.tool_output(f"Found {len(large_files)} large files that will be processed individually:")
            for rel_path, _ in large_files:
                self.io.tool_output(f"  - {rel_path}")

        return large_files, normal_files
    
    def filter_files_by_natural_language(self, files: List[Tuple[str, str]], nl_query: str) -> List[Tuple[str, str]]:
        """Filter files based on a natural language query.
        
        Args:
            files: List of (relative_path, absolute_path) tuples
            nl_query: Natural language query to filter by
            
        Returns:
            Filtered list of files that match the query
        """
        if not nl_query or not files:
            return files
            
        self.io.tool_output(f"Filtering files based on query: '{nl_query}'...")
        
        # Special handling for "entire codebase" queries
        if "entire" in nl_query.lower() and "codebase" in nl_query.lower():
            self.io.tool_output("Detected 'entire codebase' review request - not filtering by natural language")
            return files
        
        # Extract key concepts from the query
        concepts = self._extract_concepts_from_query(nl_query)
        if not concepts:
            self.io.tool_warning("No specific filtering concepts detected in query, using all files")
            return files
            
        self.io.tool_output(f"Filtering for concepts: {', '.join(concepts)}")
        
        # Read and analyze files
        filtered_files = []
        skipped_files = []
        
        for rel_path, abs_path in files:
            try:
                # Check if file exists and is readable
                if not os.path.isfile(abs_path):
                    self.io.tool_warning(f"File not found or not readable: {rel_path}")
                    # Include the file anyway to avoid unexpected exclusions
                    filtered_files.append((rel_path, abs_path))
                    continue
                    
                # Read file content
                try:
                    with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                except Exception as e:
                    self.io.tool_warning(f"Error reading {rel_path}: {e}")
                    # Include files that couldn't be read to be safe
                    filtered_files.append((rel_path, abs_path))
                    continue
                
                # Check if the file matches any of our target concepts
                matches_concept, matched_concepts = self._file_matches_concepts(rel_path, content, concepts)
                
                if matches_concept:
                    filtered_files.append((rel_path, abs_path))
                    self.io.tool_output(f"  + Including: {rel_path} (matched {', '.join(matched_concepts)})")
                else:
                    skipped_files.append(rel_path)
            except Exception as e:
                self.io.tool_warning(f"Error analyzing {rel_path}: {e}")
                # Include files that couldn't be analyzed to be safe
                filtered_files.append((rel_path, abs_path))
        
        if skipped_files:
            self.io.tool_output(f"Excluded {len(skipped_files)} files not matching the query")
            # If too many files were excluded, show a sample
            if len(skipped_files) > 5:
                self.io.tool_output(f"Sample excluded: {', '.join(skipped_files[:5])}")
        
        if not filtered_files:
            self.io.tool_warning("No files matched your query criteria. Using all files instead.")
            return files  # Return original files if no matches were found
        
        # If very few files were matched, show a warning
        if len(filtered_files) < 3 and len(files) > 10:
            self.io.tool_warning(f"Only {len(filtered_files)} files matched your query out of {len(files)} total")
            self.io.tool_output("Consider using a more general query if this is too restrictive")
            
        return filtered_files

    def _extract_concepts_from_query(self, query: str) -> List[str]:
        """Extract key coding concepts from a natural language query."""
        query_lower = query.lower()
        
        # Direct concept matches
        matched_concepts = []
        for concept, keywords in self.code_concepts.items():
            # Check if the concept itself is mentioned
            if concept in query_lower:
                matched_concepts.append(concept)
                continue
                
            # Check for keyword matches
            for keyword in keywords:
                # Use word boundary to avoid partial matches
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                    matched_concepts.append(concept)
                    break
        
        # Check for special file types mentioned
        file_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.rs', '.go']
        for ext in file_extensions:
            if ext in query_lower:
                matched_concepts.append(f"files:{ext}")
        
        # Check for directory mentions
        dir_patterns = [r'(in|from|under|within)\s+([a-zA-Z0-9_/.-]+)\s+(dir|directory|folder)', 
                       r'([a-zA-Z0-9_/.-]+)\s+(dir|directory|folder)']
        
        for pattern in dir_patterns:
            matches = re.search(pattern, query_lower)
            if matches:
                dir_name = matches.group(2) if len(matches.groups()) > 1 else matches.group(1)
                matched_concepts.append(f"dir:{dir_name}")
        
        return matched_concepts
    
    def _file_matches_concepts(self, file_path: str, content: str, concepts: List[str]) -> Tuple[bool, List[str]]:
        """Check if a file matches the specified concepts.
        
        Returns:
            Tuple of (matches_any_concept, list_of_matched_concepts)
        """
        file_lower = file_path.lower()
        content_lower = content.lower()
        matched = []
        
        for concept in concepts:
            # Handle special file extension filter
            if concept.startswith("files:"):
                ext = concept[6:]
                if file_lower.endswith(ext):
                    matched.append(f"file type: {ext}")
                    continue
            
            # Handle directory filter
            elif concept.startswith("dir:"):
                dir_pattern = concept[4:]
                path_parts = Path(file_path).parts
                if any(dir_pattern in part.lower() for part in path_parts):
                    matched.append(f"directory: {dir_pattern}")
                    continue
                    
            # Handle regular concept keywords
            elif concept in self.code_concepts:
                # Check the filename first
                filename_matched = any(keyword in file_lower for keyword in self.code_concepts[concept])
                
                # Then check content with more detailed pattern matching
                content_matched = False
                for keyword in self.code_concepts[concept]:
                    # Use word boundaries for more accurate matching
                    if re.search(r'\b' + re.escape(keyword) + r'\b', content_lower):
                        content_matched = True
                        break
                
                if filename_matched or content_matched:
                    matched.append(concept)
        
        return len(matched) > 0, matched

    def analyze_dependencies(self, normal_files: List[Tuple[str, str]]) -> Tuple[Dict[str, int], DefaultDict[str, Set[str]], DefaultDict[str, Set[str]], DefaultDict[str, List], DefaultDict[str, List]]:
        """Analyze file dependencies and group files by directory and type."""
        directory_groups = defaultdict(list)
        file_types = defaultdict(list)
        file_imports = defaultdict(set)
        file_imported_by = defaultdict(set)
        file_tokens = {}

        for rel_path, abs_path in normal_files:
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    token_estimate = self._estimate_file_tokens(content, rel_path)
                    file_tokens[rel_path] = token_estimate

                    # Group by directory and file type
                    dir_group = self._get_directory_depth(rel_path)
                    directory_groups[dir_group].append((rel_path, abs_path, token_estimate))
                    file_ext = self._get_file_extension(rel_path)
                    file_types[file_ext].append((rel_path, abs_path, token_estimate))

                    # Analyze dependencies
                    self._analyze_file_dependencies(rel_path, content, file_imports, file_imported_by, normal_files)

            except Exception as e:
                self.io.tool_warning(f"Error analyzing {rel_path}: {e}")
                file_tokens[rel_path] = 1000  # default estimate
                dir_group = self._get_directory_depth(rel_path)
                directory_groups[dir_group].append((rel_path, abs_path, 1000))
                file_ext = self._get_file_extension(rel_path)
                file_types[file_ext].append((rel_path, abs_path, 1000))

        return file_tokens, file_imports, file_imported_by, directory_groups, file_types

    def _estimate_file_tokens(self, content: str, file_path: str) -> int:
        """Estimate token count for a file based on its content and type."""
        line_count = content.count('\n') + 1
        char_count = len(content)
        file_ext = self._get_file_extension(file_path)

        # Determine token factor based on file type
        token_factors = {
            '.py': 0.25,
            '.rb': 0.25,
            '.sh': 0.25,
            '.js': 0.3,
            '.ts': 0.3,
            '.jsx': 0.3,
            '.tsx': 0.3,
            '.java': 0.3,
            '.cs': 0.3,
            '.c': 0.33,
            '.cpp': 0.33,
            '.h': 0.33,
            '.hpp': 0.33,
            '.go': 0.33,
            '.rs': 0.33,
            '.json': 0.35,
            '.xml': 0.35,
            '.yaml': 0.35,
            '.yml': 0.35,
            '.md': 0.2,
            '.txt': 0.2,
            '.rst': 0.2,
        }

        token_factor = token_factors.get(file_ext, 0.3)
        return max(int(char_count * token_factor), line_count)

    def _analyze_file_dependencies(self, rel_path: str, content: str, file_imports: DefaultDict[str, Set[str]], 
                                 file_imported_by: DefaultDict[str, Set[str]], normal_files: List[Tuple[str, str]]):
        """Analyze imports and dependencies in a file."""
        file_ext = self._get_file_extension(rel_path)
        if file_ext in self.import_patterns:
            for pattern in self.import_patterns[file_ext]:
                import_matches = re.findall(pattern, content)
                for imp in import_matches:
                    # Normalize the import name
                    imp = imp.split('/')[-1].split('.')[0]
                    file_imports[rel_path].add(imp)

                    # Find potential files that match this import
                    for other_rel, other_abs in normal_files:
                        other_name = os.path.basename(other_rel).split('.')[0]
                        if other_name == imp:
                            file_imported_by[other_rel].add(rel_path)

    @staticmethod
    def _get_file_extension(path: str) -> str:
        """Get the lowercase file extension from a path."""
        _, ext = os.path.splitext(path)
        return ext.lower()

    @staticmethod
    def _get_directory_depth(path: str, max_depth: int = 3) -> str:
        """Get the directory path up to a maximum depth."""
        parts = os.path.dirname(path).split(os.sep)
        return '/'.join(parts[:max_depth]) if parts else '' 