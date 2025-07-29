"""
Kanban board integration for code reviews.

This module provides functionality to export TODOs from code reviews to popular
Kanban board platforms like Notion and Trello.
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# Conditional imports for optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class KanbanIntegration:
    """Base class for Kanban board integrations."""
    
    def __init__(self, io):
        """Initialize the Kanban integration.
        
        Args:
            io: The IO interface for user interaction
        """
        self.io = io
    
    def export_todos(self, todos: List[Dict[str, Any]], board_info: Dict[str, Any]) -> bool:
        """Export TODOs to a Kanban board.
        
        Args:
            todos: List of TODO items from code review
            board_info: Information about the target Kanban board
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement export_todos")
    
    @staticmethod
    def parse_todo_items(review_content: str) -> List[Dict[str, Any]]:
        """Parse TODO items from review content.
        
        Args:
            review_content: The content of the review
            
        Returns:
            List of parsed TODO items
        """
        import re
        
        # Pattern for standard review output format
        todo_pattern = r'- \[([ xX])\] \*\*Issue\*\*: (.*?)(?:\n\s+\*\*Location\*\*: (.*?))?(?:\n\s+\*\*Priority\*\*: (.*?))?(?:\n\s+\*\*Details\*\*: (.*?))?(?:\n\s+\*\*Category\*\*: (.*?))?(?:\n\s+\*\*Effort\*\*: (.*?))?(?:\n\s+\*\*Dependencies\*\*: (.*?))?(?=\n- \[|$)'
        
        # Pattern for simple TODO.md format
        simple_todo_pattern = r'- \[([ xX])\] (.*?)(?:\n|$)'
        
        todos = []
        
        # Try the standard format first
        matches = re.findall(todo_pattern, review_content, re.DOTALL)
        
        if matches:
            for match in matches:
                status, issue, location, priority, details, category, effort, dependencies = match
                resolved = status.strip().lower() in ['x']
                
                todos.append({
                    'issue': issue.strip(),
                    'location': location.strip() if location else '',
                    'resolved': resolved,
                    'details': details.strip() if details else '',
                    'priority': priority.strip() if priority else 'Medium',
                    'category': category.strip() if category else 'Code Quality',
                    'effort': effort.strip() if effort else 'Medium',
                    'dependencies': dependencies.strip() if dependencies else '',
                    'created_at': datetime.datetime.now().isoformat()
                })
        else:
            # If no standard format TODOs found, try the simple format
            simple_matches = re.findall(simple_todo_pattern, review_content, re.MULTILINE)
            
            if simple_matches:
                for match in simple_matches:
                    status, issue = match
                    resolved = status.strip().lower() in ['x']
                    
                    # Try to extract location from the issue text if it contains a file path pattern
                    location = ''
                    location_match = re.search(r'(\S+\.\w+(?::\d+)?)', issue)
                    if location_match:
                        location = location_match.group(1)
                    
                    # Try to extract priority from the issue text
                    priority = 'Medium'
                    for p in ['high', 'medium', 'low']:
                        if p in issue.lower():
                            priority = p.capitalize()
                            break
                    
                    todos.append({
                        'issue': issue.strip(),
                        'location': location,
                        'resolved': resolved,
                        'details': '',
                        'priority': priority,
                        'category': 'Code Quality',
                        'effort': 'Medium',
                        'dependencies': '',
                        'created_at': datetime.datetime.now().isoformat()
                    })
        
        return todos


