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
    print_verbose("This is a verbose message (only visible in verbose mode)")
    
    # Panels
    print_header("Panels", "Different panel styles")
    print_panel("This is a default panel with blue style", title="Default Panel")
    print_panel("This is a success panel", title="Success Panel", style="success")
    print_panel("This is an error panel", title="Error Panel", style="error")
    print_panel("This is a warning panel", title="Warning Panel", style="warning")
    
    # Code blocks
    print_header("Code Blocks", "Syntax highlighted code")
    python_code = """
def hello_world():
    \"\"\"Print hello world message.\"\"\"
    print("Hello, World!")
    
    # This is a comment
    for i in range(5):
        print(f"Count: {i}")
        
hello_world()
"""
    print_code(python_code, title="Python Code Example")
    
    # Markdown
    print_header("Markdown", "Formatted markdown text")
    markdown_text = """
# VaahAI

## Multi-agent AI CLI tool

- Built with **Microsoft Autogen Framework**
- Supports multiple LLM providers
- Features:
  - Code review
  - Security audit
  - Quality analysis

[Visit GitHub](https://github.com/webreinvent/vaahai)
"""
    print_markdown(markdown_text)
    
    # Tables
    print_header("Tables", "Formatted data tables")
    columns = ["Command", "Description", "Group"]
    rows = [
        ["config", "Manage configuration", "core"],
        ["version", "Show version information", "core"],
        ["review", "Review code", "project"],
        ["audit", "Audit code", "project"],
        ["helloworld", "Test command", "dev"],
    ]
    print_table(columns, rows, title="VaahAI Commands")
    
    # Formatted elements
    print_header("Formatted Elements", "Consistently styled elements")
    console.print(f"File path: {format_path('/path/to/file.py')}")
    console.print(f"Command: {format_command('vaahai config init')}")
    console.print(f"URL: {format_url('https://github.com/webreinvent/vaahai')}")
    
    # Interactive elements (only in TTY)
    print_header("Interactive Elements", "User interaction (only in TTY)")
    try:
        if confirm("Would you like to see a progress bar demo?"):
            with create_progress() as progress:
                task = progress.add_task("[cyan]Processing...", total=100)
                for i in range(101):
                    progress.update(task, completed=i)
                    time.sleep(0.01)
            print_success("Progress bar demo completed!")
            
            name = ask_question("What's your name?", default="User")
            print_success(f"Hello, {name}!")
            
            color = ask_question(
                "What's your favorite color?", 
                choices=["red", "green", "blue", "yellow"]
            )
            print_success(f"You chose {color}!")
    except Exception as e:
        print_info("Interactive elements skipped (non-TTY environment)")
    
    print_header("Showcase Complete", "All formatting examples demonstrated")
    print_success("Rich integration showcase completed successfully!")


if __name__ == "__main__":
    showcase_app()
