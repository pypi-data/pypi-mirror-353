"""
Command implementation for Notion integration.
"""

import argparse
import os
import shlex
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from .notion_integration import NotionIntegration


class NotionCommand:
    """Command class for Notion integration."""
    
    def __init__(self, io, coder):
        """Initialize the Notion command.
        
        Args:
            io: The IO interface for interacting with the user.
            coder: The Coder instance for accessing repository information.
        """
        self.io = io
        self.coder = coder
        self.notion = NotionIntegration(io, coder)
        
    def execute(self, args: str = "") -> None:
        """Execute the Notion command.
        
        Args:
            args: The command arguments.
        """
        # Parse arguments while respecting quoted strings
        try:
            parts = shlex.split(args)
        except ValueError as e:
            self.io.tool_error(f"Error parsing arguments: {e}")
            self._show_help()
            return
            
        if not parts:
            self._show_help()
            return
            
        subcommand = parts[0].lower()
        
        # Handle subcommands
        if subcommand == "setup":
            self._handle_setup(parts[1:])
        elif subcommand == "status":
            self._handle_status()
        elif subcommand == "list":
            self._handle_list()
        elif subcommand == "add":
            self._handle_add(parts[1:])
        elif subcommand == "update":
            self._handle_update(parts[1:])
        elif subcommand == "delete":
            self._handle_delete(parts[1:])
        elif subcommand == "import":
            self._handle_import(parts[1:])
        elif subcommand == "export":
            self._handle_export(parts[1:])
        elif subcommand == "help":
            self._show_help()
        else:
            self.io.tool_error(f"Unknown subcommand: {subcommand}")
            self._show_help()
    
    def _handle_setup(self, args: List[str]) -> None:
        """Handle setup subcommand.
        
        Args:
            args: The subcommand arguments.
        """
        token = None
        database_id = None
        create_db = False
        db_title = "Codecraft TODOs"
        parent_page_id = None
        
        # Parse named arguments
        i = 0
        while i < len(args):
            if args[i] == "--token" and i + 1 < len(args):
                token = args[i + 1]
                i += 2
            elif args[i] == "--database-id" and i + 1 < len(args):
                database_id = args[i + 1]
                i += 2
            elif args[i] == "--create-db":
                create_db = True
                i += 1
            elif args[i] == "--db-title" and i + 1 < len(args):
                db_title = args[i + 1]
                i += 2
            elif args[i] == "--page-id" and i + 1 < len(args):
                parent_page_id = args[i + 1]
                i += 2
            else:
                self.io.tool_error(f"Unknown setup argument: {args[i]}")
                return
                
        if not token and not database_id and not create_db:
            # Interactive setup flow
            self.io.tool_output("Starting Notion integration setup...")
            
            # Step 1: Token
            if not self.notion.token:
                self.io.tool_output("\nStep 1: Notion API Token")
                self.io.tool_output("Create an integration at https://www.notion.so/my-integrations")
                self.io.tool_output("Copy your 'Internal Integration Token'")
                self.io.tool_output("Run: /notion setup --token YOUR_TOKEN")
                return
                
            # If we have a token but no database, guide to creating one
            if not self.notion.database_id:
                self.io.tool_output("\nStep 2: Notion Database")
                self.io.tool_output("Option 1: Connect to existing database")
                self.io.tool_output("1. Create a database in Notion with these properties:")
                self.io.tool_output("   - Name (Title)")
                self.io.tool_output("   - Status (Select: Backlog, To Do, In Progress, Done)")
                self.io.tool_output("   - Priority (Select: Low, Medium, High)")
                self.io.tool_output("   - Category (Multi-select)")
                self.io.tool_output("   - Effort (Select or Multi-select)")
                self.io.tool_output("2. Share your database with the integration")
                self.io.tool_output("3. Copy the database ID from the URL")
                self.io.tool_output("   Format: https://www.notion.so/workspace/DATABASE_ID?...")
                self.io.tool_output("Run: /notion setup --database-id YOUR_DATABASE_ID")
                self.io.tool_output("\nOption 2: Create a new database")
                self.io.tool_output("1. Create a page in Notion where you want the database to be created")
                self.io.tool_output("2. Share the page with your integration")
                self.io.tool_output("3. Get the page ID from the URL:")
                self.io.tool_output("   Format: https://www.notion.so/PAGE_ID?...")
                self.io.tool_output("Run: /notion setup --create-db --page-id YOUR_PAGE_ID [--db-title \"My Custom Title\"]")
                return
        
        # First setup with token if provided
        if token:
            token_success = self.notion.setup(token=token)
            if not token_success:
                self.io.tool_error("Failed to setup Notion with the provided token.")
                return
                
        # If we need to create a database
        if create_db:
            # Make sure we have a token first
            if not self.notion.token:
                self.io.tool_error("Notion token is required to create a database.")
                self.io.tool_output("Run: /notion setup --token YOUR_TOKEN first")
                return
            
            if not parent_page_id:
                self.io.tool_error("Parent page ID is required to create a database.")
                self.io.tool_output("You need to specify where to create the database:")
                self.io.tool_output("1. Create a page in Notion where you want the database to be created")
                self.io.tool_output("2. Share that page with your integration")
                self.io.tool_output("3. Get the page ID from the URL: https://www.notion.so/PAGE_ID?...")
                self.io.tool_output("Run: /notion setup --create-db --page-id YOUR_PAGE_ID [--db-title \"My Custom Title\"]")
                
                # Ask user if they want to enter a page ID now
                parent_page_id = self.io.prompt_ask("Enter a Notion page ID where the database should be created (or press Enter to skip):")
                if not parent_page_id:
                    return
                
            self.io.tool_output(f"Creating new Notion database with title: {db_title}")
            db_id = self.notion.create_kanban_database(title=db_title, parent_page_id=parent_page_id)
            if db_id:
                database_id = db_id  # Use this database ID for final setup
                self.io.tool_output(f"Successfully created database with ID: {db_id}")
                self.io.tool_output(f"You can access your database at: https://www.notion.so/{db_id.replace('-', '')}")
            else:
                self.io.tool_error("Failed to create Notion database")
                self.io.tool_output("Make sure your integration has 'Insert content' capability enabled:")
                self.io.tool_output("1. Go to https://www.notion.so/my-integrations")
                self.io.tool_output("2. Select your integration")
                self.io.tool_output("3. Ensure 'Insert content' capability is turned ON")
                self.io.tool_output("4. Also make sure you've shared the parent page with your integration")
                return
        
        # Final setup with database ID
        if database_id:
            db_success = self.notion.setup(database_id=database_id)
            if db_success:
                self.io.tool_output("Notion integration setup complete!")
                self.notion.display_readiness_status()
            else:
                self.io.tool_error("Failed to setup Notion with the provided database ID.")
                self.notion.display_readiness_status()
        elif token:
            # Only token was provided, show readiness status
            self.io.tool_output("Token setup complete. Now you need to set up a database.")
            self.notion.display_readiness_status()

    def _handle_status(self) -> None:
        """Handle status subcommand."""
        self.io.tool_output("Notion Integration Status:")
        self.notion.display_readiness_status()

    def _handle_list(self) -> None:
        """Handle list subcommand."""
        if not self._check_ready():
            return
            
        self.io.tool_output("Fetching TODOs from Notion...")
        todos = self.notion.list_todos()
        
        if not todos:
            self.io.tool_output("No TODOs found in Notion database.")
            return
            
        self.io.tool_output(f"Found {len(todos)} TODOs:")
        
        # Group by status
        by_status = {}
        for todo in todos:
            status = todo.get("status") or "No Status"
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(todo)
            
        # Display TODOs grouped by status
        for status, items in by_status.items():
            self.io.tool_output(f"\n## {status} ({len(items)})")
            for todo in items:
                name = todo.get("name", "Untitled")
                priority = f" [Priority: {todo.get('priority')}]" if todo.get("priority") else ""
                category = f" [Category: {todo.get('category')}]" if todo.get("category") else ""
                due = f" (Due: {todo.get('due_date')})" if todo.get("due_date") else ""
                self.io.tool_output(f"- {name}{priority}{category}{due}")
                
                # Add effort and location on next line if available
                details = []
                if todo.get("effort"):
                    details.append(f"Effort: {todo.get('effort')}")
                if todo.get("location"):
                    details.append(f"Location: {todo.get('location')}")
                    
                if details:
                    self.io.tool_output(f"  {', '.join(details)}")
        
    def _handle_add(self, args: List[str]) -> None:
        """Handle add subcommand.
        
        Args:
            args: The subcommand arguments.
        """
        if not self._check_ready():
            return
            
        if not args:
            self.io.tool_error("No TODO name specified.")
            return
            
        name = args[0]
        status = "To Do"
        priority = "Medium"
        category = None
        effort = None
        location = None
        due_date = None
        
        # Parse named arguments
        i = 1
        while i < len(args):
            if args[i] == "--status" and i + 1 < len(args):
                status = args[i + 1]
                i += 2
            elif args[i] == "--priority" and i + 1 < len(args):
                priority = args[i + 1]
                i += 2
            elif args[i] == "--category" and i + 1 < len(args):
                category = args[i + 1]
                i += 2
            elif args[i] == "--effort" and i + 1 < len(args):
                effort = args[i + 1]
                i += 2
            elif args[i] == "--location" and i + 1 < len(args):
                location = args[i + 1]
                i += 2
            elif args[i] == "--due" and i + 1 < len(args):
                due_date = args[i + 1]
                i += 2
            else:
                self.io.tool_error(f"Unknown add argument: {args[i]}")
                return
        
        self.io.tool_output(f"Adding TODO: {name}")
        todo_id = self.notion.add_todo(
            name=name, 
            status=status, 
            priority=priority,
            category=category,
            effort=effort,
            location=location,
            due_date=due_date
        )
        
        if todo_id:
            self.io.tool_output(f"Successfully added TODO with ID: {todo_id}")
        else:
            self.io.tool_error("Failed to add TODO.")
            
    def _handle_update(self, args: List[str]) -> None:
        """Handle update subcommand.
        
        Args:
            args: The subcommand arguments.
        """
        if not self._check_ready():
            return
            
        if not args:
            self.io.tool_error("No TODO ID specified.")
            return
            
        todo_id = args[0]
        updates = {}
        
        # Parse named arguments
        i = 1
        while i < len(args):
            if args[i] == "--name" and i + 1 < len(args):
                updates["name"] = args[i + 1]
                i += 2
            elif args[i] == "--status" and i + 1 < len(args):
                updates["status"] = args[i + 1]
                i += 2
            elif args[i] == "--priority" and i + 1 < len(args):
                updates["priority"] = args[i + 1]
                i += 2
            elif args[i] == "--category" and i + 1 < len(args):
                updates["category"] = args[i + 1]
                i += 2
            elif args[i] == "--effort" and i + 1 < len(args):
                updates["effort"] = args[i + 1]
                i += 2
            elif args[i] == "--location" and i + 1 < len(args):
                updates["location"] = args[i + 1]
                i += 2
            elif args[i] == "--due" and i + 1 < len(args):
                updates["due_date"] = args[i + 1]
                i += 2
            else:
                self.io.tool_error(f"Unknown update argument: {args[i]}")
                return
                
        if not updates:
            self.io.tool_error("No updates specified.")
            return
            
        self.io.tool_output(f"Updating TODO: {todo_id}")
        success = self.notion.update_todo(todo_id, **updates)
        
        if success:
            self.io.tool_output(f"Successfully updated TODO: {todo_id}")
        else:
            self.io.tool_error(f"Failed to update TODO: {todo_id}")
            
    def _handle_delete(self, args: List[str]) -> None:
        """Handle delete subcommand.
        
        Args:
            args: The subcommand arguments.
        """
        if not self._check_ready():
            return
            
        if not args:
            self.io.tool_error("No TODO ID specified.")
            return
            
        todo_id = args[0]
        self.io.tool_output(f"Deleting TODO: {todo_id}")
        success = self.notion.delete_todo(todo_id)
        
        if success:
            self.io.tool_output(f"Successfully deleted TODO: {todo_id}")
        else:
            self.io.tool_error(f"Failed to delete TODO: {todo_id}")
            
    def _handle_import(self, args: List[str]) -> None:
        """Handle import subcommand.
        
        Args:
            args: The subcommand arguments.
        """
        if not self._check_ready():
            return
            
        if not args:
            self.io.tool_error("No file path specified.")
            return
            
        file_path = args[0]
        self.io.tool_output(f"Importing TODOs from: {file_path}")
        success = self.notion.import_todos_from_file(file_path)
        
        if success:
            self.io.tool_output(f"Successfully imported TODOs from {file_path}")
        else:
            self.io.tool_error(f"Failed to import TODOs from {file_path}")
            
    def _handle_export(self, args: List[str]) -> None:
        """Handle export subcommand.
        
        Args:
            args: The subcommand arguments.
        """
        if not self._check_ready():
            return
            
        file_path = f"notion_todos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        if args:
            file_path = args[0]
            
        self.io.tool_output(f"Exporting TODOs to: {file_path}")
        success = self.notion.export_todos_to_file(file_path)
        
        if success:
            self.io.tool_output(f"Successfully exported TODOs to {file_path}")
        else:
            self.io.tool_error(f"Failed to export TODOs to {file_path}")
            
    def _show_help(self) -> None:
        """Show help information."""
        self.io.tool_output("Notion Integration Commands:\n")
        self.io.tool_output("Setup/Status:")
        self.io.tool_output("  /notion setup")
        self.io.tool_output("  /notion setup --token TOKEN --database-id DB_ID")
        self.io.tool_output("  /notion setup --create-db --page-id PAGE_ID [--db-title \"My Custom Title\"]")
        self.io.tool_output("  /notion status\n")
        
        self.io.tool_output("Managing TODOs:")
        self.io.tool_output('  /notion list')
        self.io.tool_output('  /notion add "Fix login bug" [--status "To Do"] [--priority "High"] [--category "Bug,Frontend"] [--effort "Medium"] [--location "src/auth.js"] [--due "2023-12-31"]')
        self.io.tool_output('  /notion update ID [--name "Updated name"] [--status "In Progress"]')
        self.io.tool_output('  /notion delete ID\n')
        
        self.io.tool_output("Import/Export:")
        self.io.tool_output("  /notion import TODO.md")
        self.io.tool_output("  /notion export [filename.md]\n")
        
        self.io.tool_output("Help:")
        self.io.tool_output("  /notion help")
        
    def _check_ready(self) -> bool:
        """Check if Notion integration is ready.
        
        Returns:
            bool: True if ready, False otherwise.
        """
        if not self.notion.is_ready():
            self.io.tool_error("Notion integration is not properly configured.")
            self.io.tool_output("Run /notion setup to configure Notion integration.")
            return False
        return True

    def _install_notion_client(self) -> None:
        """Install the notion-client package."""
        import subprocess
        import sys
        
        self.io.tool_output("Installing notion-client package...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "notion-client"])
            self.io.tool_output("notion-client installed successfully!")
        except subprocess.CalledProcessError as e:
            self.io.tool_error(f"Failed to install notion-client: {e}")
    
    def _setup_notion(self, token: str = None, database_id: str = None) -> None:
        """Set up the Notion integration.
        
        Args:
            token: Notion API token
            database_id: Notion database ID
        """
        self.io.tool_output("\n== Notion Integration Setup ==")
        
        if token:
            os.environ["NOTION_TOKEN"] = token
            self.io.tool_output("✓ Notion API token set!")
        else:
            token = os.environ.get("NOTION_TOKEN")
            if not token:
                # Use prompt_ask instead of input_ask
                self.io.tool_output("To set up Notion integration, you need an API token.")
                self.io.tool_output("1. Go to https://www.notion.so/my-integrations")
                self.io.tool_output("2. Click '+ New integration'")
                self.io.tool_output("3. Give it a name and select your workspace")
                self.io.tool_output("4. Copy the 'Internal Integration Token'")
                
                token = self.io.prompt_ask("Enter your Notion API token:")
                if token:
                    os.environ["NOTION_TOKEN"] = token
                    self.io.tool_output("✓ Notion API token set!")
                else:
                    self.io.tool_error("✗ No token provided. Setup aborted.")
                    return
        
        # Re-initialize the client with the new token
        self.notion = NotionIntegration(self.io, self.coder)
        
        if not self.notion.client:
            self.io.tool_error("✗ Failed to initialize Notion client with the provided token.")
            return
            
        if database_id:
            os.environ["NOTION_DATABASE_ID"] = database_id
            self.io.tool_output("✓ Notion database ID set!")
            self.notion.database_id = database_id
            
            # Verify the database is accessible
            try:
                # Try to query the database to verify access
                self.io.tool_output("Verifying database access...")
                self.notion.client.databases.retrieve(database_id=database_id)
                self.io.tool_output("✓ Successfully connected to the database!")
            except Exception as e:
                self.io.tool_error(f"✗ Error accessing database: {e}")
                self.io.tool_output("Make sure you've shared the database with your integration.")
                self.io.tool_output("In Notion, go to the database, click 'Share', and add your integration.")
                return
        elif not os.environ.get("NOTION_DATABASE_ID"):
            self._show_database_setup_instructions()
            return
                
        # Display final status
        if self.notion.is_ready():
            self.io.tool_output("\n✓ Notion integration is ready to use!")
            self.io.tool_output("Try: /notion list")
        else:
            self.io.tool_output("\nSetup is incomplete. Run '/notion status' to check what's missing.")
    
    def _show_database_setup_instructions(self):
        """Show detailed instructions for setting up a Notion database."""
        self.io.tool_output("\n== Notion Database Setup ==")
        self.io.tool_output("\nOption 1: Automatic Database Creation")
        self.io.tool_output("Create a database automatically with:")
        self.io.tool_output("   > /notion setup --create-db [--db-title \"My Custom Database\"]")
        
        self.io.tool_output("\nOption 2: Manual Database Setup")
        self.io.tool_output("1. Create a database in Notion:")
        self.io.tool_output("   a. Open Notion and create a new page")
        self.io.tool_output("   b. Type '/database' and select 'Table - Full page'")
        self.io.tool_output("   c. Click 'Create a database'")
        
        self.io.tool_output("\n2. Add the required properties to your database:")
        self.io.tool_output("   a. Keep the default 'Name' property for task names")
        self.io.tool_output("   b. Add a 'Status' property as a 'Select' type with options:")
        self.io.tool_output("      - Backlog, To Do, In Progress, Done, Cancelled")
        self.io.tool_output("   c. Add a 'Priority' property as a 'Select' type with options:")
        self.io.tool_output("      - Low, Medium, High")
        self.io.tool_output("   d. Add 'Due Date' property as a 'Date' type")
        
        self.io.tool_output("\n3. Share the database with your integration:")
        self.io.tool_output("   a. Click 'Share' in the top-right corner")
        self.io.tool_output("   b. In the 'Add people, groups, or integrations' field,")
        self.io.tool_output("      find and select your integration name")
        self.io.tool_output("   c. Ensure it has full edit access")
        
        self.io.tool_output("\n4. Get the database ID:")
        self.io.tool_output("   a. Open the database in your browser")
        self.io.tool_output("   b. Look at the URL - it will look like:")
        self.io.tool_output("      https://www.notion.so/workspace/LONG-UUID-HERE?...")
        self.io.tool_output("   c. The database ID is that long UUID part")
        
        self.io.tool_output("\n5. Set the database ID in Codecraft:")
        self.io.tool_output("   > /notion setup --database-id YOUR_DATABASE_ID")
        
        # Ask if they'd like to create a database automatically
        if self.io.confirm_ask("\nWould you like to create a database automatically?", default="y"):
            title = self.io.prompt_ask("Enter a title for your database (press Enter for default):")
            if not title:
                title = "Codecraft TODOs"
            self.io.tool_output(f"\nCreating database with title: {title}...")
            db_id = self.notion.create_kanban_database(title=title)
            if db_id:
                os.environ["NOTION_DATABASE_ID"] = db_id
                self.notion.database_id = db_id
                self.io.tool_output(f"✓ Successfully created database with ID: {db_id}")
                
                # Display final status
                if self.notion.is_ready():
                    self.io.tool_output("\n✓ Notion integration is fully configured and ready to use!")
                    self.io.tool_output("Try: /notion list")
            else:
                # If automatic creation failed, continue with manual setup
                self.io.tool_error("✗ Failed to create database automatically.")
                self._ask_for_manual_database_id()
        else:
            self._ask_for_manual_database_id()
            
    def _ask_for_manual_database_id(self):
        """Ask for manual database ID input"""
        # Ask if they want to enter a database ID manually
        if self.io.confirm_ask("\nWould you like to enter a database ID manually?", default="y"):
            database_id = self.io.prompt_ask("Enter your Notion database ID:")
            if database_id:
                os.environ["NOTION_DATABASE_ID"] = database_id
                self.notion.database_id = database_id
                self.io.tool_output("✓ Notion database ID set!")
                
                # Verify the database is accessible
                try:
                    # Try to query the database to verify access
                    self.io.tool_output("\nVerifying database access...")
                    self.notion.client.databases.retrieve(database_id=database_id)
                    self.io.tool_output("✓ Successfully connected to the database!")
                    
                    # Display final status
                    if self.notion.is_ready():
                        self.io.tool_output("\n✓ Notion integration is fully configured and ready to use!")
                        self.io.tool_output("Try: /notion list")
                except Exception as e:
                    self.io.tool_error(f"✗ Error accessing database: {e}")
                    self.io.tool_output("Make sure you've shared the database with your integration.")
        else:
            self.io.tool_output("\nYou can complete setup later with: /notion setup --database-id YOUR_DATABASE_ID")
            self.io.tool_output("Or create a database automatically with: /notion setup --create-db")
    
    def _create_database(self, title: str = "Codecraft TODOs") -> None:
        """Create a new Notion database.
        
        Args:
            title: Title for the database
        """
        if not self.notion.client:
            self.io.tool_error("Notion client not initialized. Run '/notion setup' first.")
            return None
            
        database_id = self.notion.create_kanban_database(title)
        if database_id:
            self.io.tool_output(
                f"✓ Created Notion database with ID: {database_id}"
            )
            self.io.tool_output(
                f"To make this permanent, add to your environment: NOTION_DATABASE_ID={database_id}"
            )
            return database_id
        return None
            
    def _list_todos(self) -> None:
        """List all TODOs from Notion."""
        if not self.notion.is_ready():
            self.io.tool_error("Notion integration not ready. Run '/notion setup' first.")
            return
            
        todos = self.notion.list_todos()
        if not todos:
            self.io.tool_output("No TODOs found in Notion")
            return
            
        # Group by status
        status_groups = {}
        for todo in todos:
            status = todo.get("status") or "No Status"
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(todo)
            
        # Display TODOs grouped by status
        self.io.tool_output("\nTODOs from Notion:")
        for status, items in status_groups.items():
            self.io.tool_output(f"\n## {status}")
            for item in items:
                name = item.get("name", "Unnamed")
                priority = f"[{item.get('priority', 'No')} Priority]" if item.get("priority") else ""
                due_date = f"(Due: {item.get('due_date')})" if item.get("due_date") else ""
                item_id = item.get("id", "")
                self.io.tool_output(f"- {name} {priority} {due_date} (ID: {item_id})")
                
    def _add_todo(self, args) -> None:
        """Add a new TODO to Notion.
        
        Args:
            args: Parsed arguments containing name, status, priority, and due date
        """
        if not self.notion.is_ready():
            self.io.tool_error("Notion integration not ready. Run '/notion setup' first.")
            return
            
        todo_id = self.notion.add_todo(args.name, args.status, args.priority, args.due)
        if todo_id:
            self.io.tool_output(f"Added TODO: {args.name} (ID: {todo_id})")
            
    def _update_todo(self, args) -> None:
        """Update a TODO in Notion.
        
        Args:
            args: Parsed arguments containing id, name, status, priority, and due date
        """
        if not self.notion.is_ready():
            self.io.tool_error("Notion integration not ready. Run '/notion setup' first.")
            return
            
        kwargs = {}
        if args.name:
            kwargs["name"] = args.name
        if args.status:
            kwargs["status"] = args.status
        if args.priority:
            kwargs["priority"] = args.priority
        if args.due:
            kwargs["due_date"] = args.due
            
        success = self.notion.update_todo(args.id, **kwargs)
        if success:
            self.io.tool_output(f"Updated TODO with ID: {args.id}")
        else:
            self.io.tool_error(f"Failed to update TODO with ID: {args.id}")
            
    def _delete_todo(self, todo_id: str) -> None:
        """Delete a TODO from Notion.
        
        Args:
            todo_id: ID of the TODO to delete
        """
        if not self.notion.is_ready():
            self.io.tool_error("Notion integration not ready. Run '/notion setup' first.")
            return
            
        success = self.notion.delete_todo(todo_id)
        if success:
            self.io.tool_output(f"Deleted TODO with ID: {todo_id}")
        else:
            self.io.tool_error(f"Failed to delete TODO with ID: {todo_id}")
            
    def _import_todos(self, file_path: str) -> None:
        """Import TODOs from a file.
        
        Args:
            file_path: Path to the file
        """
        if not self.notion.is_ready():
            self.io.tool_error("Notion integration not ready. Run '/notion setup' first.")
            return
            
        path = Path(file_path)
        if not path.exists():
            self.io.tool_error(f"File not found: {file_path}")
            return
            
        success = self.notion.import_todos_from_file(file_path)
        if success:
            self.io.tool_output(f"Successfully imported TODOs from {file_path}")
            
    def _export_todos(self, file_path: str) -> None:
        """Export TODOs to a file.
        
        Args:
            file_path: Path to save the file
        """
        if not self.notion.is_ready():
            self.io.tool_error("Notion integration not ready. Run '/notion setup' first.")
            return
            
        success = self.notion.export_todos_to_file(file_path)
        if success:
            self.io.tool_output(f"Successfully exported TODOs to {file_path}")
            
    def _show_status(self) -> None:
        """Show the status of the Notion integration."""
        self.io.tool_output("\n== Notion Integration Status ==")
        
        # Check notion-client installation
        try:
            import notion_client
            self.io.tool_output("✓ notion-client package installed")
        except ImportError:
            self.io.tool_error("✗ notion-client package not installed")
            self.io.tool_output("  Run: pip install notion-client")
            return
            
        # Check token
        token = os.environ.get("NOTION_TOKEN")
        if token:
            self.io.tool_output("✓ NOTION_TOKEN environment variable set")
        else:
            self.io.tool_error("✗ NOTION_TOKEN environment variable not set")
            self.io.tool_output("  Run: /notion setup --token YOUR_TOKEN")
            
        # Check database ID
        database_id = os.environ.get("NOTION_DATABASE_ID")
        if database_id:
            self.io.tool_output(f"✓ NOTION_DATABASE_ID environment variable set: {database_id}")
        else:
            self.io.tool_error("✗ NOTION_DATABASE_ID environment variable not set")
            self.io.tool_output("  Run: /notion setup --database-id YOUR_DATABASE_ID")
            
        # Check client initialization
        if self.notion.client:
            self.io.tool_output("✓ Notion client initialized")
        else:
            self.io.tool_error("✗ Notion client not initialized")
            
        # Overall status
        if self.notion.is_ready():
            self.io.tool_output("\n✓ Notion integration is fully configured and ready to use!")
        else:
            self.io.tool_error("\n✗ Notion integration is not ready")
            self.io.tool_output("  Run: /notion setup to complete configuration") 