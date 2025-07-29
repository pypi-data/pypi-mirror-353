"""
Context management for code review sessions.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union


class ReviewContext:
    """Manages context data for a review session."""
    
    def __init__(self, workspace_root: str, io=None):
        self.workspace_root = workspace_root
        self.io = io  # IO interface for output
        self.context_dir = os.path.join(workspace_root, '.codecraft', 'review')
        
        # Ensure the context directory exists
        os.makedirs(self.context_dir, exist_ok=True)
        
        # Initialize context data structure
        self.context = {
            "session_id": self._generate_session_id(),
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "files_reviewed": set(),
            "todo_items": [],
            "file_stats": {},
            "batches": [],
            "recent_focus": None,
            "progress": {
                "total_files": 0,
                "reviewed_files": 0,
                "completion_percentage": 0,
                "high_priority_issues": 0,
                "medium_priority_issues": 0,
                "low_priority_issues": 0,
            }
        }
        
        # Try to load existing context if available
        self._load_context()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = int(time.time())
        return f"review_{timestamp}"
    
    def _get_context_path(self) -> str:
        """Get the path to the context file."""
        return os.path.join(self.context_dir, 'review_context.json')
    
    def _load_context(self) -> None:
        """Load review context from disk if available."""
        try:
            context_path = self._get_context_path()
            if os.path.exists(context_path):
                with open(context_path, 'r', encoding='utf-8') as f:
                    loaded_context = json.load(f)
                    
                    # Special handling for sets which are saved as lists
                    if 'files_reviewed' in loaded_context:
                        loaded_context['files_reviewed'] = set(loaded_context['files_reviewed'])
                    
                    # Update context with loaded data
                    self.context.update(loaded_context)
                    
                    if self.io:
                        self.io.tool_output(f"Loaded review context from previous session")
        except Exception as e:
            if self.io:
                self.io.tool_warning(f"Failed to load review context: {e}")
    
    def save_context(self) -> None:
        """Save the current context to disk."""
        try:
            context_path = self._get_context_path()
            
            # Convert sets to lists for JSON serialization
            serializable_context = self.context.copy()
            if isinstance(serializable_context.get('files_reviewed'), set):
                serializable_context['files_reviewed'] = list(serializable_context['files_reviewed'])
            
            # Update last updated timestamp
            serializable_context['last_updated'] = datetime.now().isoformat()
            
            with open(context_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_context, f, indent=2)
        except Exception as e:
            if self.io:
                self.io.tool_warning(f"Failed to save review context: {e}")
    
    def update_file_reviewed(self, file_path: str) -> None:
        """Mark a file as reviewed."""
        self.context['files_reviewed'].add(file_path)
        self.context['progress']['reviewed_files'] = len(self.context['files_reviewed'])
        self._update_progress()
        self.save_context()
    
    def update_files_reviewed(self, file_paths: List[str]) -> None:
        """Mark multiple files as reviewed."""
        self.context['files_reviewed'].update(file_paths)
        self.context['progress']['reviewed_files'] = len(self.context['files_reviewed'])
        self._update_progress()
        self.save_context()
    
    def is_file_reviewed(self, file_path: str) -> bool:
        """Check if a file has been reviewed."""
        return file_path in self.context['files_reviewed']
    
    def get_reviewed_files(self) -> Set[str]:
        """Get the set of reviewed files."""
        return self.context['files_reviewed']
    
    def add_todo_item(self, todo_item: Dict[str, Any]) -> None:
        """Add a TODO item to the context."""
        self.context['todo_items'].append(todo_item)
        
        # Update priority counts
        priority = todo_item.get('priority', '').lower()
        if priority == 'high':
            self.context['progress']['high_priority_issues'] += 1
        elif priority == 'medium':
            self.context['progress']['medium_priority_issues'] += 1
        elif priority == 'low':
            self.context['progress']['low_priority_issues'] += 1
        
        self.save_context()
    
    def add_batch(self, batch_info: Dict[str, Any]) -> None:
        """Add information about a processed batch."""
        self.context['batches'].append(batch_info)
        self.save_context()
    
    def update_file_stats(self, file_path: str, stats: Dict[str, Any]) -> None:
        """Update statistics for a file."""
        self.context['file_stats'][file_path] = stats
        self.save_context()
    
    def set_total_files(self, total_files: int) -> None:
        """Set the total number of files to review."""
        self.context['progress']['total_files'] = total_files
        self._update_progress()
        self.save_context()
    
    def _update_progress(self) -> None:
        """Update progress percentage."""
        total = self.context['progress']['total_files']
        reviewed = self.context['progress']['reviewed_files']
        
        if total > 0:
            self.context['progress']['completion_percentage'] = int((reviewed / total) * 100)
        else:
            self.context['progress']['completion_percentage'] = 0
    
    def set_recent_focus(self, focus: str) -> None:
        """Set the most recent focus area."""
        self.context['recent_focus'] = focus
        self.save_context()
    
    def get_recent_focus(self) -> Optional[str]:
        """Get the most recent focus area."""
        return self.context['recent_focus']
    
    def get_progress(self) -> Dict[str, Union[int, float]]:
        """Get the current progress."""
        return self.context['progress']
    
    def get_todo_items(self) -> List[Dict[str, Any]]:
        """Get all TODO items."""
        return self.context['todo_items']
    
    def get_file_stats(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a file or all files."""
        if file_path:
            return self.context['file_stats'].get(file_path, {})
        return self.context['file_stats']
    
    def reset_context(self) -> None:
        """Reset the context to a fresh state."""
        self.context = {
            "session_id": self._generate_session_id(),
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "files_reviewed": set(),
            "todo_items": [],
            "file_stats": {},
            "batches": [],
            "recent_focus": None,
            "progress": {
                "total_files": 0,
                "reviewed_files": 0,
                "completion_percentage": 0,
                "high_priority_issues": 0,
                "medium_priority_issues": 0,
                "low_priority_issues": 0,
            }
        }
        self.save_context()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session."""
        return {
            "session_id": self.context['session_id'],
            "created": self.context['created'],
            "last_updated": self.context['last_updated'],
            "reviewed_files_count": len(self.context['files_reviewed']),
            "todo_items_count": len(self.context['todo_items']),
            "batches_count": len(self.context['batches']),
            "progress": self.context['progress']
        } 