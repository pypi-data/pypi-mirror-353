"""
Console output utilities for VaahAI CLI.

This module provides utility functions for consistent console output formatting
using Rich library across all CLI commands.
"""

import os
import sys
from typing import Optional, List, Dict, Any, Union, Callable
import contextlib
import io

from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.box import Box, ROUNDED, SIMPLE
from rich.style import Style
from rich.theme import Theme
from rich.traceback import install as install_rich_traceback
from rich.tree import Tree
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule

# Define VaahAI color scheme
VAAHAI_COLORS = {
    "primary": "blue",
    "secondary": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "cyan",
    "muted": "dim",
    "highlight": "magenta",
    "code": "bright_black",
}

# Define VaahAI theme with consistent styles
VAAHAI_THEME = Theme({
    "info": f"bold {VAAHAI_COLORS['info']}",
    "warning": f"bold {VAAHAI_COLORS['warning']}",
    "error": f"bold {VAAHAI_COLORS['error']}",
    "success": f"bold {VAAHAI_COLORS['success']}",
    "heading": f"bold {VAAHAI_COLORS['primary']}",
    "subheading": f"{VAAHAI_COLORS['secondary']}",
    "muted": VAAHAI_COLORS['muted'],
    "highlight": f"bold {VAAHAI_COLORS['highlight']}",
    "code": VAAHAI_COLORS['code'],
    "command": "bold cyan on black",
    "path": "underline bright_blue",
    "url": "underline bright_blue",
})

# Create a shared console instance with our theme
console = Console(theme=VAAHAI_THEME, highlight=True)

# Install rich traceback handler for better error reporting
install_rich_traceback()


# Environment handling functions
def is_tty() -> bool:
    """Check if the current environment is a TTY."""
    return sys.stdout.isatty()


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return os.environ.get("VAAHAI_VERBOSE", "0") == "1"


def is_quiet() -> bool:
    """Check if quiet mode is enabled."""
    return os.environ.get("VAAHAI_QUIET", "0") == "1"


def should_output(level: str = "normal") -> bool:
    """
    Determine if output should be shown based on verbosity level.
    
    Args:
        level: The output level ('verbose', 'normal', or 'important')
        
    Returns:
        True if output should be shown, False otherwise
    """
    if is_quiet() and level != "important":
        return False
    if level == "verbose" and not is_verbose():
        return False
    return True


# Basic output functions
def print_header(title: str, subtitle: Optional[str] = None) -> None:
    """
    Print a formatted header with optional subtitle.
    
    Args:
        title: The main title text
        subtitle: Optional subtitle text
    """
    if not should_output("normal"):
        return
        
    console.print(Text(title, style="heading"))
    if subtitle:
        console.print(Text(subtitle, style="subheading"))
    console.print("")


def print_success(message: str) -> None:
    """
    Print a success message.
    
    Args:
        message: The success message to print
    """
    if not should_output("normal"):
        return
        
    console.print(f"✓ {message}", style="success")


def print_error(message: str) -> None:
    """
    Print an error message.
    
    Args:
        message: The error message to print
    """
    # Always show errors regardless of quiet mode
    console.print(f"✗ {message}", style="error")


def print_warning(message: str) -> None:
    """
    Print a warning message.
    
    Args:
        message: The warning message to print
    """
    if not should_output("normal"):
        return
        
    console.print(f"⚠ {message}", style="warning")


def print_info(message: str) -> None:
    """
    Print an info message.
    
    Args:
        message: The info message to print
    """
    if not should_output("normal"):
        return
        
    console.print(f"ℹ {message}", style="info")


def print_verbose(message: str) -> None:
    """
    Print a verbose message (only shown in verbose mode).
    
    Args:
        message: The verbose message to print
    """
    if not should_output("verbose"):
        return
        
    console.print(f"› {message}", style="muted")


