"""
Notion integration for Codecraft.

This module provides functionality to integrate with Notion's API
for managing TODOs in a Kanban board format.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Check if notion-client is installed
try:
    from notion_client import Client
    from notion_client.errors import APIResponseError, APIErrorCode
    from notion_client.helpers import iterate_paginated_api, collect_paginated_api
except ImportError:
    Client = None
    APIResponseError = Exception
    APIErrorCode = None


class NotionIntegration:
    """Handles integration with Notion API."""

    CONFIG_FILE = "notion_config.json"

    def __init__(self, io, coder):
        """Initialize the Notion integration.

        Args:
            io: The IO interface for interacting with the user.
            coder: The Coder instance for accessing repository information.
        """
        self.io = io
        self.coder = coder
        self.client = None
        
        # Try loading config from file first, then fall back to environment variables
        config = self._load_config()
        self.token = config.get("token") or os.environ.get("NOTION_TOKEN")
        self.database_id = config.get("database_id") or os.environ.get("NOTION_DATABASE_ID")
        
        # If token was loaded from config, set it in environment so other parts of code work
        if self.token and not os.environ.get("NOTION_TOKEN"):
            os.environ["NOTION_TOKEN"] = self.token
            
        # If database_id was loaded from config, set it in environment
        if self.database_id and not os.environ.get("NOTION_DATABASE_ID"):
            os.environ["NOTION_DATABASE_ID"] = self.database_id
            
        self._initialize_client()

    def _initialize_client(self) -> bool:
        """Initialize the Notion client.

        Returns:
            bool: True if client was successfully initialized, False otherwise.
        """
        if not self.token:
            return False
            
        if Client is None:
            return False
            
        try:
            self.client = Client(auth=self.token)
            return True
        except Exception as e:
            self.io.tool_error(f"Failed to initialize Notion client: {e}")
            return False
            
    def _config_path(self) -> Path:
        """Get the path to the configuration file.
        
        Returns:
            Path: The configuration file path
        """
        # Store in the same directory as the script or in repository root
        try:
            repo_dir = self.coder.repo_dir
            if repo_dir:
                return Path(repo_dir) / self.CONFIG_FILE
        except:
            pass
            
        # Fallback to the current directory
        return Path.cwd() / self.CONFIG_FILE
        
    def _save_config(self, token: str = None, database_id: str = None) -> bool:
        """Save configuration to file.
        
        Args:
            token: Notion API token
            database_id: Notion database ID
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        # Use existing values if not provided
        if token is None:
            token = self.token
            
        if database_id is None:
            database_id = self.database_id
            
        config = {
            "token": token,
            "database_id": database_id
        }
        
        try:
            with open(self._config_path(), "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            self.io.tool_error(f"Error saving configuration: {e}")
            return False
            
    def _load_config(self) -> dict:
        """Load configuration from file.
        
        Returns:
            dict: Configuration dict with token and database_id keys
        """
        try:
            config_path = self._config_path()
            if config_path.exists():
                with open(config_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            self.io.tool_error(f"Error loading configuration: {e}")
        
        return {}

    def setup(self, token: str = None, database_id: str = None) -> bool:
        """Setup Notion integration with token and database ID.
        
        Args:
            token: Notion API token
            database_id: Notion database ID
            
        Returns:
            bool: True if setup was successful, False otherwise
        """
        # Update token if provided
        if token:
            self.token = token
            os.environ["NOTION_TOKEN"] = token
            self._initialize_client()
            
        # Update database ID if provided
        if database_id:
            self.database_id = database_id
            os.environ["NOTION_DATABASE_ID"] = database_id
            
        # Save configuration to file
        saved = self._save_config(token, database_id)
        if saved:
            self.io.tool_output("Notion configuration saved to file")
            
        return self.is_ready()

    def is_ready(self) -> bool:
        """Check if the Notion integration is ready to use.
        
        Returns:
            bool: True if ready, False otherwise.
        """
        return self.client is not None and self.database_id is not None

    def display_readiness_status(self) -> None:
        """Display the readiness status of Notion integration."""
        if Client is None:
            self.io.tool_error("✗ notion-client package not installed")
            self.io.tool_output("  Run: pip install notion-client")
            return
            
        if not self.token:
            self.io.tool_error("✗ NOTION_TOKEN not configured")
            self.io.tool_output("  Run: /notion setup --token YOUR_TOKEN")
            return
            
        if self.client:
            self.io.tool_output("✓ Notion client initialized with token")
        else:
            self.io.tool_error("✗ Failed to initialize Notion client with token")
            return
            
        if not self.database_id:
            self.io.tool_error("✗ NOTION_DATABASE_ID not configured")
            self.io.tool_output("  Run: /notion setup --database-id YOUR_DATABASE_ID")
            return
            
        # Final check
        if self.is_ready():
            config_path = self._config_path()
            if config_path.exists():
                self.io.tool_output(f"✓ Configuration saved in {config_path}")
            self.io.tool_output("✓ Notion integration is fully configured")
        else:
            self.io.tool_error("✗ Notion integration is not fully configured")

    def _clean_page_id(self, page_id: str) -> str:
        """Clean a page ID to ensure it's in the format Notion API expects.
        
        Args:
            page_id: The raw page ID from the URL or user input
            
        Returns:
            str: The cleaned page ID suitable for API calls
        """
        # Remove any text before a hyphen that isn't part of the UUID format
        if '-' in page_id and not page_id[8:9] == '-':
            # This likely has a prefix like "PAGE-" or similar
            parts = page_id.split('-', 1)
            if len(parts) > 1:
                page_id = parts[1]
                
        # Remove any non-alphanumeric characters except dashes
        # This handles cases like spaces, special characters, etc.
        import re
        page_id = re.sub(r'[^a-zA-Z0-9\-]', '', page_id)
        
        return page_id
        
    def create_kanban_database(self, title: str = "Codecraft TODOs", parent_page_id: str = None) -> str:
        """Create a Kanban database in Notion.
        
        Args:
            title: The title for the database.
            parent_page_id: The ID of the parent page where the database will be created.
            
        Returns:
            str: The ID of the created database, or None if creation failed.
        """
        if not self.client:
            self.io.tool_error("Notion client not initialized")
            return None
            
        try:
            if not parent_page_id:
                self.io.tool_error("Parent page ID is required to create a database")
                self.io.tool_output("1. Open a page in Notion where you want to create the database")
                self.io.tool_output("2. Share that page with your integration")
                self.io.tool_output("3. Get the page ID from the URL: https://www.notion.so/PAGE_ID?...")
                self.io.tool_output("   The page ID is the part after notion.so/ and before the first ? or #")
                return None
                
            # Clean the page ID to ensure it's in the right format
            cleaned_page_id = self._clean_page_id(parent_page_id)
            self.io.tool_output(f"Using page ID: {cleaned_page_id}")
            
            # Create the database within the specified parent page
            self.io.tool_output(f"Creating database within the page...")
            db_response = self.client.databases.create(
                parent={"type": "page_id", "page_id": cleaned_page_id},
                title=[
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ],
                properties={
                    "Name": {"title": {}},
                    "Status": {
                        "select": {
                            "options": [
                                {"name": "Backlog", "color": "gray"},
                                {"name": "To Do", "color": "blue"},
                                {"name": "In Progress", "color": "yellow"},
                                {"name": "Done", "color": "green"},
                                {"name": "Cancelled", "color": "red"}
                            ]
                        }
                    },
                    "Priority": {
                        "select": {
                            "options": [
                                {"name": "Low", "color": "gray"},
                                {"name": "Medium", "color": "yellow"},
                                {"name": "High", "color": "red"}
                            ]
                        }
                    },
                    "Category": {
                        "multi_select": {
                            "options": [
                                {"name": "Feature", "color": "blue"},
                                {"name": "Bug", "color": "red"},
                                {"name": "Documentation", "color": "green"},
                                {"name": "Task", "color": "yellow"}
                            ]
                        }
                    },
                    "Effort": {
                        "select": {
                            "options": [
                                {"name": "Small", "color": "green"},
                                {"name": "Medium", "color": "yellow"},
                                {"name": "Large", "color": "red"}
                            ]
                        }
                    },
                    "Location": {"rich_text": {}},
                    "Assignee": {"people": {}},
                    "Created": {"date": {}},
                    "Due Date": {"date": {}}
                }
            )
            
            database_id = db_response.get("id")
            if database_id:
                self.database_id = database_id
                os.environ["NOTION_DATABASE_ID"] = database_id
                self.io.tool_output(f"Created Notion database with ID: {database_id}")
                self.io.tool_output(f"Database URL: https://www.notion.so/{database_id.replace('-', '')}")
                self.io.tool_output(f"Please set this ID in your environment: NOTION_DATABASE_ID={database_id}")
                return database_id
            
            return None
            
        except APIResponseError as error:
            self.io.tool_error(f"Error creating Notion database: {error}")
            
            # Provide more details about the error
            if hasattr(error, 'body'):
                self.io.tool_error(f"API Error details: {error.body}")
            
            # Show integration guide
            self.io.tool_output("\nTo use Notion integration correctly:")
            self.io.tool_output("1. Create an integration at https://www.notion.so/my-integrations")
            self.io.tool_output("2. Copy the integration token and use it with '/notion setup --token YOUR_TOKEN'")
            self.io.tool_output("3. Make sure your integration has 'Insert content' capability enabled")
            self.io.tool_output("4. Create a page manually in Notion")
            self.io.tool_output("5. Share that page with your integration")
            self.io.tool_output("6. Use the page ID as parent for creating your database: /notion setup --create-db --page-id YOUR_PAGE_ID")
            
            return None

    def list_todos(self) -> List[Dict[str, Any]]:
        """List all TODOs from Notion database.
        
        Returns:
            List[Dict]: List of TODO items
        """
        if not self.is_ready():
            self.io.tool_error("Notion integration not ready. Check configuration.")
            return []
            
        try:
            response = self.client.databases.query(database_id=self.database_id)
            todos = []
            
            for item in response.get("results", []):
                properties = item.get("properties", {})
                
                name = self._extract_property_value(properties, "Name", "title", [])
                status = self._extract_property_value(properties, "Status", "select", {}).get("name", "")
                priority = self._extract_property_value(properties, "Priority", "select", {}).get("name", "")
                category = self._extract_property_value(properties, "Category", "select", {}).get("name", "")
                effort = self._extract_property_value(properties, "Effort", "select", {}).get("name", "")
                
                # Location could be rich_text or url
                location = ""
                if "Location" in properties:
                    if properties["Location"]["type"] == "rich_text":
                        location = self._extract_property_value(properties, "Location", "rich_text", [])
                    elif properties["Location"]["type"] == "url":
                        location = properties["Location"].get("url", "")
                
                created = self._extract_property_value(properties, "Created", "date", {})
                created_date = created.get("start", "") if created else ""
                
                due_date = self._extract_property_value(properties, "Due Date", "date", {})
                due_date_value = due_date.get("start", "") if due_date else ""
                
                todos.append({
                    "id": item.get("id"),
                    "name": name,
                    "status": status,
                    "priority": priority,
                    "category": category,
                    "effort": effort,
                    "location": location,
                    "created": created_date,
                    "due_date": due_date_value
                })
                
            return todos
            
        except APIResponseError as error:
            self.io.tool_error(f"Error listing TODOs: {error}")
            return []
            
    def _clean_select_value(self, value: str) -> str:
        """Clean a value for select fields to remove problematic characters.
        
        Args:
            value: The original value
            
        Returns:
            str: Cleaned value suitable for select fields
        """
        # For select fields, simplify to avoid API errors
        if ',' in value or '(' in value:
            # Get the first part before comma or opening parenthesis
            clean_value = value.split(',')[0].split('(')[0].strip()
            return clean_value
        return value

    def add_todo(self, name: str, status: str = "To Do", priority: str = "Medium", 
                 due_date: str = None, category: str = None, effort: str = None,
                 location: str = None, details: str = None) -> Optional[str]:
        """Add a new TODO to Notion.
        
        Args:
            name: The name/title of the TODO
            status: The status (Backlog, To Do, In Progress, Done, Cancelled)
            priority: The priority (Low, Medium, High)
            due_date: Due date in ISO format (YYYY-MM-DD)
            category: Category of the TODO, comma-separated values for multi-select
            effort: Effort estimation (Small, Medium, Large)
            location: Location/file path
            details: Additional details
            
        Returns:
            Optional[str]: The ID of the created TODO or None if failed
        """
        if not self.is_ready():
            self.io.tool_error("Notion integration not ready. Check configuration.")
            return None
            
        # Start with required properties
        properties = {
            "Name": {"title": [{"text": {"content": name}}]},
        }
        
        # Add optional properties if they exist in database
        try:
            # Try to query database properties first
            db_info = self.client.databases.retrieve(database_id=self.database_id)
            db_properties = db_info.get("properties", {})
            
            # Add Status if it exists
            if "Status" in db_properties and status:
                prop_type = db_properties["Status"]["type"]
                if prop_type == "select":
                    properties["Status"] = {"select": {"name": status}}
                elif prop_type == "rich_text":
                    properties["Status"] = {"rich_text": [{"text": {"content": status}}]}
            
            # Add Priority if it exists
            if "Priority" in db_properties and priority:
                prop_type = db_properties["Priority"]["type"]
                if prop_type == "select":
                    properties["Priority"] = {"select": {"name": priority}}
                elif prop_type == "rich_text":
                    properties["Priority"] = {"rich_text": [{"text": {"content": priority}}]}
            
            # Add Category if it exists
            if "Category" in db_properties and category:
                prop_type = db_properties["Category"]["type"]
                if prop_type == "select":
                    # For single select, use first category if comma-separated
                    if ',' in category:
                        first_category = category.split(',')[0].strip()
                        properties["Category"] = {"select": {"name": first_category}}
                    else:
                        properties["Category"] = {"select": {"name": category}}
                elif prop_type == "multi_select":
                    # For multi-select, split by comma and add each as an option
                    multi_categories = []
                    for cat in category.split(','):
                        cat = cat.strip()
                        if cat:
                            multi_categories.append({"name": cat})
                    properties["Category"] = {"multi_select": multi_categories}
                elif prop_type == "rich_text":
                    properties["Category"] = {"rich_text": [{"text": {"content": category}}]}
            
            # Add Effort if it exists
            if "Effort" in db_properties and effort:
                prop_type = db_properties["Effort"]["type"]
                if prop_type == "select":
                    # Clean the effort value for select field
                    clean_effort = self._clean_select_value(effort)
                    properties["Effort"] = {"select": {"name": clean_effort}}
                elif prop_type == "multi_select":
                    # For multi-select, handle complex parsing with parentheses
                    multi_efforts = []
                    # First try to split by comma not inside parentheses
                    import re
                    # Simple pattern to extract main effort values
                    effort_values = [e.strip() for e in re.split(r',\s*(?![^()]*\))', effort)]
                    
                    for eff in effort_values:
                        eff = eff.strip()
                        if eff:
                            # Further clean each value for multi-select
                            if '(' in eff and not eff.endswith(')'):
                                eff = eff.split('(')[0].strip()
                            multi_efforts.append({"name": eff})
                    properties["Effort"] = {"multi_select": multi_efforts}
                elif prop_type == "rich_text":
                    properties["Effort"] = {"rich_text": [{"text": {"content": effort}}]}
            
            # Add Location if it exists
            if "Location" in db_properties and location:
                prop_type = db_properties["Location"]["type"]
                if prop_type == "rich_text":
                    properties["Location"] = {"rich_text": [{"text": {"content": location}}]}
                elif prop_type == "url":
                    properties["Location"] = {"url": location}
            
            # Add Details if it exists (might be in rich_text or other formats)
            if "Details" in db_properties and details:
                prop_type = db_properties["Details"]["type"]
                if prop_type == "rich_text":
                    properties["Details"] = {"rich_text": [{"text": {"content": details}}]}
                
            # Check if Created property exists
            if "Created" in db_properties and db_properties["Created"]["type"] == "date":
                properties["Created"] = {"date": {"start": datetime.datetime.now().date().isoformat()}}
                
            # Check if Due Date property exists
            if due_date and "Due Date" in db_properties and db_properties["Due Date"]["type"] == "date":
                properties["Due Date"] = {"date": {"start": due_date}}
                
        except APIResponseError as error:
            self.io.tool_warning(f"Could not verify database properties: {error}")
            # If we can't verify, take a best guess with required properties only
        
        try:
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            return response.get("id")
            
        except APIResponseError as error:
            self.io.tool_error(f"Error adding TODO: {error}")
            return None
            
    def update_todo(self, todo_id: str, **kwargs) -> bool:
        """Update a TODO item.
        
        Args:
            todo_id: The ID of the TODO to update
            **kwargs: Fields to update (name, status, priority, category, effort, location, due_date, details)
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        if not self.is_ready():
            self.io.tool_error("Notion integration not ready. Check configuration.")
            return False
            
        properties = {}
        
        try:
            # Query database properties to know what we can use
            db_info = self.client.databases.retrieve(database_id=self.database_id)
            db_properties = db_info.get("properties", {})
            
            if "name" in kwargs:
                properties["Name"] = {"title": [{"text": {"content": kwargs["name"]}}]}
                
            if "status" in kwargs and "Status" in db_properties:
                prop_type = db_properties["Status"]["type"]
                if prop_type == "select":
                    properties["Status"] = {"select": {"name": kwargs["status"]}}
                elif prop_type == "rich_text":
                    properties["Status"] = {"rich_text": [{"text": {"content": kwargs["status"]}}]}
                
            if "priority" in kwargs and "Priority" in db_properties:
                prop_type = db_properties["Priority"]["type"]
                if prop_type == "select":
                    properties["Priority"] = {"select": {"name": kwargs["priority"]}}
                elif prop_type == "rich_text":
                    properties["Priority"] = {"rich_text": [{"text": {"content": kwargs["priority"]}}]}
                
            if "category" in kwargs and "Category" in db_properties:
                category = kwargs["category"]
                prop_type = db_properties["Category"]["type"]
                if prop_type == "select":
                    # For single select, use first category if comma-separated
                    if ',' in category:
                        first_category = category.split(',')[0].strip()
                        properties["Category"] = {"select": {"name": first_category}}
                    else:
                        properties["Category"] = {"select": {"name": category}}
                elif prop_type == "multi_select":
                    # For multi-select, split by comma and add each as an option
                    multi_categories = []
                    for cat in category.split(','):
                        cat = cat.strip()
                        if cat:
                            multi_categories.append({"name": cat})
                    properties["Category"] = {"multi_select": multi_categories}
                elif prop_type == "rich_text":
                    properties["Category"] = {"rich_text": [{"text": {"content": category}}]}
                
            if "effort" in kwargs and "Effort" in db_properties:
                effort = kwargs["effort"]
                prop_type = db_properties["Effort"]["type"] 
                if prop_type == "select":
                    # Clean the effort value for select field
                    clean_effort = self._clean_select_value(effort)
                    properties["Effort"] = {"select": {"name": clean_effort}}
                elif prop_type == "multi_select":
                    # For multi-select, handle complex parsing with parentheses
                    multi_efforts = []
                    # First try to split by comma not inside parentheses
                    import re
                    # Simple pattern to extract main effort values
                    effort_values = [e.strip() for e in re.split(r',\s*(?![^()]*\))', effort)]
                    
                    for eff in effort_values:
                        eff = eff.strip()
                        if eff:
                            # Further clean each value for multi-select
                            if '(' in eff and not eff.endswith(')'):
                                eff = eff.split('(')[0].strip()
                            multi_efforts.append({"name": eff})
                    properties["Effort"] = {"multi_select": multi_efforts}
                elif prop_type == "rich_text":
                    properties["Effort"] = {"rich_text": [{"text": {"content": effort}}]}
                
            if "location" in kwargs and "Location" in db_properties:
                prop_type = db_properties["Location"]["type"]
                if prop_type == "rich_text":
                    properties["Location"] = {"rich_text": [{"text": {"content": kwargs["location"]}}]}
                elif prop_type == "url":
                    properties["Location"] = {"url": kwargs["location"]}
                
            if "details" in kwargs and "Details" in db_properties:
                prop_type = db_properties["Details"]["type"]
                if prop_type == "rich_text":
                    properties["Details"] = {"rich_text": [{"text": {"content": kwargs["details"]}}]}
                
            if "due_date" in kwargs and "Due Date" in db_properties:
                properties["Due Date"] = {"date": {"start": kwargs["due_date"]}}
                
        except APIResponseError as error:
            self.io.tool_warning(f"Could not verify database properties: {error}")
            # If we can't verify, fall back to simpler approach
            
            if "name" in kwargs:
                properties["Name"] = {"title": [{"text": {"content": kwargs["name"]}}]}
                
            if "status" in kwargs:
                properties["Status"] = {"select": {"name": kwargs["status"]}}
                
            if "priority" in kwargs:
                properties["Priority"] = {"select": {"name": kwargs["priority"]}}
                
            if "due_date" in kwargs:
                properties["Due Date"] = {"date": {"start": kwargs["due_date"]}}
            
        if not properties:
            return True  # Nothing to update
            
        try:
            self.client.pages.update(page_id=todo_id, properties=properties)
            return True
            
        except APIResponseError as error:
            self.io.tool_error(f"Error updating TODO: {error}")
            return False
            
    def delete_todo(self, todo_id: str) -> bool:
        """Delete/Archive a TODO item.
        
        Args:
            todo_id: The ID of the TODO to delete
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        if not self.is_ready():
            self.io.tool_error("Notion integration not ready. Check configuration.")
            return False
            
        try:
            # Notion API doesn't have a true delete, we archive the page
            self.client.pages.update(page_id=todo_id, archived=True)
            return True
            
        except APIResponseError as error:
            self.io.tool_error(f"Error deleting TODO: {error}")
            return False
            
    def _extract_property_value(self, properties, property_name, property_type, default):
        """Extract value from a Notion property.
        
        Args:
            properties: The properties object from Notion API
            property_name: The name of the property
            property_type: The type of the property
            default: Default value if property doesn't exist
            
        Returns:
            The extracted property value or default
        """
        prop = properties.get(property_name, {})
        
        # Special handling for title properties
        if property_type == "title":
            title_array = prop.get(property_type, [])
            if title_array and isinstance(title_array, list):
                # Combine all text content from the title array
                return ''.join(item.get("plain_text", "") 
                              for item in title_array if isinstance(item, dict))
            return default
        
        return prop.get(property_type, default)
            
    def import_todos_from_file(self, file_path: str) -> bool:
        """Import TODOs from a markdown file to Notion.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            bool: True if import was successful, False otherwise
        """
        if not self.is_ready():
            self.io.tool_error("Notion integration not ready. Check configuration.")
            return False
            
        try:
            path = Path(file_path)
            if not path.exists():
                self.io.tool_error(f"File not found: {file_path}")
                return False
                
            content = path.read_text(encoding='utf-8')
            
            # Simple parsing of markdown TODOs
            # Assumes format: - [ ] TODO item or # TODO: item
            todos = []
            
            # More sophisticated parsing for code review TODOs with metadata
            in_todo_item = False
            current_todo = {}
            
            for line in content.split('\n'):
                line = line.strip()
                
                # Check for markdown task format: - [ ] Task description
                if line.startswith('- [ ]'):
                    # If we were processing a previous task, add it to the list
                    if in_todo_item and current_todo.get("name"):
                        todos.append(current_todo)
                        current_todo = {}
                        
                    in_todo_item = True
                    task = line[5:].strip()
                    
                    # Extract metadata if this is a code review TODO
                    if "**Issue**:" in task:
                        current_todo["name"] = task.split("**Issue**:", 1)[1].strip()
                    else:
                        current_todo = {"name": task, "status": "To Do"}
                
                # Extract other metadata fields if we're in a todo item
                elif in_todo_item:
                    if "**Location**:" in line:
                        current_todo["location"] = line.split("**Location**:", 1)[1].strip()
                    elif "**Priority**:" in line:
                        current_todo["priority"] = line.split("**Priority**:", 1)[1].strip()
                    elif "**Category**:" in line:
                        current_todo["category"] = line.split("**Category**:", 1)[1].strip()
                    elif "**Effort**:" in line:
                        current_todo["effort"] = line.split("**Effort**:", 1)[1].strip()
                    elif "**Details**:" in line:
                        current_todo["details"] = line.split("**Details**:", 1)[1].strip()
                    # Empty line or new task could signal end of current todo
                    elif not line or line.startswith('- [ ]'):
                        if current_todo.get("name"):
                            todos.append(current_todo)
                            current_todo = {}
                            in_todo_item = False
                
                # Check for heading format: # TODO: Task description
                elif '# TODO:' in line or line.startswith('TODO:'):
                    task = line.split('TODO:', 1)[1].strip()
                    todos.append({"name": task, "status": "To Do"})
            
            # Add the last todo if we were processing one
            if in_todo_item and current_todo.get("name"):
                todos.append(current_todo)
                    
            if not todos:
                self.io.tool_output(f"No TODOs found in file: {file_path}")
                return True
                
            # Query database properties once to know what we can use
            db_properties = {}
            try:
                db_info = self.client.databases.retrieve(database_id=self.database_id)
                db_properties = db_info.get("properties", {})
            except APIResponseError as error:
                self.io.tool_warning(f"Could not verify database properties: {error}")
            
            # Add TODOs to Notion
            success_count = 0
            for todo in todos:
                try:
                    # Prepare properties based on available database schema
                    properties = {
                        "Name": {"title": [{"text": {"content": todo.get("name", "Unnamed TODO")}}]},
                    }
                    
                    # Add Status if it exists
                    if "Status" in db_properties:
                        prop_type = db_properties["Status"]["type"]
                        status = todo.get("status", "To Do")
                        if prop_type == "select":
                            properties["Status"] = {"select": {"name": status}}
                        elif prop_type == "rich_text":
                            properties["Status"] = {"rich_text": [{"text": {"content": status}}]}
                    
                    # Add Priority if it exists
                    if "Priority" in db_properties and "priority" in todo:
                        prop_type = db_properties["Priority"]["type"]
                        if prop_type == "select":
                            properties["Priority"] = {"select": {"name": todo["priority"]}}
                        elif prop_type == "rich_text":
                            properties["Priority"] = {"rich_text": [{"text": {"content": todo["priority"]}}]}
                    
                    # Add Category if it exists
                    if "Category" in db_properties and "category" in todo:
                        category = todo["category"]
                        prop_type = db_properties["Category"]["type"]
                        if prop_type == "select":
                            # For single select, use first category if comma-separated
                            if ',' in category:
                                first_category = category.split(',')[0].strip()
                                properties["Category"] = {"select": {"name": first_category}}
                            else:
                                properties["Category"] = {"select": {"name": category}}
                        elif prop_type == "multi_select":
                            # For multi-select, split by comma and add each as an option
                            multi_categories = []
                            for cat in category.split(','):
                                cat = cat.strip()
                                if cat:
                                    multi_categories.append({"name": cat})
                            properties["Category"] = {"multi_select": multi_categories}
                        elif prop_type == "rich_text":
                            properties["Category"] = {"rich_text": [{"text": {"content": category}}]}
                    
                    # Add Effort if it exists
                    if "Effort" in db_properties and "effort" in todo:
                        effort = todo["effort"]
                        prop_type = db_properties["Effort"]["type"]
                        if prop_type == "select":
                            # Clean the effort value for select field
                            clean_effort = self._clean_select_value(effort)
                            properties["Effort"] = {"select": {"name": clean_effort}}
                        elif prop_type == "multi_select":
                            # For multi-select, handle complex parsing with parentheses
                            multi_efforts = []
                            # First try to split by comma not inside parentheses
                            import re
                            # Simple pattern to extract main effort values
                            effort_values = [e.strip() for e in re.split(r',\s*(?![^()]*\))', effort)]
                            
                            for eff in effort_values:
                                eff = eff.strip()
                                if eff:
                                    # Further clean each value for multi-select
                                    if '(' in eff and not eff.endswith(')'):
                                        eff = eff.split('(')[0].strip()
                                    multi_efforts.append({"name": eff})
                            properties["Effort"] = {"multi_select": multi_efforts}
                        elif prop_type == "rich_text":
                            properties["Effort"] = {"rich_text": [{"text": {"content": effort}}]}
                    
                    # Add Location if it exists
                    if "Location" in db_properties and "location" in todo:
                        prop_type = db_properties["Location"]["type"]
                        if prop_type == "rich_text":
                            properties["Location"] = {"rich_text": [{"text": {"content": todo["location"]}}]}
                        elif prop_type == "url":
                            properties["Location"] = {"url": todo["location"]}
                    
                    # Add Details if it exists
                    if "Details" in db_properties and "details" in todo:
                        prop_type = db_properties["Details"]["type"]
                        if prop_type == "rich_text":
                            properties["Details"] = {"rich_text": [{"text": {"content": todo["details"]}}]}
                    
                    # Add Created date if it exists
                    if "Created" in db_properties and db_properties["Created"]["type"] == "date":
                        properties["Created"] = {"date": {"start": datetime.datetime.now().date().isoformat()}}
                    
                    # Create the page
                    self.client.pages.create(
                        parent={"database_id": self.database_id},
                        properties=properties
                    )
                    success_count += 1
                except APIResponseError as error:
                    self.io.tool_error(f"Error adding TODO: {error}")
                
            self.io.tool_output(f"Imported {success_count} TODOs from {file_path}")
            return success_count > 0
            
        except Exception as e:
            self.io.tool_error(f"Error importing TODOs: {e}")
            return False
            
    def export_todos_to_file(self, file_path: str) -> bool:
        """Export TODOs from Notion to a markdown file.
        
        Args:
            file_path: Path to save the markdown file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        if not self.is_ready():
            self.io.tool_error("Notion integration not ready. Check configuration.")
            return False
            
        todos = self.list_todos()
        if not todos:
            self.io.tool_output("No TODOs to export")
            return True
            
        try:
            content = "# Exported TODOs from Notion\n\n"
            content += f"*Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            
            # Group by status
            status_groups = {}
            for todo in todos:
                status = todo.get("status") or "No Status"
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(todo)
            
            # Generate markdown
            for status, items in status_groups.items():
                content += f"## {status}\n\n"
                for item in items:
                    checkbox = 'x' if status == 'Done' else ' '
                    content += f"- [{checkbox}] {item.get('name', 'Unnamed TODO')}\n"
                    
                    # Add metadata with formatting
                    if item.get("category"):
                        content += f"  - **Category**: {item['category']}\n"
                    if item.get("priority"):
                        content += f"  - **Priority**: {item['priority']}\n"
                    if item.get("effort"):
                        content += f"  - **Effort**: {item['effort']}\n"
                    if item.get("location"):
                        content += f"  - **Location**: {item['location']}\n"
                    if item.get("due_date"):
                        content += f"  - **Due Date**: {item['due_date']}\n"
                    
                    content += "\n"
                
            # Save to file
            path = Path(file_path)
            path.write_text(content, encoding='utf-8')
            
            self.io.tool_output(f"Exported {len(todos)} TODOs to {file_path}")
            return True
            
        except Exception as e:
            self.io.tool_error(f"Error exporting TODOs: {e}")
            return False 