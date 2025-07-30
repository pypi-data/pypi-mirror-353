"""
Tests for the VaahAI CLI Rich integration.

This module contains tests for the Rich formatting utilities and showcase command.
"""

import pytest
import io
import sys
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from vaahai.cli.main import app
from vaahai.cli.utils.console import (
    console,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_verbose,
    is_tty,
    is_verbose,
    is_quiet,
    should_output,
)

runner = CliRunner()


def test_showcase_command_exists():
    """Test that the showcase command exists in the dev command group."""
    result = runner.invoke(app, ["dev", "--help"])
    assert result.exit_code == 0
    assert "showcase" in result.stdout


def test_showcase_command_runs():
    """Test that the showcase command runs without errors."""
    # Use non-interactive mode to avoid prompts
    with patch('sys.stdout.isatty', return_value=False):
        result = runner.invoke(app, ["dev", "showcase"])
        assert result.exit_code == 0
        assert "VaahAI Rich Formatting Showcase" in result.stdout


def test_message_styling():
    """Test that message styling functions work correctly."""
    # Capture stdout to check output
    stdout = io.StringIO()
    with patch('sys.stdout', stdout):
        # Create a test console that writes to our StringIO
        test_console = MagicMock()
        with patch('vaahai.cli.utils.console.console', test_console):
            print_success("Success message")
            print_error("Error message")
            print_warning("Warning message")
            print_info("Info message")
            
            # Check that console.print was called with the right styling
            test_console.print.assert_any_call("✓ Success message", style="success")
            test_console.print.assert_any_call("✗ Error message", style="error")
            test_console.print.assert_any_call("⚠ Warning message", style="warning")
            test_console.print.assert_any_call("ℹ Info message", style="info")


def test_environment_detection():
    """Test environment detection functions."""
    # Test TTY detection
    with patch('sys.stdout.isatty', return_value=True):
        assert is_tty() is True
    
    with patch('sys.stdout.isatty', return_value=False):
        assert is_tty() is False
    
    # Test verbose mode detection
    with patch.dict('os.environ', {'VAAHAI_VERBOSE': '1'}):
        assert is_verbose() is True
    
    with patch.dict('os.environ', {'VAAHAI_VERBOSE': '0'}):
        assert is_verbose() is False
    
    # Test quiet mode detection
    with patch.dict('os.environ', {'VAAHAI_QUIET': '1'}):
        assert is_quiet() is True
    
    with patch.dict('os.environ', {'VAAHAI_QUIET': '0'}):
        assert is_quiet() is False


def test_output_control():
    """Test output control based on verbosity settings."""
    # Test normal output
    with patch('vaahai.cli.utils.console.is_quiet', return_value=False), \
         patch('vaahai.cli.utils.console.is_verbose', return_value=False):
        assert should_output("normal") is True
        assert should_output("verbose") is False
        assert should_output("important") is True
    
    # Test quiet mode
    with patch('vaahai.cli.utils.console.is_quiet', return_value=True), \
         patch('vaahai.cli.utils.console.is_verbose', return_value=False):
        assert should_output("normal") is False
        assert should_output("verbose") is False
        assert should_output("important") is True
    
    # Test verbose mode
    with patch('vaahai.cli.utils.console.is_quiet', return_value=False), \
         patch('vaahai.cli.utils.console.is_verbose', return_value=True):
        assert should_output("normal") is True
        assert should_output("verbose") is True
        assert should_output("important") is True


def test_verbose_output():
    """Test that verbose output is only shown in verbose mode."""
    # Create a test console
    test_console = MagicMock()
    
    # Test in non-verbose mode
    with patch('vaahai.cli.utils.console.console', test_console), \
         patch('vaahai.cli.utils.console.should_output', return_value=False):
        print_verbose("Verbose message")
        test_console.print.assert_not_called()
    
    # Test in verbose mode
    test_console.reset_mock()
    with patch('vaahai.cli.utils.console.console', test_console), \
         patch('vaahai.cli.utils.console.should_output', return_value=True):
        print_verbose("Verbose message")
        test_console.print.assert_called_once()