def print_panel(
    content: Union[str, Text],
    title: Optional[str] = None,
    style: str = "blue",
    expand: bool = True,
    box: Box = ROUNDED,
) -> None:
    """
    Print content in a panel with optional title.
    
    Args:
        content: The content to display in the panel
        title: Optional title for the panel
        style: Color style for the panel border
        expand: Whether to expand the panel to fill the terminal width
        box: Box style for the panel
    """
    if not should_output("normal"):
        return
        
    # Convert string content to Text if needed
    if isinstance(content, str):
        content = Text(content)
        
    panel = Panel(
        content,
        title=title,
        border_style=style,
        expand=expand,
        box=box,
    )
    console.print(panel)


def print_code(
    code: str,
    language: str = "python",
    line_numbers: bool = True,
    title: Optional[str] = None,
    theme: str = "monokai",
) -> None:
    """
    Print formatted code with syntax highlighting.
    
    Args:
        code: The code to print
        language: The programming language for syntax highlighting
        line_numbers: Whether to show line numbers
        title: Optional title for the code block
        theme: Syntax highlighting theme
    """
    if not should_output("normal"):
        return
        
    syntax = Syntax(
        code,
        language,
        line_numbers=line_numbers,
        theme=theme,
    )
    if title:
        console.print(Text(title, style="heading"))
    console.print(syntax)


def print_markdown(markdown_text: str) -> None:
    """
    Print formatted markdown text.
    
    Args:
        markdown_text: The markdown text to print
    """
    if not should_output("normal"):
        return
        
    md = Markdown(markdown_text)
    console.print(md)


def create_table(
    columns: List[str],
    rows: List[List[Any]],
    title: Optional[str] = None,
    show_header: bool = True,
    box: Box = ROUNDED,
    padding: int = 1,
    expand: bool = False,
) -> Table:
    """
    Create a formatted table.
    
    Args:
        columns: List of column headers
        rows: List of rows, each containing values for each column
        title: Optional title for the table
        show_header: Whether to show the header row
        box: Box style for the table
        padding: Cell padding
        expand: Whether to expand the table to fill the terminal width
        
    Returns:
        A Rich Table object that can be printed with console.print()
    """
    table = Table(
        title=title, 
        show_header=show_header, 
        box=box, 
        padding=padding,
        expand=expand
    )
    
    # Add columns
    for column in columns:
        table.add_column(column)
    
    # Add rows
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    
    return table


def print_table(
    columns: List[str],
    rows: List[List[Any]],
    title: Optional[str] = None,
    show_header: bool = True,
    box: Box = ROUNDED,
    padding: int = 1,
    expand: bool = False,
) -> None:
    """
    Create and print a formatted table.
    
    Args:
        columns: List of column headers
        rows: List of rows, each containing values for each column
        title: Optional title for the table
        show_header: Whether to show the header row
        box: Box style for the table
        padding: Cell padding
        expand: Whether to expand the table to fill the terminal width
    """
    if not should_output("normal"):
        return
        
    table = create_table(
        columns=columns,
        rows=rows,
        title=title,
        show_header=show_header,
        box=box,
        padding=padding,
        expand=expand,
    )
    console.print(table)


def ask_question(
    question: str,
    default: Optional[str] = None,
    choices: Optional[List[str]] = None,
) -> str:
    """
    Ask the user a question and return their response.
    
    Args:
        question: The question to ask
        default: Default value if user doesn't provide input
        choices: Optional list of valid choices
        
    Returns:
        User's response as a string
    """
    if not is_tty():
        if default is not None:
            return default
        raise RuntimeError("Cannot prompt for input in non-interactive environment")
    
    if choices:
        result = Prompt.ask(
            question,
            default=default,
            choices=choices,
            show_choices=True,
        )
    else:
        result = Prompt.ask(question, default=default)
    
    return result


