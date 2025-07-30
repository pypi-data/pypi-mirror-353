"""
Custom help formatting utilities for VaahAI CLI.

This module provides utilities for enhancing Typer's help output with Rich formatting.
"""

from typing import Any, List, Optional, Dict
import typer
from rich.console import Console

console = Console()


def custom_callback(ctx: typer.Context):
    """
    Custom callback for the main CLI app to enhance help output.
    
    Args:
        ctx: Typer context object
    """
    # Use Typer's built-in help instead of custom formatting
    typer.echo(ctx.get_help())
    raise typer.Exit()


def show_custom_help(ctx: typer.Context):
    """
    Display custom formatted help using Rich.
    
    Args:
        ctx: Typer context object
    """
    # Use Typer's built-in help instead of custom formatting
    typer.echo(ctx.get_help())
    raise typer.Exit()


def format_command_help(ctx: typer.Context):
    """
    Format help for a specific command.
    
    Args:
        ctx: Typer context object for the command
    """
    # Use Typer's built-in help instead of custom formatting
    typer.echo(ctx.get_help())
    raise typer.Exit()
