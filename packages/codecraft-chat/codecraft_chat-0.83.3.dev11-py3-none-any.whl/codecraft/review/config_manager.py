"""
Configuration management for code review.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Any


class ConfigManager:
    """Manages configuration for code review including defaults and project-specific settings."""
    
    DEFAULT_CONFIG = {
        # Standard exclusion patterns for build artifacts and generated code
        "exclude_patterns": [
            # Node.js related
            "**/node_modules/**",
            "**/dist/**", 
            "**/build/**",
            "**/coverage/**",
            "**/package-lock.json",
            "**/yarn.lock",
            
            # Python related
            "**/__pycache__/**",
            "**/.pytest_cache/**",
            "**/.mypy_cache/**",
            "**/*.pyc",
            "**/venv/**",
            "**/.env/**",
            "**/.venv/**",
            "**/env/**",
            "**/eggs/**",
            "**/.eggs/**",
            
            # Java/Maven/Gradle related
            "**/target/**",
            "**/.gradle/**",
            "**/out/**",
            "**/build/**",
            
            # .NET related
            "**/bin/**",
            "**/obj/**",
            
            # Editor/IDE settings
            "**/.idea/**",
            "**/.vscode/**",
            
            # Generated documentation
            "**/docs/build/**",
            "**/docs/_build/**",
            "**/site-packages/**",
            
            # Common binary and generated files
            "**/*.min.js",
            "**/*.bundle.js",
            "**/*.gz",
            "**/*.zip",
            "**/*.tar",
            "**/*.jar",
            "**/*.war",
            "**/*.ear",
            "**/*.class",
            "**/*.o",
            "**/*.a",
            "**/*.so",
            "**/*.dylib",
            "**/*.dll",
            "**/*.exe",
        ],
        
        # Included file extensions for source code
        "include_extensions": [
            # Programming languages
            ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
            ".cs", ".go", ".rb", ".php", ".swift", ".kt", ".rs", ".dart", ".scala",
            
            # Web development
            ".html", ".css", ".scss", ".sass", ".less", ".vue", ".svelte",
            
            # Config and structured data
            ".json", ".yaml", ".yml", ".toml", ".xml", ".graphql", ".proto",
            
            # Shell and scripts
            ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd",
            
            # Infrastructure
            ".tf", ".hcl", ".dockerfile", ".docker", ".dockerignore",
            ".sql", ".prisma", ".schema",
            
            # Documentation and text
            # Not included by default: ".md", ".rst", ".txt",
        ],
        
        # Maximum size for files to be considered (in bytes)
        "max_file_size": 1000000,  # 1MB
        
        # Maximum number of files to include in one review batch
        "batch_size": 10,
        
        # Model token limits
        "token_reserve": 2000,
        "tokens_per_batch": 6000,
        
        # Context management
        "memory_enabled": True,
        "memory_persistence": True,
        
        # Project-specific analysis settings
        "project_analysis": {
            "prioritize_modified": True,
            "prioritize_core": True,
            "analyze_dependencies": True,
        },
        
        # Output settings
        "output_format": "md",
        "output_file": "TODO.md",
    }
    
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.config_path = os.path.join(workspace_root, '.codecraft', 'review_config.json')
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
        
    def load_config(self) -> None:
        """Load configuration from project config file if it exists."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    project_config = json.load(f)
                    # Update the default config with project-specific overrides
                    for key, value in project_config.items():
                        if key in self.config:
                            if isinstance(self.config[key], dict) and isinstance(value, dict):
                                # Merge dictionaries
                                self.config[key].update(value)
                            elif isinstance(self.config[key], list) and isinstance(value, list):
                                # For lists, use the project value to completely override default
                                self.config[key] = value
                            else:
                                # For simple values, just override
                                self.config[key] = value
        except Exception as e:
            print(f"Error loading review configuration: {e}")
    
    def save_config(self) -> None:
        """Save the current configuration to the project config file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving review configuration: {e}")
    
    def get_exclude_patterns(self) -> List[str]:
        """Get the exclude patterns for the project."""
        return self.config["exclude_patterns"]
    
    def get_include_extensions(self) -> List[str]:
        """Get the file extensions to include."""
        return self.config["include_extensions"]
    
    def get_max_file_size(self) -> int:
        """Get the maximum file size to include."""
        return self.config["max_file_size"]
    
    def get_batch_size(self) -> int:
        """Get the maximum number of files per batch."""
        return self.config["batch_size"]
    
    def get_token_limits(self) -> Dict[str, int]:
        """Get token limits for the model."""
        return {
            "reserve": self.config["token_reserve"],
            "per_batch": self.config["tokens_per_batch"]
        }
    
    def is_memory_enabled(self) -> bool:
        """Check if memory features are enabled."""
        return self.config["memory_enabled"]
    
    def is_memory_persistence_enabled(self) -> bool:
        """Check if memory persistence is enabled."""
        return self.config["memory_persistence"]
    
    def get_project_analysis_settings(self) -> Dict[str, bool]:
        """Get project analysis settings."""
        return self.config["project_analysis"]
    
    def get_output_settings(self) -> Dict[str, str]:
        """Get output format and file settings."""
        return {
            "format": self.config["output_format"],
            "file": self.config["output_file"]
        }
    
    def update_config(self, key: str, value: Any) -> None:
        """Update a specific configuration setting."""
        if key in self.config:
            self.config[key] = value
            self.save_config() 