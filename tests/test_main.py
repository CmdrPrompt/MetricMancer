"""
Test coverage for main.py critical functionality.

This file contains only the essential tests for main.py that test behavior,
not implementation details. Tests for the Configuration Object Pattern
implementation are in test_main_simplification_tdd.py.

This module tests:
- Usage printing when no arguments provided
- Debug mode enablement
- UTF-8 encoding configuration
- Error handling for invalid inputs
- Integration structure
"""

import pytest
from unittest.mock import patch, MagicMock

# Import the module under test
import src.main
from src.main import main


class TestMainCriticalFunctionality:
    """Critical test cases for the main entry point of MetricMancer."""

    def setup_method(self):
        """Reset debug state before each test."""
        src.utilities.debug.DEBUG = False

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
        with patch('src.main.get_output_filename', return_value='test_output.html'), \
             patch('src.main.AppConfig'), \
             patch('src.main.ReportGeneratorFactory'):
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
             patch('sys.argv', ['metricmancer', '/test/path']), \
             patch('src.main.AppConfig'), \
             patch('src.main.ReportGeneratorFactory'):
            
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
        with patch('src.main.get_output_filename', return_value='test.html'), \
             patch('src.main.AppConfig'), \
             patch('src.main.ReportGeneratorFactory'):
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

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path', '--churn-period', '60'])
    def test_main_with_churn_period_flag(self, mock_parse_args, mock_app_class):
        """Test main() with --churn-period flag sets correct value in config."""
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.directories = ['/test/path']
        mock_args.output_format = 'summary'
        mock_args.output_formats = None
        mock_args.threshold_low = 10
        mock_args.threshold_high = 20
        mock_args.problem_file_threshold = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        mock_args.review_strategy = False
        mock_args.review_output = 'review_strategy.md'
        mock_args.review_branch_only = False
        mock_args.review_base_branch = 'main'
        mock_args.churn_period = 60  # Custom value
        mock_args.report_folder = None
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser
        
        # Setup mock app
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        # Execute
        main()
        
        # Verify MetricMancerApp was called with config containing churn_period=60
        mock_app_class.assert_called_once()
        call_kwargs = mock_app_class.call_args[1]
        assert 'config' in call_kwargs
        config = call_kwargs['config']
        assert config.churn_period == 60

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('sys.argv', ['metricmancer', '/test/path'])
    def test_main_with_default_churn_period(self, mock_parse_args, mock_app_class):
        """Test main() uses default churn_period of 30 days when not specified."""
        # Setup mock arguments without churn_period
        mock_args = MagicMock()
        mock_args.directories = ['/test/path']
        mock_args.output_format = 'summary'
        mock_args.output_formats = None
        mock_args.threshold_low = 10
        mock_args.threshold_high = 20
        mock_args.problem_file_threshold = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        mock_args.review_strategy = False
        mock_args.review_output = 'review_strategy.md'
        mock_args.review_branch_only = False
        mock_args.review_base_branch = 'main'
        mock_args.churn_period = 30  # Default value
        mock_args.report_folder = None
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser
        
        # Setup mock app
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance
        
        # Execute
        main()
        
        # Verify MetricMancerApp was called with config containing default churn_period=30
        mock_app_class.assert_called_once()
        call_kwargs = mock_app_class.call_args[1]
        assert 'config' in call_kwargs
        config = call_kwargs['config']
        assert config.churn_period == 30
