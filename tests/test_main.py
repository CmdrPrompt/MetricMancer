"""
Test coverage for main.py module - the primary entry point of MetricMancer.

This module tests:
- Command line argument handling
- Main execution flow
- Output format selection
- Error handling for invalid inputs
- Integration with different report generators
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Import the module under test
import src.main
from src.main import main


class TestMain:
    """Test cases for the main entry point of MetricMancer."""

    def setup_method(self):
        """Reset debug state before each test."""
        src.utilities.debug.DEBUG = False

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path'])
    def test_main_with_valid_directory_html_format(self, mock_parse_args, mock_app_class):
        """Test main() with valid directory and HTML output format."""
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.directories = ['/test/path']
        mock_args.output_format = 'html'
        mock_args.threshold_low = 10
        mock_args.threshold_high = 20
        mock_args.problem_file_threshold = 5
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser
        
        # Setup mock app
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        # Mock get_output_filename to return a test filename
        with patch('src.main.get_output_filename', return_value='test_output.html'):
            # Execute
            main()
            
            # Verify app was created with correct parameters
            mock_app_class.assert_called_once_with(
                directories=['/test/path'],
                threshold_low=10,
                threshold_high=20,
                problem_file_threshold=5,
                output_file='test_output.html',
                report_generator_cls=None,  # HTML defaults to None
                level='file',
                hierarchical=False,
                output_format='html',
                list_hotspots=False,
                hotspot_threshold=50,
                hotspot_output=None
            )
            
            # Verify app.run() was called
            mock_app_instance.run.assert_called_once()

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path', '--output-format', 'json'])
    def test_main_with_json_format(self, mock_parse_args, mock_app_class):
        """Test main() with JSON output format."""
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.directories = ['/test/path']
        mock_args.output_format = 'json'
        mock_args.threshold_low = 10
        mock_args.threshold_high = 20
        mock_args.problem_file_threshold = 5
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser
        
        # Setup mock app
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        # Mock get_output_filename and JSONReportGenerator
        with patch('src.main.get_output_filename', return_value='test_output.json'), \
             patch('src.main.JSONReportGenerator') as mock_json_gen:
            
            # Execute
            main()
            
            # Verify correct report generator was selected
            mock_app_class.assert_called_once()
            args, kwargs = mock_app_class.call_args
            assert kwargs['report_generator_cls'] == mock_json_gen

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path', '--output-format', 'machine'])
    def test_main_with_machine_format(self, mock_parse_args, mock_app_class):
        """Test main() with machine/CLI output format."""
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.directories = ['/test/path']
        mock_args.output_format = 'machine'
        mock_args.threshold_low = 10
        mock_args.threshold_high = 20
        mock_args.problem_file_threshold = 5
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser
        
        # Setup mock app
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        # Mock CLIReportGenerator
        with patch('src.main.CLIReportGenerator') as mock_cli_gen:
            
            # Execute
            main()
            
            # Verify correct report generator was selected
            mock_app_class.assert_called_once()
            args, kwargs = mock_app_class.call_args
            assert kwargs['report_generator_cls'] == mock_cli_gen

    @patch('src.main.print_usage')
    @patch('sys.argv', ['metricmancer'])
    def test_main_with_no_arguments_prints_usage(self, mock_print_usage):
        """Test main() with no arguments prints usage and returns early."""
        # Execute
        main()
        
        # Verify usage was printed
        mock_print_usage.assert_called_once()

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path', '--debug'])
    def test_main_enables_debug_mode(self, mock_parse_args, mock_app_class):
        """Test main() properly enables debug mode when --debug flag is used."""
        # Setup mock arguments with debug enabled
        mock_args = MagicMock()
        mock_args.directories = ['/test/path']
        mock_args.output_format = 'html'
        mock_args.threshold_low = 10
        mock_args.threshold_high = 20
        mock_args.problem_file_threshold = 5
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = True
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser
        
        # Setup mock app
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        # Execute
        with patch('src.main.get_output_filename', return_value='test_output.html'):
            main()
            
            # Verify debug mode was enabled
            assert src.utilities.debug.DEBUG is True

    @patch('builtins.print')
    @patch('sys.stdout')
    @patch('sys.stderr')
    def test_main_configures_utf8_encoding(self, mock_stderr, mock_stdout, mock_print):
        """Test main() configures UTF-8 encoding for stdout/stderr."""
        # Setup mocks with reconfigure method
        mock_stdout.reconfigure = MagicMock()
        mock_stderr.reconfigure = MagicMock()
        
        # Mock other dependencies to prevent actual execution
        with patch('src.main.parse_args') as mock_parse_args, \
             patch('src.main.MetricMancerApp') as mock_app_class, \
             patch('sys.argv', ['metricmancer', '/test/path']):
            
            # Setup minimal mock args
            mock_args = MagicMock()
            mock_args.directories = ['/test/path']
            mock_args.output_format = 'html'
            mock_args.debug = False
            mock_parser = MagicMock()
            mock_parser.parse_args.return_value = mock_args
            mock_parse_args.return_value = mock_parser
            
            mock_app_instance = MagicMock()
            mock_app_class.return_value = mock_app_instance
            
            with patch('src.main.get_output_filename', return_value='test.html'):
                # Execute
                main()
                
                # Verify UTF-8 encoding was configured
                mock_stdout.reconfigure.assert_called_once_with(encoding='utf-8')
                mock_stderr.reconfigure.assert_called_once_with(encoding='utf-8')

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path', '--output-format', 'unknown'])
    def test_main_with_unknown_output_format_defaults_to_cli(self, mock_parse_args, mock_app_class):
        """Test main() with unknown output format defaults to CLI generator."""
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.directories = ['/test/path']
        mock_args.output_format = 'unknown'
        mock_args.threshold_low = 10
        mock_args.threshold_high = 20
        mock_args.problem_file_threshold = 5
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser
        
        # Setup mock app
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        # Mock CLIReportGenerator
        with patch('src.main.CLIReportGenerator') as mock_cli_gen:
            
            # Execute
            main()
            
            # Verify CLI generator was selected as fallback
            mock_app_class.assert_called_once()
            args, kwargs = mock_app_class.call_args
            assert kwargs['report_generator_cls'] == mock_cli_gen

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path1', '/test/path2'])
    def test_main_with_multiple_directories(self, mock_parse_args, mock_app_class):
        """Test main() handles multiple directories correctly."""
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.directories = ['/test/path1', '/test/path2']
        mock_args.output_format = 'html'
        mock_args.threshold_low = 10
        mock_args.threshold_high = 20
        mock_args.problem_file_threshold = 5
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser
        
        # Setup mock app
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        # Execute
        with patch('src.main.get_output_filename', return_value='test_output.html'):
            main()
            
            # Verify app was created with multiple directories
            mock_app_class.assert_called_once()
            args, kwargs = mock_app_class.call_args
            assert kwargs['directories'] == ['/test/path1', '/test/path2']


class TestMainErrorHandling:
    """Test error handling scenarios in main()."""

    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path'])
    def test_main_handles_parse_args_exception(self, mock_parse_args):
        """Test main() handles exceptions from argument parsing."""
        # Setup parse_args to raise an exception
        mock_parse_args.side_effect = SystemExit("Invalid arguments")
        
        # Execute and verify exception is propagated
        with pytest.raises(SystemExit):
            main()

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path'])
    def test_main_handles_app_creation_exception(self, mock_parse_args, mock_app_class):
        """Test main() handles exceptions during app creation."""
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.directories = ['/test/path']
        mock_args.output_format = 'html'
        mock_args.debug = False
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser
        
        # Setup app to raise exception during creation
        mock_app_class.side_effect = Exception("App creation failed")
        
        # Execute and verify exception is propagated
        with patch('src.main.get_output_filename', return_value='test.html'):
            with pytest.raises(Exception, match="App creation failed"):
                main()


class TestMainIntegration:
    """Integration tests for main() function."""

    def test_main_if_name_main_block(self):
        """Test that main() is called when script is run directly."""
        # This test verifies the if __name__ == "__main__": block
        # We can't easily test this without running the script as a subprocess,
        # but we can verify the structure exists
        
        # Read the main.py file to verify the structure
        import inspect
        main_source = inspect.getsource(src.main)
        assert 'if __name__ == "__main__":' in main_source
        assert 'main()' in main_source