class NotionIntegration(KanbanIntegration):
    """Integration with Notion Kanban boards."""
    
    def __init__(self, io, token: str, database_id: str):
        """Initialize the Notion integration.
        
        Args:
            io: The IO interface for user interaction
            token: Notion API token
            database_id: Notion database ID for the Kanban board
        """
        super().__init__(io)
        self.token = token
        self.database_id = database_id
        
        if not REQUESTS_AVAILABLE:
            self.io.tool_error("The 'requests' package is required for Notion integration.")
            raise ImportError("The 'requests' package is required for Notion integration.")
    
    def check_database_exists(self) -> bool:
        """Check if the database exists and has the required structure.
        
        Returns:
            bool: True if the database exists and has the required structure
        """
        if not self.database_id:
            return False
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        try:
            response = requests.get(
                f"https://api.notion.com/v1/databases/{self.database_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                self.io.tool_error(f"Database ID {self.database_id} is not valid or you don't have access to it.")
                return False
            
            # Check if the database has the required properties
            data = response.json()
            properties = data.get("properties", {})
            
            required_properties = {
                "Name": "title",
                "Status": "select",
                "Priority": "select",
                "Category": "select",
                "Location": "rich_text",
                "Effort": "select"
            }
            
            missing_properties = []
            for prop_name, prop_type in required_properties.items():
                if prop_name not in properties:
                    missing_properties.append(prop_name)
                elif prop_name != "Name" and properties[prop_name]["type"] != prop_type:
                    missing_properties.append(f"{prop_name} (wrong type, should be {prop_type})")
            
            if missing_properties:
                self.io.tool_error(f"Database exists but is missing required properties: {', '.join(missing_properties)}")
                return False
            
            return True
            
        except Exception as e:
            self.io.tool_error(f"Error checking database: {str(e)}")
            return False
    
    def create_database(self) -> bool:
        """Create a new database with the required structure.
        
        Returns:
            bool: True if the database was created successfully
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Search for pages the integration has access to
        try:
            response = requests.post(
                "https://api.notion.com/v1/search",
                headers=headers,
                json={"filter": {"property": "object", "value": "page"}}
            )
            
            if response.status_code != 200:
                self.io.tool_error(f"Failed to search for pages: {response.status_code} - {response.text}")
                return False
                
            pages = response.json().get("results", [])
            
            # Check if we found any pages
            if not pages:
                self.io.tool_error("No pages found that the integration has access to.")
                self.io.tool_output("Please share a page with your integration and try again.")
                return False
            
            # Use the first page as parent
            selected_page = pages[0]
            
            # Get project name from the workspace path
            project_name = os.path.basename(os.path.normpath(os.getcwd()))
            
            # Create the database
            payload = {
                "parent": {"type": "page_id", "page_id": selected_page["id"]},
                "icon": {
                    "type": "emoji",
                    "emoji": "📋"
                },
                "cover": {
                    "type": "external",
                    "external": {
                        "url": "https://images.unsplash.com/photo-1526280760714-f9e8b26f318f"
                    }
                },
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"{project_name} TODOs",
                            "link": None
                        }
                    }
                ],
                "properties": {
                    "Name": {
                        "title": {}
                    },
                    "Status": {
                        "select": {
                            "options": [
                                {"name": "To Do", "color": "red"},
                                {"name": "In Progress", "color": "yellow"},
                                {"name": "Done", "color": "green"}
                            ]
                        }
                    },
                    "Priority": {
                        "select": {
                            "options": [
                                {"name": "High", "color": "red"},
                                {"name": "Medium", "color": "yellow"},
                                {"name": "Low", "color": "blue"}
                            ]
                        }
                    },
                    "Category": {
                        "select": {
                            "options": [
                                {"name": "Code Quality", "color": "purple"},
                                {"name": "Security", "color": "red"},
                                {"name": "Performance", "color": "orange"},
                                {"name": "Architecture", "color": "blue"},
                                {"name": "Documentation", "color": "green"},
                                {"name": "Bug Fix", "color": "yellow"}
                            ]
                        }
                    },
                    "Location": {
                        "rich_text": {}
                    },
                    "Effort": {
                        "select": {
                            "options": [
                                {"name": "Small", "color": "green"},
                                {"name": "Medium", "color": "yellow"},
                                {"name": "Large", "color": "red"}
                            ]
                        }
                    }
                }
            }
            
            # Create the database
            response = requests.post(
                "https://api.notion.com/v1/databases",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                self.io.tool_error(f"Failed to create database: {response.status_code} - {response.text}")
                return False
                
            database_id = response.json().get("id")
            self.database_id = database_id
            
            self.io.tool_output(f"Successfully created a new Notion database!")
            self.io.tool_output(f"Database ID: {database_id}")
            self.io.tool_output("Please save this ID in your NOTION_DATABASE_ID environment variable:")
            self.io.tool_output(f"  set NOTION_DATABASE_ID={database_id}")
            
            return True
            
        except Exception as e:
            self.io.tool_error(f"Error creating database: {str(e)}")
            return False
    
    def export_todos(self, todos: List[Dict[str, Any]], board_info: Dict[str, Any]) -> bool:
        """Export TODOs to a Notion database.
        
        Args:
            todos: List of TODO items from code review
            board_info: Information about the target Notion database
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        if not todos:
            self.io.tool_output("No TODOs to export to Notion.")
            return True
        
        # Check if the database exists and has the required structure
        if not self.check_database_exists():
            self.io.tool_output("The specified Notion database doesn't exist or has an invalid structure.")
            
            # Ask the user if they want to create a new database
            create_db = False
            if board_info.get('auto_create_database', False):
                create_db = True
            else:
                create_db = self.io.confirm_ask("Would you like to create a new database now?", default="y")
            
            if create_db:
                if not self.create_database():
                    self.io.tool_error("Failed to create a new database.")
                    return False
            else:
                self.io.tool_error("Cannot export TODOs without a valid database.")
                return False
        
        self.io.tool_output(f"Exporting {len(todos)} TODOs to Notion database...")
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        success_count = 0
        
        for todo in todos:
            # Skip resolved TODOs unless specified in board_info
            # Ensure resolved is a proper boolean, not a string
            is_resolved = False
            if 'resolved' in todo:
                if isinstance(todo['resolved'], bool):
                    is_resolved = todo['resolved']
                elif isinstance(todo['resolved'], str):
                    is_resolved = todo['resolved'].lower() in ['true', 'yes', 'y', 'x']
            
            if is_resolved and not board_info.get('include_resolved', False):
                continue
                
            # Fix comma issues in select fields
            category = todo.get('category', 'Code Quality')
            if ',' in category:
                # Take only the first category before any comma
                category = category.split(',')[0].strip()
                
            priority = todo.get('priority', 'Medium')
            if ',' in priority:
                # Take only the first priority before any comma
                priority = priority.split(',')[0].strip()
                
            effort = todo.get('effort', 'Medium')
            if ',' in effort:
                # Take only the first effort before any comma
                effort = effort.split(',')[0].strip()
                
            # Remove any text in parentheses from select fields
            if '(' in category:
                category = category.split('(')[0].strip()
            if '(' in priority:
                priority = priority.split('(')[0].strip()
            if '(' in effort:
                effort = effort.split('(')[0].strip()
            
            # Create the Notion page properties
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": todo['issue']
                            }
                        }
                    ]
                },
                "Status": {
                    "select": {
                        "name": "Done" if is_resolved else "To Do"
                    }
                },
                "Priority": {
                    "select": {
                        "name": priority
                    }
                },
                "Category": {
                    "select": {
                        "name": category
                    }
                }
            }
            
            # Add location if available
            if todo['location']:
                properties["Location"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": todo['location']
                            }
                        }
                    ]
                }
            
            # Add effort if available
            if effort:
                properties["Effort"] = {
                    "select": {
                        "name": effort
                    }
                }
            
            # Prepare the request payload
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": properties,
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": todo['details']
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            
            try:
                response = requests.post(
                    "https://api.notion.com/v1/pages",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    self.io.tool_error(f"Failed to create Notion page: {response.status_code} - {response.text}")
            
            except Exception as e:
                self.io.tool_error(f"Error exporting TODO to Notion: {str(e)}")
        
        self.io.tool_output(f"Successfully exported {success_count} of {len(todos)} TODOs to Notion.")
        return success_count > 0


class TrelloIntegration(KanbanIntegration):
    """Integration with Trello Kanban boards."""
    
    def __init__(self, io, api_key: str, token: str, board_id: str):
        """Initialize the Trello integration.
        
        Args:
            io: The IO interface for user interaction
            api_key: Trello API key
            token: Trello API token
            board_id: Trello board ID
        """
        super().__init__(io)
        self.api_key = api_key
        self.token = token
        self.board_id = board_id
        
        if not REQUESTS_AVAILABLE:
            self.io.tool_error("The 'requests' package is required for Trello integration.")
            raise ImportError("The 'requests' package is required for Trello integration.")
        
        # Optional py-trello support
        try:
            from trello import TrelloClient
            self.client = TrelloClient(
                api_key=api_key,
                token=token
            )
            self.use_client = True
        except ImportError:
            self.use_client = False
    
    def _get_lists(self) -> Dict[str, str]:
        """Get all lists from the board.
        
        Returns:
            Dict mapping list names to list IDs
        """
        if self.use_client:
            board = self.client.get_board(self.board_id)
            return {lst.name: lst.id for lst in board.open_lists()}
        else:
            url = f"https://api.trello.com/1/boards/{self.board_id}/lists"
            params = {
                "key": self.api_key,
                "token": self.token
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                lists = response.json()
                return {lst['name']: lst['id'] for lst in lists}
            else:
                self.io.tool_error(f"Failed to get Trello lists: {response.status_code} - {response.text}")
                return {}
    
    def export_todos(self, todos: List[Dict[str, Any]], board_info: Dict[str, Any]) -> bool:
        """Export TODOs to a Trello board.
        
        Args:
            todos: List of TODO items from code review
            board_info: Information about the target Trello board
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        if not todos:
            self.io.tool_output("No TODOs to export to Trello.")
            return True
        
        self.io.tool_output(f"Exporting {len(todos)} TODOs to Trello board...")
        
        # Get the lists on the board
        lists = self._get_lists()
        
        # Determine which list to use for new cards
        todo_list_name = board_info.get('todo_list', 'To Do')
        done_list_name = board_info.get('done_list', 'Done')
        
        todo_list_id = lists.get(todo_list_name)
        done_list_id = lists.get(done_list_name)
        
        if not todo_list_id:
            self.io.tool_error(f"Could not find '{todo_list_name}' list on the Trello board.")
            return False
        
        if not done_list_id:
            self.io.tool_error(f"Could not find '{done_list_name}' list on the Trello board.")
            return False
        
        success_count = 0
        
        for todo in todos:
            # Skip resolved TODOs unless specified in board_info
            # Ensure resolved is a proper boolean, not a string
            is_resolved = False
            if 'resolved' in todo:
                if isinstance(todo['resolved'], bool):
                    is_resolved = todo['resolved']
                elif isinstance(todo['resolved'], str):
                    is_resolved = todo['resolved'].lower() in ['true', 'yes', 'y', 'x']
            
            if is_resolved and not board_info.get('include_resolved', False):
                continue
            
            # Determine which list to add the card to
            list_id = done_list_id if is_resolved else todo_list_id
            
            # Create card title
            card_name = todo['issue']
            
            # Create card description
            card_desc = f"**Details:** {todo['details']}\n\n"
            if todo['location']:
                card_desc += f"**Location:** {todo['location']}\n"
            card_desc += f"**Priority:** {todo['priority']}\n"
            card_desc += f"**Category:** {todo['category']}\n"
            card_desc += f"**Effort:** {todo['effort']}\n"
            if todo['dependencies']:
                card_desc += f"**Dependencies:** {todo['dependencies']}\n"
            
            # Add labels based on priority and category
            labels = []
            if todo['priority'] == 'High':
                labels.append('red')
            elif todo['priority'] == 'Medium':
                labels.append('yellow')
            elif todo['priority'] == 'Low':
                labels.append('green')
            
            try:
                if self.use_client:
                    # Use py-trello if available
                    board = self.client.get_board(self.board_id)
                    list_obj = next((lst for lst in board.open_lists() if lst.id == list_id), None)
                    if list_obj:
                        card = list_obj.add_card(name=card_name, desc=card_desc)
                        for label_color in labels:
                            label = next((lbl for lbl in board.get_labels() if lbl.color == label_color), None)
                            if label:
                                card.add_label(label)
                        success_count += 1
                else:
                    # Use REST API directly
                    url = "https://api.trello.com/1/cards"
                    params = {
                        "key": self.api_key,
                        "token": self.token,
                        "idList": list_id,
                        "name": card_name,
                        "desc": card_desc
                    }
                    
                    response = requests.post(url, params=params)
                    if response.status_code == 200:
                        card_id = response.json()['id']
                        
                        # Add labels if needed
                        for label_color in labels:
                            label_url = f"https://api.trello.com/1/cards/{card_id}/labels"
                            label_params = {
                                "key": self.api_key,
                                "token": self.token,
                                "color": label_color
                            }
                            requests.post(label_url, params=label_params)
                        
                        success_count += 1
                    else:
                        self.io.tool_error(f"Failed to create Trello card: {response.status_code} - {response.text}")
            
            except Exception as e:
                self.io.tool_error(f"Error exporting TODO to Trello: {str(e)}")
        
        self.io.tool_output(f"Successfully exported {success_count} of {len(todos)} TODOs to Trello.")
        return success_count > 0


def create_kanban_integration(io, platform: str, config: Dict[str, Any]) -> Optional[KanbanIntegration]:
    """Create a Kanban integration instance based on the platform.
    
    Args:
        io: The IO interface for user interaction
        platform: The Kanban platform to use ('notion' or 'trello')
        config: Configuration for the integration
        
    Returns:
        A KanbanIntegration instance or None if the platform is not supported
    """
    if platform.lower() == 'notion':
        token = config.get('token') or os.environ.get('NOTION_TOKEN')
        database_id = config.get('database_id') or os.environ.get('NOTION_DATABASE_ID')
        
        if not token:
            io.tool_error("Notion integration requires a token.")
            io.tool_output("You can create one at https://www.notion.so/my-integrations")
            io.tool_output("Then set the NOTION_TOKEN environment variable.")
            return None
        
        # Allow empty database_id for auto-creation
        if not database_id:
            io.tool_output("No Notion database ID provided. A new database will be created automatically.")
            database_id = ""
        
        return NotionIntegration(io, token, database_id)
    
    elif platform.lower() == 'trello':
        api_key = config.get('api_key') or os.environ.get('TRELLO_API_KEY')
        token = config.get('token') or os.environ.get('TRELLO_TOKEN')
        board_id = config.get('board_id') or os.environ.get('TRELLO_BOARD_ID')
        
        if not api_key or not token or not board_id:
            io.tool_error("Trello integration requires an API key, token, and board ID.")
            return None
        
        return TrelloIntegration(io, api_key, token, board_id)
    
    else:
        io.tool_error(f"Unsupported Kanban platform: {platform}")
        return None


def export_todos_to_kanban(
    io,
    review_content: str,
    platform: str,
    config: Dict[str, Any],
    board_info: Optional[Dict[str, Any]] = None
) -> bool:
    """Export TODOs from a review to a Kanban board.
    
    Args:
        io: The IO interface for user interaction
        review_content: The content of the review
        platform: The Kanban platform to use ('notion' or 'trello')
        config: Configuration for the integration
        board_info: Additional information about the target board
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    if not REQUESTS_AVAILABLE:
        io.tool_error("The 'requests' package is required for Kanban integration.")
        return False
    
    # Ensure board_info is a dictionary
    if board_info is None:
        board_info = {}
        
    # Parse TODOs from the review content
    todos = KanbanIntegration.parse_todo_items(review_content)
    
    if not todos:
        io.tool_output("No TODOs found in the review content.")
        return True
    
    # Create the integration
    integration = create_kanban_integration(io, platform, config)
    if not integration:
        return False
    
    # Export the TODOs
    return integration.export_todos(todos, board_info) 