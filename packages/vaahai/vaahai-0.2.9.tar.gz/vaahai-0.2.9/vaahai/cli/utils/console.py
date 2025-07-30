"""
Console output utilities for VaahAI CLI.

This module provides utility functions for consistent console output formatting
using Rich library across all CLI commands.
"""

import os
import sys
from typing import Optional, List, Dict, Any, Union, Callable

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
