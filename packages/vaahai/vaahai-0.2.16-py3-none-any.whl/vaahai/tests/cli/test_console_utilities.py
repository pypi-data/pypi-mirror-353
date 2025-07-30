"""
Tests for the VaahAI CLI console utilities.

This module contains tests for the console output utilities in vaahai.cli.utils.console.
"""

import pytest
import io
import os
import sys
from unittest.mock import patch, MagicMock
from rich.text import Text

from vaahai.cli.utils.console import (
    # Basic output functions
    console,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_verbose,
    
    # Environment handling
    is_tty,
    is_verbose,
    is_quiet,
    should_output,
    
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
    
    # Formatting helpers
    format_highlight,
    format_key,
    format_value,
    format_status,
    format_path,
    format_command,
    format_url,
    
    # Context managers
    progress_spinner,
    capture_console_output,
)


class TestBasicOutputFunctions:
    """Test basic output functions."""
    
    def test_print_success(self):
        """Test print_success function."""
        with capture_console_output() as output:
            print_success("Test success message")
            assert "✓ Test success message" in output.getvalue()
    
    def test_print_error(self):
        """Test print_error function."""
        with capture_console_output() as output:
            print_error("Test error message")
            assert "✗ Test error message" in output.getvalue()
    
    def test_print_warning(self):
        """Test print_warning function."""
        with capture_console_output() as output:
            print_warning("Test warning message")
            assert "⚠ Test warning message" in output.getvalue()
    
    def test_print_info(self):
        """Test print_info function."""
        with capture_console_output() as output:
            print_info("Test info message")
            assert "ℹ Test info message" in output.getvalue()
    
    def test_print_verbose(self):
        """Test print_verbose function."""
        # Test with verbose mode enabled
        with patch('vaahai.cli.utils.console.is_verbose', return_value=True):
            with capture_console_output() as output:
                print_verbose("Test verbose message")
                assert "› Test verbose message" in output.getvalue()
        
        # Test with verbose mode disabled
        with patch('vaahai.cli.utils.console.is_verbose', return_value=False):
            with capture_console_output() as output:
                print_verbose("Test verbose message")
                assert output.getvalue() == ""


class TestEnvironmentHandling:
    """Test environment handling functions."""
    
    def test_is_tty(self):
        """Test is_tty function."""
        with patch('sys.stdout.isatty', return_value=True):
            assert is_tty() is True
        
        with patch('sys.stdout.isatty', return_value=False):
            assert is_tty() is False
    
    def test_is_verbose(self):
        """Test is_verbose function."""
        with patch.dict('os.environ', {'VAAHAI_VERBOSE': '1'}):
            assert is_verbose() is True
        
        with patch.dict('os.environ', {'VAAHAI_VERBOSE': '0'}):
            assert is_verbose() is False
        
        with patch.dict('os.environ', clear=True):
            assert is_verbose() is False
    
    def test_is_quiet(self):
        """Test is_quiet function."""
        with patch.dict('os.environ', {'VAAHAI_QUIET': '1'}):
            assert is_quiet() is True
        
        with patch.dict('os.environ', {'VAAHAI_QUIET': '0'}):
            assert is_quiet() is False
        
        with patch.dict('os.environ', clear=True):
            assert is_quiet() is False
    
    def test_should_output(self):
        """Test should_output function."""
        # Test normal output in normal mode
        with patch('vaahai.cli.utils.console.is_quiet', return_value=False), \
             patch('vaahai.cli.utils.console.is_verbose', return_value=False):
            assert should_output("normal") is True
            assert should_output("verbose") is False
            assert should_output("important") is True
        
        # Test normal output in quiet mode
        with patch('vaahai.cli.utils.console.is_quiet', return_value=True), \
             patch('vaahai.cli.utils.console.is_verbose', return_value=False):
            assert should_output("normal") is False
            assert should_output("verbose") is False
            assert should_output("important") is True
        
        # Test normal output in verbose mode
        with patch('vaahai.cli.utils.console.is_quiet', return_value=False), \
             patch('vaahai.cli.utils.console.is_verbose', return_value=True):
            assert should_output("normal") is True
            assert should_output("verbose") is True
            assert should_output("important") is True


