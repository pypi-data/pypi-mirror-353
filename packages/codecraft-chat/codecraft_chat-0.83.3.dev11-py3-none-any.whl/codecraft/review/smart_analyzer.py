"""
Smart file analysis for code review.
"""

import os
import re
import fnmatch
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, DefaultDict, Optional, Any

class SmartAnalyzer:
    """Smart file analysis for code review that prioritizes important files."""
    
    def __init__(self, workspace_root: str, io=None, config_manager=None):
        self.workspace_root = workspace_root
        self.io = io
        self.config_manager = config_manager
        
        # Core file patterns (likely to be important in most projects)
        self.core_file_patterns = [
            # Main/entry point files
            "**/main.{py,js,ts,java,cpp,c,go,rs}",
            "**/index.{js,ts,jsx,tsx}",
            "**/app.{py,js,ts,jsx,tsx,java}",
            "**/server.{js,ts,py,go,rs}",
            
            # Config files
            "**/settings.{py,js,ts,json,yml,yaml,xml}",
            "**/config.{py,js,ts,json,yml,yaml,xml}",
            
            # Project-specific patterns (automatically detected)
            # Will be populated during analysis
        ]
        
        # File importance scoring weights
        self.importance_weights = {
            "is_modified_recently": 10,
            "is_core_file": 8,
            "has_many_imports": 5,
            "is_imported_by_many": 7,
            "has_security_keywords": 9,
            "code_to_comment_ratio": 3,
            "file_size": 2,
            "test_file": -2,  # Lower priority for test files
        }
    
    def find_source_files(self) -> List[Tuple[str, str]]:
        """Find source code files in the workspace, excluding build artifacts.
        
        Returns:
            List of (relative_path, absolute_path) tuples
        """
        source_files = []
        
        if self.io:
            self.io.tool_output("Scanning workspace for source files...")
        
        # Get exclude patterns from config
        exclude_patterns = self.config_manager.get_exclude_patterns() if self.config_manager else [
            "**/node_modules/**", "**/build/**", "**/dist/**", "**/__pycache__/**", 
            "**/.git/**", "**/venv/**", "**/env/**", "**/.venv/**"
        ]
        
        # Get include extensions from config
        include_extensions = self.config_manager.get_include_extensions() if self.config_manager else [
            ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", ".go",
            ".rs", ".php", ".rb", ".cs", ".swift", ".kt", ".scala", ".html", ".css"
        ]
        
        # Maximum file size
        max_file_size = self.config_manager.get_max_file_size() if self.config_manager else 1000000  # 1MB default
        
        # Walk the directory tree
        for root, dirs, files in os.walk(self.workspace_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(os.path.join(root, d), pat) for pat in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.workspace_root)
                
                # Skip excluded files
                if any(fnmatch.fnmatch(rel_path, pat) for pat in exclude_patterns):
                    continue
                
                # Check file extension
                if not any(file.lower().endswith(ext) for ext in include_extensions):
                    continue
                
                # Check file size
                try:
                    if os.path.getsize(file_path) > max_file_size:
                        if self.io:
                            self.io.tool_output(f"Skipping large file: {rel_path}")
                        continue
                except Exception:
                    # If we can't determine file size, still include it
                    pass
                
                source_files.append((rel_path, file_path))
        
        if self.io:
            self.io.tool_output(f"Found {len(source_files)} source files")
        
        return source_files
    
    def find_git_tracked_files(self) -> List[str]:
        """Find all Git-tracked files in the workspace.
        
        Returns:
            List of relative paths to tracked files
        """
        try:
            # Check if Git is available and the directory is a Git repository
            result = subprocess.run(
                ["git", "-C", self.workspace_root, "rev-parse", "--is-inside-work-tree"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if result.returncode != 0:
                if self.io:
                    self.io.tool_warning("Not a Git repository or Git not available")
                return []
            
            # Get all tracked files
            result = subprocess.run(
                ["git", "-C", self.workspace_root, "ls-files"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if result.returncode != 0:
                if self.io:
                    self.io.tool_warning("Failed to get Git tracked files")
                return []
            
            tracked_files = result.stdout.strip().split('\n')
            return [f for f in tracked_files if f.strip()]
            
        except Exception as e:
            if self.io:
                self.io.tool_warning(f"Error getting Git tracked files: {e}")
            return []
    
    def get_recently_modified_files(self, days: int = 7) -> List[str]:
        """Get files modified in the last N days using Git.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of relative paths to recently modified files
        """
        try:
            # Format date for Git
            date = f"{days}.days.ago"
            
            # Get files modified since the date
            result = subprocess.run(
                ["git", "-C", self.workspace_root, "log", "--name-only", "--pretty=format:", f"--since={date}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if result.returncode != 0:
                return []
            
            # Get unique file paths
            modified_files = set()
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    modified_files.add(line.strip())
            
            return list(modified_files)
            
        except Exception:
            return []
    
    def analyze_project_structure(self, files: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Analyze project structure to identify patterns and important files.
        
        Args:
            files: List of (relative_path, absolute_path) tuples
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "framework_detected": None,
            "language_stats": defaultdict(int),
            "directory_structure": defaultdict(int),
            "important_files": [],
            "entry_points": [],
            "core_components": [],
        }
        
        # Detect languages and frameworks
        framework_patterns = {
            "react": ["**/package.json", "**/react", "**/jsx"],
            "angular": ["**/angular.json", "**/app.module.ts"],
            "vue": ["**/vue.config.js", "**/*.vue"],
            "django": ["**/manage.py", "**/settings.py", "**/wsgi.py"],
            "flask": ["**/app.py", "**/flask", "**/__init__.py"],
            "spring": ["**/pom.xml", "**/application.properties", "**/SpringApplication"],
            "express": ["**/express", "**/app.js", "**/server.js"],
            "rails": ["**/Gemfile", "**/config/routes.rb"],
            "laravel": ["**/artisan", "**/composer.json"],
            "dotnet": ["**/*.csproj", "**/Program.cs", "**/Startup.cs"],
        }
        
        # Count file extensions and check for framework patterns
        framework_matches = defaultdict(int)
        directories = set()
        
        for rel_path, abs_path in files:
            # Get file extension
            _, ext = os.path.splitext(rel_path.lower())
            if ext:
                analysis["language_stats"][ext] += 1
            
            # Get directory
            directory = os.path.dirname(rel_path)
            if directory:
                directories.add(directory)
                analysis["directory_structure"][directory] += 1
            
            # Check for framework patterns
            for framework, patterns in framework_patterns.items():
                if any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns):
                    framework_matches[framework] += 1
        
        # Determine the most likely framework
        if framework_matches:
            analysis["framework_detected"] = max(framework_matches.items(), key=lambda x: x[1])[0]
        
        # Find entry points and core components based on naming conventions and patterns
        entry_point_patterns = [
            "**/main.{py,js,ts,java,cpp,c,go,rs}",
            "**/index.{js,ts,jsx,tsx}",
            "**/app.{py,js,ts,jsx,tsx,java}",
            "**/server.{js,ts,py,go,rs}",
            "**/Program.cs",
            "**/Application.java",
        ]
        
        for rel_path, abs_path in files:
            # Check for entry points
            if any(fnmatch.fnmatch(rel_path, pattern) for pattern in entry_point_patterns):
                analysis["entry_points"].append(rel_path)
                analysis["important_files"].append(rel_path)
            
            # Check for core components
            if "core" in rel_path.lower() or "main" in rel_path.lower():
                analysis["core_components"].append(rel_path)
                analysis["important_files"].append(rel_path)
        
        # Update core file patterns based on detected framework
        if analysis["framework_detected"]:
            framework = analysis["framework_detected"]
            if framework == "react":
                self.core_file_patterns.extend(["**/App.{jsx,tsx,js,ts}", "**/index.{js,ts,jsx,tsx}"])
            elif framework == "angular":
                self.core_file_patterns.extend(["**/app.module.ts", "**/app.component.ts"])
            elif framework == "django":
                self.core_file_patterns.extend(["**/urls.py", "**/views.py", "**/models.py"])
            elif framework == "flask":
                self.core_file_patterns.extend(["**/routes.py", "**/models.py", "**/app.py"])
        
        return analysis
    
    def prioritize_files(self, files: List[Tuple[str, str]]) -> List[Tuple[str, str, int]]:
        """Prioritize files based on importance for review.
        
        Args:
            files: List of (relative_path, absolute_path) tuples
            
        Returns:
            List of (relative_path, absolute_path, importance_score) tuples
        """
        if self.io:
            self.io.tool_output("Prioritizing files for review...")
        
        # Get recently modified files
        recently_modified = set(self.get_recently_modified_files())
        
        # Analyze project structure
        project_analysis = self.analyze_project_structure(files)
        
        # Extract core files
        core_files = set(project_analysis["important_files"])
        
        # Analyze dependencies between files
        file_imports, file_imported_by = self._analyze_dependencies(files)
        
        # Calculate importance scores
        scored_files = []
        
        for rel_path, abs_path in files:
            score = 0
            file_scores = {}
            
            # Check if recently modified
            if rel_path in recently_modified:
                score += self.importance_weights["is_modified_recently"]
                file_scores["is_modified_recently"] = True
            
            # Check if core file
            is_core = rel_path in core_files or any(fnmatch.fnmatch(rel_path, pattern) for pattern in self.core_file_patterns)
            if is_core:
                score += self.importance_weights["is_core_file"]
                file_scores["is_core_file"] = True
            
            # Check number of imports
            num_imports = len(file_imports.get(rel_path, set()))
            if num_imports > 5:
                score += self.importance_weights["has_many_imports"]
                file_scores["has_many_imports"] = num_imports
            
            # Check how often this file is imported
            num_imported_by = len(file_imported_by.get(rel_path, set()))
            if num_imported_by > 0:
                score += min(num_imported_by * 0.5, self.importance_weights["is_imported_by_many"])
                file_scores["is_imported_by_many"] = num_imported_by
            
            # Check for security-related keywords
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    
                    # Security keywords
                    security_keywords = ["password", "token", "auth", "secret", "key", "encrypt", "decrypt", "hash"]
                    if any(keyword in content.lower() for keyword in security_keywords):
                        score += self.importance_weights["has_security_keywords"]
                        file_scores["has_security_keywords"] = True
                    
                    # Check code-to-comment ratio
                    code_lines = 0
                    comment_lines = 0
                    for line in content.split('\n'):
                        stripped = line.strip()
                        if not stripped:
                            continue
                        if stripped.startswith('//') or stripped.startswith('#') or stripped.startswith('/*') or stripped.startswith('*'):
                            comment_lines += 1
                        else:
                            code_lines += 1
                    
                    comment_ratio = comment_lines / max(code_lines, 1) if code_lines > 0 else 0
                    if comment_ratio < 0.1 and code_lines > 20:  # Low comments on substantive code
                        score += self.importance_weights["code_to_comment_ratio"]
                        file_scores["code_to_comment_ratio"] = comment_ratio
                    
                    # File size
                    file_size = len(content)
                    if file_size > 10000:  # Larger files may need more attention
                        score += self.importance_weights["file_size"]
                        file_scores["file_size"] = file_size
            except Exception:
                pass
            
            # Lower priority for test files
            if "test" in rel_path.lower() or "spec" in rel_path.lower():
                score += self.importance_weights["test_file"]
                file_scores["test_file"] = True
            
            scored_files.append((rel_path, abs_path, score))
        
        # Sort files by importance score (descending)
        scored_files.sort(key=lambda x: x[2], reverse=True)
        
        if self.io:
            self.io.tool_output(f"Prioritized {len(scored_files)} files")
            if scored_files:
                top_files = scored_files[:5]
                self.io.tool_output("Top priority files:")
                for rel_path, _, score in top_files:
                    self.io.tool_output(f"  - {rel_path} (score: {score})")
        
        return scored_files
    
    def filter_by_natural_language(self, files: List[Tuple[str, str, int]], query: str) -> List[Tuple[str, str, int]]:
        """Filter files based on a natural language query.
        
        Args:
            files: List of (relative_path, absolute_path, importance_score) tuples
            query: Natural language query to filter by
            
        Returns:
            Filtered list of (relative_path, absolute_path, importance_score) tuples
        """
        if not query or not files:
            return files
        
        if self.io:
            self.io.tool_output(f"Filtering files based on query: '{query}'")
        
        # Special handling for "entire codebase" queries
        if "entire" in query.lower() and "codebase" in query.lower():
            if self.io:
                self.io.tool_output("Detected 'entire codebase' review request - not filtering")
            return files
        
        # Common coding concepts with related keywords
        code_concepts = {
            'authentication': ['auth', 'login', 'password', 'credential', 'token', 'jwt', 'oauth', 'session'],
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
        
        # Extract key concepts from the query
        query_lower = query.lower()
        matched_concepts = []
        
        for concept, keywords in code_concepts.items():
            # Check if the concept itself is mentioned
            if concept in query_lower:
                matched_concepts.append(concept)
                continue
            
            # Check for keyword matches
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                    matched_concepts.append(concept)
                    break
        
        # Check for file extensions mentioned
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
        
        if not matched_concepts:
            if self.io:
                self.io.tool_output("No specific filtering concepts detected in query, using all files")
            return files
        
        if self.io:
            self.io.tool_output(f"Filtering for concepts: {', '.join(matched_concepts)}")
        
        # Filter files based on matched concepts
        filtered_files = []
        
        for rel_path, abs_path, score in files:
            try:
                # Check file path first (cheaper)
                file_path_lower = rel_path.lower()
                
                # Check directory filters
                dir_matches = [c for c in matched_concepts if c.startswith("dir:")]
                if dir_matches and not any(os.path.dirname(rel_path).lower().find(c[4:]) >= 0 for c in dir_matches):
                    continue
                
                # Check file extension filters
                ext_matches = [c for c in matched_concepts if c.startswith("files:")]
                if ext_matches and not any(file_path_lower.endswith(c[6:]) for c in ext_matches):
                    continue
                
                # Read file content for deeper analysis
                try:
                    with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read().lower()
                except Exception:
                    # If we can't read the file, skip deeper analysis but include it anyway
                    filtered_files.append((rel_path, abs_path, score))
                    continue
                
                # Check if the file matches any of our target concepts
                concept_matches = []
                
                for concept in [c for c in matched_concepts if not c.startswith("dir:") and not c.startswith("files:")]:
                    # Check file path for concept
                    if concept in file_path_lower:
                        concept_matches.append(concept)
                        continue
                    
                    # Check content for concept keywords
                    if concept in code_concepts:
                        for keyword in code_concepts[concept]:
                            if re.search(r'\b' + re.escape(keyword) + r'\b', content):
                                concept_matches.append(concept)
                                break
                
                if concept_matches or not [c for c in matched_concepts if not c.startswith("dir:") and not c.startswith("files:")]:
                    # Boost score for files that match multiple concepts
                    concept_boost = min(len(concept_matches) * 2, 10)
                    filtered_files.append((rel_path, abs_path, score + concept_boost))
                
            except Exception as e:
                if self.io:
                    self.io.tool_warning(f"Error analyzing {rel_path}: {e}")
                # Include files that couldn't be analyzed to be safe
                filtered_files.append((rel_path, abs_path, score))
        
        # If no files matched, return the original list
        if not filtered_files:
            if self.io:
                self.io.tool_warning("No files matched your query criteria. Using all files instead.")
            return files
        
        # Sort by adjusted score
        filtered_files.sort(key=lambda x: x[2], reverse=True)
        
        if self.io:
            self.io.tool_output(f"Found {len(filtered_files)} files matching your query")
        
        return filtered_files
    
    def _analyze_dependencies(self, files: List[Tuple[str, str]]) -> Tuple[DefaultDict[str, Set[str]], DefaultDict[str, Set[str]]]:
        """Analyze dependencies between files.
        
        Args:
            files: List of (relative_path, absolute_path) tuples
            
        Returns:
            Tuple of (file_imports, file_imported_by) dictionaries
        """
        # Import patterns for different languages
        import_patterns = {
            '.py': [r'import\s+(\w+)', r'from\s+(\w+)'],
            '.js': [r'import.*from\s+[\'"](.+)[\'"]', r'require\([\'"](.+)[\'"]\)'],
            '.jsx': [r'import.*from\s+[\'"](.+)[\'"]'],
            '.ts': [r'import.*from\s+[\'"](.+)[\'"]'],
            '.tsx': [r'import.*from\s+[\'"](.+)[\'"]'],
            '.java': [r'import\s+([\w\.]+)'],
            '.cpp': [r'#include\s+[<"](.+)[>"]'],
            '.c': [r'#include\s+[<"](.+)[>"]'],
        }
        
        file_imports = defaultdict(set)
        file_imported_by = defaultdict(set)
        
        # Build a map of file basenames to paths
        file_map = {}
        for rel_path, _ in files:
            basename = os.path.basename(rel_path)
            # Remove extension
            basename_no_ext = os.path.splitext(basename)[0]
            file_map[basename] = rel_path
            file_map[basename_no_ext] = rel_path
        
        # Analyze imports in each file
        for rel_path, abs_path in files:
            ext = os.path.splitext(rel_path.lower())[1]
            
            if ext not in import_patterns:
                continue
            
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # Find imports
                for pattern in import_patterns[ext]:
                    for match in re.finditer(pattern, content):
                        imported = match.group(1)
                        
                        # Clean up the import
                        imported = imported.strip()
                        if imported.startswith('./') or imported.startswith('../'):
                            imported = os.path.basename(imported)
                        
                        # Check if we can resolve this import to a file
                        if imported in file_map:
                            imported_file = file_map[imported]
                            file_imports[rel_path].add(imported_file)
                            file_imported_by[imported_file].add(rel_path)
            except Exception:
                pass
        
        return file_imports, file_imported_by 