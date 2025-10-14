"""
TDD tests for main.py simplification with AppConfig.from_cli_args().

These tests are written BEFORE refactoring main.py to verify that:
1. AppConfig.from_cli_args() can handle all CLI argument patterns
2. The simplified main() produces identical behavior
3. Report generator selection logic works correctly
4. All edge cases are handled

Tests will initially FAIL (need implementation), then guide refactoring.
"""

import unittest
from unittest.mock import Mock, patch
import sys

from src.config.app_config import AppConfig


class TestAppConfigFromCLIArgsIntegration(unittest.TestCase):
    """Test AppConfig.from_cli_args() with realistic CLI patterns."""

    def test_from_cli_args_minimal(self):
        """Test minimal CLI args (just directories)."""
        mock_args = Mock()
        mock_args.directories = ['/test/dir']
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.output_format = 'summary'
        mock_args.level = 'file'
        mock_args.hierarchical = False

        config = AppConfig.from_cli_args(mock_args)

        self.assertEqual(config.directories, ['/test/dir'])
        self.assertEqual(config.threshold_low, 10.0)
        self.assertEqual(config.output_format, 'summary')

    def test_from_cli_args_with_hotspots(self):
        """Test CLI args with hotspot analysis options."""
        mock_args = Mock()
        mock_args.directories = ['/test/dir']
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.output_format = 'summary'
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.list_hotspots = True
        mock_args.hotspot_threshold = 75
        mock_args.hotspot_output = 'hotspots.txt'

        config = AppConfig.from_cli_args(mock_args)

        self.assertTrue(config.list_hotspots)
        self.assertEqual(config.hotspot_threshold, 75)
        self.assertEqual(config.hotspot_output, 'hotspots.txt')

    def test_from_cli_args_with_review_strategy(self):
        """Test CLI args with review strategy options."""
        mock_args = Mock()
        mock_args.directories = ['/test/dir']
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.output_format = 'summary'
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.review_strategy = True
        mock_args.review_output = 'custom_review.md'
        mock_args.review_branch_only = True
        mock_args.review_base_branch = 'develop'

        config = AppConfig.from_cli_args(mock_args)

        self.assertTrue(config.review_strategy)
        self.assertEqual(config.review_output, 'custom_review.md')
        self.assertTrue(config.review_branch_only)
        self.assertEqual(config.review_base_branch, 'develop')