def confirm(
    question: str,
    default: bool = False,
) -> bool:
    """
    Ask the user for confirmation.
    
    Args:
        question: The confirmation question to ask
        default: Default value if user doesn't provide input
        
    Returns:
        True if confirmed, False otherwise
    """
    if not is_tty():
        return default
    
    return Confirm.ask(question, default=default)


def create_progress() -> Progress:
    """
    Create a progress bar with VaahAI styling.
    
    Returns:
        A Rich Progress object
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TaskProgressColumn(),
    )


def format_path(path: str) -> Text:
    """
    Format a file path with consistent styling.
    
    Args:
        path: The file path to format
        
    Returns:
        A styled Text object
    """
    return Text(path, style="path")


def format_command(command: str) -> Text:
    """
    Format a command with consistent styling.
    
    Args:
        command: The command to format
        
    Returns:
        A styled Text object
    """
    return Text(command, style="command")


def format_url(url: str) -> Text:
    """
    Format a URL with consistent styling.
    
    Args:
        url: The URL to format
        
    Returns:
        A styled Text object
    """
    return Text(url, style="url")


# Enhanced output functions for CLI context
def print_command_start(command_name: str, description: Optional[str] = None) -> None:
    """
    Print a formatted header when a command starts execution.
    
    Args:
        command_name: The name of the command being executed
        description: Optional description of what the command does
    """
    if not should_output("normal"):
        return
        
    header = f"Running command: {command_name}"
    if description:
        print_panel(f"{header}\n\n{description}", style=VAAHAI_COLORS["primary"])
    else:
        print_header(header)
    

def print_command_result(success: bool, message: str) -> None:
    """
    Print a formatted result when a command completes execution.
    
    Args:
        success: Whether the command completed successfully
        message: Result message to display
    """
    if success:
        print_success(message)
    else:
        print_error(message)


def print_step(step_number: int, total_steps: int, description: str) -> None:
    """
    Print a step indicator for multi-step operations.
    
    Args:
        step_number: Current step number
        total_steps: Total number of steps
        description: Description of the current step
    """
    if not should_output("normal"):
        return
        
    console.print(f"[bold blue]Step {step_number}/{total_steps}:[/] {description}")


def print_section(title: str) -> None:
    """
    Print a section divider with title.
    
    Args:
        title: The section title
    """
    if not should_output("normal"):
        return
        
    console.print()
    console.print(Rule(title, style="bold blue"))
    console.print()


# Additional structured output functions
def print_key_value(key: str, value: Any, key_style: str = "bold blue") -> None:
    """
    Print a key-value pair with consistent formatting.
    
    Args:
        key: The key/label
        value: The value to display
        key_style: Style to apply to the key
    """
    if not should_output("normal"):
        return
        
    console.print(f"[{key_style}]{key}:[/] {value}")


def print_list(items: List[Any], title: Optional[str] = None, bullet: str = "•") -> None:
    """
    Print a bulleted list of items.
    
    Args:
        items: List of items to display
        title: Optional title for the list
        bullet: Bullet character to use
    """
    if not should_output("normal"):
        return
        
    if title:
        console.print(f"[bold]{title}[/]")
        
    for item in items:
        console.print(f"{bullet} {item}")
    
    console.print()


def print_tree(data: Dict[str, Any], title: Optional[str] = None) -> None:
    """
    Print a hierarchical tree structure.
    
    Args:
        data: Dictionary containing hierarchical data
        title: Optional title for the tree
    """
    if not should_output("normal"):
        return
        
    tree = Tree(title or "")
    
    def _add_to_tree(node, data):
        for key, value in data.items():
            if isinstance(value, dict):
                branch = node.add(f"[bold]{key}[/]")
                _add_to_tree(branch, value)
            else:
                node.add(f"[bold]{key}:[/] {value}")
    
    _add_to_tree(tree, data)
    console.print(tree)


def print_columns(items: List[Any], num_columns: int = 3) -> None:
    """
    Print items in a columnar layout.
    
    Args:
        items: List of items to display
        num_columns: Number of columns to use
    """
    if not should_output("normal"):
        return
    
    str_items = [str(item) for item in items]
    
    # Calculate width for each column based on terminal width
    terminal_width = console.width
    column_width = max(10, terminal_width // num_columns - 2)
    
    # Group items into rows
    rows = []
    for i in range(0, len(str_items), num_columns):
        rows.append(str_items[i:i + num_columns])
    
    # Create a table with no borders to simulate columns
    table = Table.grid(padding=(0, 2), expand=True)
    for _ in range(num_columns):
        table.add_column(width=column_width)
    
    for row in rows:
        # Pad the row if needed
        while len(row) < num_columns:
            row.append("")
        table.add_row(*row)
    
    console.print(table)


def print_json(data: Dict[str, Any], title: Optional[str] = None) -> None:
    """
    Print formatted JSON data.
    
    Args:
        data: Dictionary containing data to display as JSON
        title: Optional title
    """
    import json
    
    if not should_output("normal"):
        return
        
    json_str = json.dumps(data, indent=2)
    
    if title:
        print_code(json_str, language="json", title=title)
    else:
        print_code(json_str, language="json")


# Enhanced formatting helpers
def format_highlight(text: str) -> Text:
    """
    Format text with highlight styling.
    
    Args:
        text: The text to format
        
    Returns:
        A styled Text object
    """
    return Text(text, style="highlight")


def format_key(text: str) -> Text:
    """
    Format a key/property name with consistent styling.
    
    Args:
        text: The key text to format
        
    Returns:
        A styled Text object
    """
    return Text(text, style="bold blue")


def format_value(text: str, type_hint: Optional[str] = None) -> Text:
    """
    Format a value with styling based on its type.
    
    Args:
        text: The value text to format
        type_hint: Optional type hint (string, number, boolean, etc.)
        
    Returns:
        A styled Text object
    """
    if type_hint == "string":
        return Text(f'"{text}"', style="green")
    elif type_hint == "number":
        return Text(text, style="cyan")
    elif type_hint == "boolean":
        return Text(text, style="magenta")
    else:
        return Text(text)


def format_status(status: str) -> Text:
    """
    Format a status message with appropriate styling.
    
    Args:
        status: The status text (success, error, warning, info)
        
    Returns:
        A styled Text object
    """
    status = status.lower()
    if status in ["success", "completed", "done", "ok"]:
        return Text(status, style="success")
    elif status in ["error", "failed", "failure"]:
        return Text(status, style="error")
    elif status in ["warning", "caution"]:
        return Text(status, style="warning")
    elif status in ["info", "notice"]:
        return Text(status, style="info")
    else:
        return Text(status)


# Context manager for progress reporting
class progress_spinner:
    """
    Context manager for displaying a spinner during an operation.
    
    Example:
        with progress_spinner("Loading data...") as spinner:
            # Do some work
            spinner.update("Processing data...")
            # Do more work
    """
    
    def __init__(self, message: str):
        self.message = message
        self.progress = None
        self.task_id = None
    
    def __enter__(self):
        if should_output("normal"):
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            )
            self.progress.start()
            self.task_id = self.progress.add_task(self.message)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()
    
    def update(self, message: str):
        """Update the spinner message."""
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, description=message)


# Utility for capturing console output for testing
@contextlib.contextmanager
def capture_console_output():
    """
    Context manager to capture console output for testing.
    
    Returns:
        StringIO object containing the captured output
    
    Example:
        with capture_console_output() as output:
            print_info("Test message")
            assert "Test message" in output.getvalue()
    """
    string_io = io.StringIO()
    original_console = console
    
    # Create a new console that writes to our StringIO
    temp_console = Console(file=string_io, theme=VAAHAI_THEME, highlight=False)
    
    # Replace the global console with our temporary one
    globals()['console'] = temp_console
    
    try:
        yield string_io
    finally:
        # Restore the original console
        globals()['console'] = original_console
