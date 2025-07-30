"""
Rich formatting showcase for VaahAI CLI.

This module demonstrates the Rich formatting capabilities of the VaahAI CLI.
It serves as both a test and an example of how to use the formatting utilities.
"""

import typer
import time
from pathlib import Path
from typing import Optional

from vaahai.cli.utils.console import (
    console,
    print_header,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_verbose,
    print_panel,
    print_code,
    print_markdown,
    print_table,
    create_table,
    ask_question,
    confirm,
    create_progress,
    format_path,
    format_command,
    format_url,
    # Enhanced output functions
    print_command_start,
    print_command_result,
    print_step,
    print_section,
    print_key_value,
    print_list,
    print_tree,
    print_columns,
    print_json,
    # Enhanced formatting helpers
    format_highlight,
    format_key,
    format_value,
    format_status,
    # Context managers
    progress_spinner,
)

showcase_app = typer.Typer(help="Demonstrate Rich formatting capabilities")


@showcase_app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """Showcase Rich formatting capabilities."""
    if ctx.invoked_subcommand is None:
        run_showcase()


def run_showcase():
    """Run the Rich formatting showcase."""
    print_header("VaahAI Rich Formatting Showcase", "Demonstrating the Rich formatting capabilities")
    
    # Basic message types
    print_header("Message Types", "Different types of messages")
    print_success("This is a success message")
    print_error("This is an error message")
    print_warning("This is a warning message")
    print_info("This is an info message")
    print_verbose("This is a verbose message (only visible with --verbose)")
    
    # Panels and code blocks
    print_header("Panels and Code Blocks", "Formatted panels and code blocks")
    print_panel("This is a panel with formatted content.\nIt can contain multiple lines of text.", title="Example Panel")
    
    code_example = '''
def hello_world():
    """Say hello to the world."""
    print("Hello, World!")
    
if __name__ == "__main__":
    hello_world()
'''
    print_code(code_example, language="python", title="Python Example")
    
    # Markdown
    print_header("Markdown", "Formatted markdown text")
    markdown_example = '''
# Markdown Example

This is **bold** text and this is *italic* text.

## Lists
- Item 1
- Item 2
- Item 3

## Code
```python
def example():
    return "This is a code block in markdown"
```
'''
    print_markdown(markdown_example)
    
    # Tables
    print_header("Tables", "Formatted tables")
    columns = ["Name", "Type", "Description"]
    rows = [
        ["config", "Command", "Manage configuration"],
        ["review", "Command", "Review code"],
        ["audit", "Command", "Audit code"],
    ]
    print_table(columns, rows, title="VaahAI Commands")
    
    # User input
    print_header("User Input", "Interactive prompts")
    print_info("The following would ask for user input, but is disabled in showcase mode:")
    print_code('response = ask_question("What is your name?")', language="python")
    print_code('confirmed = confirm("Do you want to continue?")', language="python")
    
    # Progress indicators
    print_header("Progress Indicators", "Progress bars and spinners")
    print_info("Example of a progress bar:")
    
    # Only show progress bar if in interactive mode
    if console.is_interactive:
        with console.status("Working...") as status:
            time.sleep(1)
            status.update("Still working...")
            time.sleep(1)
    else:
        print_info("Progress bar not shown in non-interactive mode")
    
    # Formatting helpers
    print_header("Formatting Helpers", "Styled text formatting")
    console.print(f"File path: {format_path('/path/to/file.py')}")
    console.print(f"Command: {format_command('vaahai config init')}")
    console.print(f"URL: {format_url('https://example.com')}")
    
    # Enhanced output functions
    print_header("Enhanced Output Functions", "Additional formatting utilities")
    
    # Command execution formatting
    print_section("Command Execution Formatting")
    print_command_start("vaahai config init", "Initialize VaahAI configuration")
    print_step(1, 3, "Checking existing configuration")
    print_step(2, 3, "Creating new configuration file")
    print_step(3, 3, "Setting default values")
    print_command_result(True, "Configuration initialized successfully")
    
    # Structured data output
    print_section("Structured Data Output")
    
    # Key-value pairs
    print_info("Key-value pairs:")
    print_key_value("Project", "VaahAI")
    print_key_value("Version", "0.2.15")
    print_key_value("Status", "Active")
    
    # Lists
    print_info("Bulleted list:")
    print_list(["First item", "Second item", "Third item"], "Sample List")
    
    # Tree structure
    print_info("Tree structure:")
    tree_data = {
        "vaahai": {
            "cli": {
                "commands": "Command implementations",
                "utils": {
                    "console.py": "Console utilities",
                    "help.py": "Help formatting"
                }
            },
            "agents": "AI agent implementations"
        }
    }
    print_tree(tree_data, "Project Structure")
    
    # Columns
    print_info("Columnar layout:")
    print_columns(["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6"], num_columns=3)
    
    # JSON data
    print_info("JSON data:")
    json_data = {
        "name": "VaahAI",
        "version": "0.2.15",
        "dependencies": {
            "typer": "0.7.0",
            "rich": "latest",
            "autogen": "latest"
        }
    }
    print_json(json_data, "Project Configuration")
    
    # Enhanced formatting helpers
    print_section("Enhanced Formatting Helpers")
    console.print(f"Highlighted text: {format_highlight('Important information')}")
    console.print(f"Key: {format_key('api_key')}")
    console.print(f"String value: {format_value('hello', 'string')}")
    console.print(f"Number value: {format_value('42', 'number')}")
    console.print(f"Boolean value: {format_value('true', 'boolean')}")
    console.print(f"Status: {format_status('success')}")
    
    # Context managers
    print_section("Context Managers")
    print_info("Progress spinner (only shown in interactive mode):")
    
    # Only show spinner if in interactive mode
    if console.is_interactive:
        with progress_spinner("Loading data...") as spinner:
            time.sleep(1)
            spinner.update("Processing data...")
            time.sleep(1)
    else:
        print_info("Spinner not shown in non-interactive mode")
    
    # Final message
    print_success("Rich formatting showcase completed!")


if __name__ == "__main__":
    showcase_app()