class TestMainSimplifiedBehavior(unittest.TestCase):
    """Test that simplified main() behaves identically to original."""

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    def test_main_creates_app_with_config(self, mock_parse_args, mock_app_cls):
        """Test that main() creates MetricMancerApp with AppConfig."""
        # Setup mock args
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['/test']
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.output_format = 'summary'
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False

        mock_parser.parse_args.return_value = mock_args
        mock_parser.add_argument = Mock()
        mock_parse_args.return_value = mock_parser

        mock_app_instance = Mock()
        mock_app_cls.return_value = mock_app_instance

        # Mock sys.argv to avoid usage print
        with patch.object(sys, 'argv', ['main.py', '/test']):
            from src.main import main
            main()

        # Verify MetricMancerApp was called
        mock_app_cls.assert_called_once()

        # Verify it received a config parameter
        call_kwargs = mock_app_cls.call_args[1]
        self.assertIn('config', call_kwargs)

        # Verify run was called
        mock_app_instance.run.assert_called_once()

    @patch('src.main.get_output_filename')
    @patch('src.main.ReportGeneratorFactory')
    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    def test_main_uses_factory_for_generator_selection(self, mock_parse_args, mock_app_cls,
                                                       mock_factory, mock_get_filename):
        """Test that main() uses ReportGeneratorFactory for generator selection."""
        # Setup mock args
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['/test']
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.output_format = 'json'
        mock_args.output_file = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False

        mock_parser.parse_args.return_value = mock_args
        mock_parser.add_argument = Mock()
        mock_parse_args.return_value = mock_parser

        mock_generator = Mock()
        mock_factory.create.return_value = mock_generator
        mock_get_filename.return_value = 'report.json'

        mock_app_instance = Mock()
        mock_app_cls.return_value = mock_app_instance

        # Mock sys.argv
        with patch.object(sys, 'argv', ['main.py', '/test']):
            from src.main import main
            main()

        # Verify factory was used
        mock_factory.create.assert_called_once_with('json')

        # Verify app was created with factory result
        call_kwargs = mock_app_cls.call_args[1]
        self.assertEqual(call_kwargs['report_generator_cls'], mock_generator)

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    def test_main_handles_output_file_for_json(self, mock_parse_args, mock_app_cls):
        """Test that main() properly handles output_file for json format."""
        # Setup mock args for JSON output
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['/test']
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.output_format = 'json'
        mock_args.output_file = None  # Should generate default
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = False

        mock_parser.parse_args.return_value = mock_args
        mock_parser.add_argument = Mock()
        mock_parse_args.return_value = mock_parser

        mock_app_instance = Mock()
        mock_app_cls.return_value = mock_app_instance

        # Mock sys.argv
        with patch.object(sys, 'argv', ['main.py', '/test']):
            with patch('src.main.get_output_filename') as mock_get_filename:
                mock_get_filename.return_value = 'generated_report.json'
                from src.main import main
                main()

        # Verify output_file was set in config
        call_kwargs = mock_app_cls.call_args[1]
        config = call_kwargs['config']
        self.assertEqual(config.output_file, 'generated_report.json')

    @patch('src.main.print_usage')
    def test_main_prints_usage_when_no_args(self, mock_usage):
        """Test that main() prints usage when called with no arguments."""
        with patch.object(sys, 'argv', ['main.py']):
            from src.main import main
            main()

        mock_usage.assert_called_once()

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    def test_main_sets_debug_flag(self, mock_parse_args, mock_app_cls):
        """Test that main() properly handles debug flag."""
        # Setup mock args with debug
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['/test']
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.output_format = 'summary'
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.debug = True

        mock_parser.parse_args.return_value = mock_args
        mock_parser.add_argument = Mock()
        mock_parse_args.return_value = mock_parser

        mock_app_instance = Mock()
        mock_app_cls.return_value = mock_app_instance

        # Mock sys.argv
        with patch.object(sys, 'argv', ['main.py', '/test', '--debug']):
            with patch('src.utilities.debug.DEBUG', False):
                from src.main import main
                main()

        # Verify debug was set in config
        call_kwargs = mock_app_cls.call_args[1]
        config = call_kwargs['config']
        self.assertTrue(config.debug)


class TestMainCodeReduction(unittest.TestCase):
    """Test that simplified main() has less code (reduces churn)."""

    def test_main_function_line_count_reduced(self):
        """Test that new main() has significantly fewer lines than original.

        Original main() has ~70 lines with lots of conditional logic and
        manual parameter passing. Goal is to reduce to ~30 lines.
        """
        # This test documents the goal - will pass once refactoring is done
        import inspect
        from src.main import main

        source_lines = inspect.getsource(main).split('\n')
        # Remove empty lines and comments
        code_lines = [line for line in source_lines
                      if line.strip() and not line.strip().startswith('#')]

        # Original: ~50 lines of actual code
        # Target: ~25 lines (50% reduction)
        # This will fail initially, then pass after refactoring
        self.assertLess(len(code_lines), 40,
                        f"main() should be simplified to <40 lines, currently {len(code_lines)}")

    def test_main_has_no_manual_parameter_construction(self):
        """Test that main() doesn't manually construct parameter dicts.

        Original main() has 15+ lines of manual parameter passing.
        New version should use AppConfig.from_cli_args().
        """
        import inspect
        from src.main import main

        source = inspect.getsource(main)

        # Should not have manual parameter passing
        self.assertNotIn('directories=args.directories', source,
                         "main() should not manually pass directories parameter")
        self.assertNotIn('threshold_low=args.threshold_low', source,
                         "main() should not manually pass threshold_low parameter")

        # Should use AppConfig.from_cli_args()
        self.assertIn('from_cli_args', source,
                      "main() should use AppConfig.from_cli_args()")


if __name__ == '__main__':
    unittest.main()