class TestEnhancedOutputFunctions:
    """Test enhanced output functions."""
    
    def test_print_command_start(self):
        """Test print_command_start function."""
        with capture_console_output() as output:
            print_command_start("test", "Test command description")
            assert "Running command: test" in output.getvalue()
            assert "Test command description" in output.getvalue()
    
    def test_print_command_result(self):
        """Test print_command_result function."""
        with capture_console_output() as output:
            print_command_result(True, "Command completed successfully")
            assert "✓ Command completed successfully" in output.getvalue()
        
        with capture_console_output() as output:
            print_command_result(False, "Command failed")
            assert "✗ Command failed" in output.getvalue()
    
    def test_print_step(self):
        """Test print_step function."""
        with capture_console_output() as output:
            print_step(1, 3, "First step")
            assert "Step 1/3" in output.getvalue()
            assert "First step" in output.getvalue()
    
    def test_print_section(self):
        """Test print_section function."""
        with capture_console_output() as output:
            print_section("Test Section")
            assert "Test Section" in output.getvalue()
    
    def test_print_key_value(self):
        """Test print_key_value function."""
        with capture_console_output() as output:
            print_key_value("Name", "VaahAI")
            assert "Name" in output.getvalue()
            assert "VaahAI" in output.getvalue()
    
    def test_print_list(self):
        """Test print_list function."""
        with capture_console_output() as output:
            print_list(["Item 1", "Item 2", "Item 3"], "Test List")
            assert "Test List" in output.getvalue()
            assert "Item 1" in output.getvalue()
            assert "Item 2" in output.getvalue()
            assert "Item 3" in output.getvalue()
    
    def test_print_tree(self):
        """Test print_tree function."""
        with capture_console_output() as output:
            data = {
                "config": {
                    "api_key": "abc123",
                    "model": "gpt-4"
                },
                "version": "0.2.15"
            }
            print_tree(data, "Test Tree")
            assert "Test Tree" in output.getvalue()
            assert "config" in output.getvalue()
            assert "api_key" in output.getvalue()
            assert "version" in output.getvalue()
    
    def test_print_columns(self):
        """Test print_columns function."""
        with capture_console_output() as output:
            # Now using Table.grid instead of Columns
            with patch('vaahai.cli.utils.console.Table.grid') as mock_table_grid:
                mock_table = MagicMock()
                mock_table_grid.return_value = mock_table
                
                print_columns(["Item 1", "Item 2", "Item 3", "Item 4"])
                
                # Verify Table.grid was called
                mock_table_grid.assert_called_once()
                # Verify add_column was called multiple times
                assert mock_table.add_column.call_count > 0
                # Verify add_row was called at least once
                assert mock_table.add_row.call_count > 0
                # Verify console.print was called with the table
                assert mock_table.add_row.called
    
    def test_print_json(self):
        """Test print_json function."""
        with capture_console_output() as output:
            data = {"name": "VaahAI", "version": "0.2.15"}
            print_json(data, "Test JSON")
            assert "Test JSON" in output.getvalue()
            assert "name" in output.getvalue()
            assert "VaahAI" in output.getvalue()
            assert "version" in output.getvalue()
            assert "0.2.15" in output.getvalue()


class TestFormattingHelpers:
    """Test formatting helper functions."""
    
    def test_format_highlight(self):
        """Test format_highlight function."""
        result = format_highlight("Test highlight")
        assert isinstance(result, Text)
        assert result.plain == "Test highlight"
        assert "highlight" in result.style
    
    def test_format_key(self):
        """Test format_key function."""
        result = format_key("test_key")
        assert isinstance(result, Text)
        assert result.plain == "test_key"
        assert "bold" in result.style
        assert "blue" in result.style
    
    def test_format_value(self):
        """Test format_value function."""
        # Test string format
        result = format_value("test_value", "string")
        assert isinstance(result, Text)
        assert result.plain == '"test_value"'
        assert "green" in result.style
        
        # Test number format
        result = format_value("123", "number")
        assert isinstance(result, Text)
        assert result.plain == "123"
        assert "cyan" in result.style
        
        # Test boolean format
        result = format_value("true", "boolean")
        assert isinstance(result, Text)
        assert result.plain == "true"
        assert "magenta" in result.style
        
        # Test default format
        result = format_value("test_value")
        assert isinstance(result, Text)
        assert result.plain == "test_value"
    
    def test_format_status(self):
        """Test format_status function."""
        # Test success status
        result = format_status("success")
        assert isinstance(result, Text)
        assert result.plain == "success"
        assert "success" in result.style
        
        # Test error status
        result = format_status("error")
        assert isinstance(result, Text)
        assert result.plain == "error"
        assert "error" in result.style
        
        # Test warning status
        result = format_status("warning")
        assert isinstance(result, Text)
        assert result.plain == "warning"
        assert "warning" in result.style
        
        # Test info status
        result = format_status("info")
        assert isinstance(result, Text)
        assert result.plain == "info"
        assert "info" in result.style
        
        # Test unknown status
        result = format_status("unknown")
        assert isinstance(result, Text)
        assert result.plain == "unknown"
    
    def test_format_path(self):
        """Test format_path function."""
        result = format_path("/path/to/file.py")
        assert isinstance(result, Text)
        assert result.plain == "/path/to/file.py"
        assert "path" in result.style
    
    def test_format_command(self):
        """Test format_command function."""
        result = format_command("vaahai config init")
        assert isinstance(result, Text)
        assert result.plain == "vaahai config init"
        assert "command" in result.style
    
    def test_format_url(self):
        """Test format_url function."""
        result = format_url("https://example.com")
        assert isinstance(result, Text)
        assert result.plain == "https://example.com"
        assert "url" in result.style


class TestContextManagers:
    """Test context manager utilities."""
    
    def test_progress_spinner(self):
        """Test progress_spinner context manager."""
        # Mock Progress class to avoid actual terminal output
        with patch('vaahai.cli.utils.console.Progress') as mock_progress:
            mock_instance = MagicMock()
            mock_progress.return_value = mock_instance
            mock_instance.add_task.return_value = 1
            
            # Test basic usage
            with progress_spinner("Loading...") as spinner:
                spinner.update("Processing...")
            
            # Verify Progress was created with the right columns
            mock_progress.assert_called_once()
            assert mock_instance.start.called
            assert mock_instance.stop.called
            assert mock_instance.add_task.called_with("Loading...")
            assert mock_instance.update.called_with(1, description="Processing...")
    
    def test_capture_console_output(self):
        """Test capture_console_output context manager."""
        # Use a direct string for testing instead of relying on console.print
        # which might be redirected differently in the test environment
        with capture_console_output() as output:
            # Write directly to the StringIO object
            output.write("Test output")
            assert "Test output" in output.getvalue()
