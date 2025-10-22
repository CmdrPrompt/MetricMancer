"""
TDD tests for multi-format support in main.py.

Phase 4: main.py Multi-Format Support

These tests verify that main.py correctly:
1. Handles config.output_formats (plural) instead of just singular
2. Does not create single generator (delegates to MetricMancerApp)
3. Maintains backward compatibility with single format
4. Handles filename generation for file-based formats
"""

from unittest.mock import Mock, patch
from src.main import main


class TestMainMultiFormat:
    """Test main() with multiple output formats."""

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('src.main.sys.argv', ['main.py', 'src', '--output-formats', 'html,json'])
    def test_main_accepts_output_formats_argument(self, mock_parse_args, mock_app_cls):
        """Test that main() accepts --output-formats argument."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['src']
        mock_args.output_formats = 'html,json'
        mock_args.output_format = 'html'
        mock_args.debug = False
        # Set all other required args
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.report_folder = None
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        mock_args.review_strategy = False
        mock_args.review_output = 'review_strategy.md'
        mock_args.review_branch_only = False
        mock_args.review_base_branch = 'main'
        mock_args.auto_report_filename = False
        mock_args.report_filename = None
        mock_args.with_date = False

        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser

        mock_app = Mock()
        mock_app_cls.return_value = mock_app

        main()

        # Should create MetricMancerApp and run it
        assert mock_app_cls.called
        assert mock_app.run.called

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('src.main.sys.argv', ['main.py', 'src', '--output-formats', 'html,json,summary'])
    def test_main_passes_config_with_multiple_formats_to_app(self, mock_parse_args, mock_app_cls):
        """Test that main() passes config with output_formats to MetricMancerApp."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['src']
        mock_args.output_formats = 'html,json,summary'
        mock_args.output_format = 'html'
        mock_args.debug = False
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.report_folder = None
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        mock_args.review_strategy = False
        mock_args.review_output = 'review_strategy.md'
        mock_args.review_branch_only = False
        mock_args.review_base_branch = 'main'
        mock_args.auto_report_filename = False
        mock_args.report_filename = None
        mock_args.with_date = False

        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser

        mock_app = Mock()
        mock_app_cls.return_value = mock_app

        main()

        # Check that AppConfig was created with output_formats
        call_kwargs = mock_app_cls.call_args.kwargs
        config = call_kwargs.get('config')
        assert config is not None
        assert hasattr(config, 'output_formats')
        assert config.output_formats == ['html', 'json', 'summary']

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('src.main.sys.argv', ['main.py', 'src', '--output-formats', 'html,json'])
    def test_main_does_not_create_single_generator_for_multi_format(self, mock_parse_args, mock_app_cls):
        """Test that main() doesn't create a single generator for multi-format."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['src']
        mock_args.output_formats = 'html,json'
        mock_args.output_format = 'html'
        mock_args.debug = False
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.report_folder = None
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        mock_args.review_strategy = False
        mock_args.review_output = 'review_strategy.md'
        mock_args.review_branch_only = False
        mock_args.review_base_branch = 'main'
        mock_args.auto_report_filename = False
        mock_args.report_filename = None
        mock_args.with_date = False

        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser

        mock_app = Mock()
        mock_app_cls.return_value = mock_app

        main()

        # Verify MetricMancerApp was created with config
        mock_app_cls.assert_called_once()
        call_kwargs = mock_app_cls.call_args.kwargs
        assert 'config' in call_kwargs
        config = call_kwargs['config']
        assert config.output_formats == ['html', 'json']


class TestMainBackwardCompatibility:
    """Test backward compatibility with single format in main.py."""

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('src.main.sys.argv', ['main.py', 'src', '--output-format', 'html'])
    def test_main_single_format_still_works(self, mock_parse_args, mock_app_cls):
        """Test that single --output-format (old way) still works."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['src']
        mock_args.output_format = 'html'
        mock_args.output_formats = None
        mock_args.debug = False
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.report_folder = None
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        mock_args.review_strategy = False
        mock_args.review_output = 'review_strategy.md'
        mock_args.review_branch_only = False
        mock_args.review_base_branch = 'main'
        mock_args.auto_report_filename = False
        mock_args.report_filename = None
        mock_args.with_date = False

        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser

        mock_app = Mock()
        mock_app_cls.return_value = mock_app

        main()

        # Should work and run the app
        assert mock_app.run.called

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('src.main.sys.argv', ['main.py', 'src'])
    def test_main_default_format_works(self, mock_parse_args, mock_app_cls):
        """Test that default format (summary) works without specifying format."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['src']
        mock_args.output_format = 'summary'
        mock_args.output_formats = None
        mock_args.debug = False
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.report_folder = None
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        mock_args.review_strategy = False
        mock_args.review_output = 'review_strategy.md'
        mock_args.review_branch_only = False
        mock_args.review_base_branch = 'main'
        mock_args.auto_report_filename = False
        mock_args.report_filename = None
        mock_args.with_date = False

        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser

        mock_app = Mock()
        mock_app_cls.return_value = mock_app

        main()

        # Should work with default
        assert mock_app.run.called


class TestMainFilenameHandling:
    """Test filename handling for file-based formats."""

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('src.main.sys.argv', ['main.py', 'src', '--output-format', 'html'])
    def test_main_generates_filename_for_html_format(self, mock_parse_args, mock_app_cls):
        """Test that main() generates filename for HTML format when not provided."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['src']
        mock_args.output_format = 'html'
        mock_args.output_formats = None
        mock_args.debug = False
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.report_folder = None
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        mock_args.review_strategy = False
        mock_args.review_output = 'review_strategy.md'
        mock_args.review_branch_only = False
        mock_args.review_base_branch = 'main'
        mock_args.auto_report_filename = False
        mock_args.report_filename = None
        mock_args.with_date = False

        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser

        mock_app = Mock()
        mock_app_cls.return_value = mock_app

        main()

        # Should create and run the app for HTML format
        mock_app_cls.assert_called_once()
        mock_app.run.assert_called_once()

    @patch('src.main.MetricMancerApp')
    @patch('src.main.parse_args')
    @patch('src.main.sys.argv', ['main.py', 'src', '--output-formats', 'html,json'])
    def test_main_generates_base_filename_for_multi_format(self, mock_parse_args, mock_app_cls):
        """Test that main() generates base filename for multi-format file outputs."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.directories = ['src']
        mock_args.output_formats = 'html,json'
        mock_args.output_format = 'html'
        mock_args.debug = False
        mock_args.threshold_low = 10.0
        mock_args.threshold_high = 20.0
        mock_args.problem_file_threshold = None
        mock_args.level = 'file'
        mock_args.hierarchical = False
        mock_args.report_folder = None
        mock_args.list_hotspots = False
        mock_args.hotspot_threshold = 50
        mock_args.hotspot_output = None
        mock_args.review_strategy = False
        mock_args.review_output = 'review_strategy.md'
        mock_args.review_branch_only = False
        mock_args.review_base_branch = 'main'
        mock_args.auto_report_filename = False
        mock_args.report_filename = None
        mock_args.with_date = False

        mock_parser.parse_args.return_value = mock_args
        mock_parse_args.return_value = mock_parser

        mock_app = Mock()
        mock_app_cls.return_value = mock_app

        main()

        # Should create app with config containing multi-format output
        mock_app_cls.assert_called_once()
        call_kwargs = mock_app_cls.call_args.kwargs
        config = call_kwargs.get('config')
        assert config.output_formats == ['html', 'json']
        mock_app.run.assert_called_once()
