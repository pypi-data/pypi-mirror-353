"""
VaahAI CLI main entry point.

This module serves as the entry point for the VaahAI CLI application.
It defines the main Typer app instance and registers all command groups.
"""

import sys
import os
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

# Import command groups
from vaahai.cli.commands.core import core_app
from vaahai.cli.commands.project import project_app
from vaahai.cli.commands.dev import dev_app

# Import direct commands for backward compatibility
from vaahai.cli.commands.config.command import config_app
from vaahai.cli.commands.helloworld.command import helloworld_app
from vaahai.cli.commands.review.command import review_app
from vaahai.cli.commands.audit.command import audit_app
from vaahai.cli.commands.version.command import version_app
from vaahai.cli.utils.console import print_error, print_info

# Create the main Typer app instance
app = typer.Typer(
    help="A multi AI agent CLI tool using Microsoft Autogen Framework",
    no_args_is_help=True,  # Show help when no arguments are provided
)

# Register command groups
app.add_typer(core_app, name="core")
app.add_typer(project_app, name="project")
app.add_typer(dev_app, name="dev")

# Register direct commands for backward compatibility
app.add_typer(config_app, name="config")
app.add_typer(helloworld_app, name="helloworld")
app.add_typer(review_app, name="review")
app.add_typer(audit_app, name="audit")
app.add_typer(version_app, name="version")


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output with detailed logs and information",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all non-essential output",
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to custom configuration file",
    ),
):
    """
    VaahAI: A multi AI agent CLI tool using Microsoft Autogen Framework.
    
    VaahAI provides a suite of AI-powered tools for code analysis, review, and auditing.
    It leverages Microsoft's Autogen Framework to create a multi-agent system that can
    understand, analyze, and improve your codebase.
    
    Examples:
        vaahai config init                   # Initialize configuration
        vaahai review run ./my-project       # Review code in a directory
        vaahai audit run ./my-project        # Audit code for security issues
    """
    # Store global options in the context for use in commands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    
    # Handle conflicting options
    if verbose and quiet:
        print_error("Cannot use both --verbose and --quiet options together")
        raise typer.Exit(code=1)
    
    # Handle custom config file
    if config_file:
        if not config_file.exists():
            print_error(f"Config file not found: {config_file}")
            raise typer.Exit(code=1)
        ctx.obj["config_file"] = config_file
        if verbose:
            print_info(f"Using custom config file: {config_file}")


def main():
    """
    Main entry point for the CLI.
    """
    try:
        app()
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        if os.environ.get("VAAHAI_DEBUG") == "1":
            raise
        print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
