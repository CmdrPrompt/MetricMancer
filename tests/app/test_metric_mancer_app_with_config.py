"""
Unit tests for MetricMancerApp with AppConfig integration (TDD).

These tests are written BEFORE implementation to follow Test-Driven Development.
They define the expected behavior when MetricMancerApp accepts AppConfig.
"""

import unittest
from unittest.mock import Mock, patch
import os
import tempfile

from src.config.app_config import AppConfig
from src.app.metric_mancer_app import MetricMancerApp


class TestMetricMancerAppWithConfig(unittest.TestCase):
    """Test MetricMancerApp can accept and use AppConfig."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig(
            directories=[self.temp_dir],
            threshold_low=5.0,
            threshold_high=15.0,
            problem_file_threshold=10,
            output_file='test_report.html',
            level='function',
            hierarchical=True,
            output_format='json',
            report_folder='test_output',
            list_hotspots=True,
            hotspot_threshold=75,
            hotspot_output='hotspots.txt',
            review_strategy=True,
            review_output='review.md',
            review_branch_only=True,
            review_base_branch='develop',
            debug=True
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_app_with_config_parameter(self):
        """Test that MetricMancerApp can be created with config parameter."""
        # This test will FAIL initially - that's expected in TDD!
        app = MetricMancerApp(config=self.config)

        # Verify config is stored
        self.assertIsNotNone(app.config)
        self.assertEqual(app.config.directories, [self.temp_dir])

    def test_config_values_accessible_via_app(self):
        """Test that config values are accessible through app instance."""
        app = MetricMancerApp(config=self.config)

        # Should be able to access config values
        self.assertEqual(app.config.threshold_low, 5.0)
        self.assertEqual(app.config.threshold_high, 15.0)
        self.assertEqual(app.config.problem_file_threshold, 10)
        self.assertEqual(app.config.output_file, 'test_report.html')
        self.assertEqual(app.config.level, 'function')
        self.assertEqual(app.config.hierarchical, True)
        self.assertEqual(app.config.output_format, 'json')
        self.assertEqual(app.config.report_folder, 'test_output')

    def test_config_hotspot_settings_accessible(self):
        """Test that hotspot configuration is accessible."""
        app = MetricMancerApp(config=self.config)

        self.assertEqual(app.config.list_hotspots, True)
        self.assertEqual(app.config.hotspot_threshold, 75)
        self.assertEqual(app.config.hotspot_output, 'hotspots.txt')

    def test_config_review_settings_accessible(self):
        """Test that review strategy configuration is accessible."""
        app = MetricMancerApp(config=self.config)

        self.assertEqual(app.config.review_strategy, True)
        self.assertEqual(app.config.review_output, 'review.md')
        self.assertEqual(app.config.review_branch_only, True)
        self.assertEqual(app.config.review_base_branch, 'develop')

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_analyzer_uses_config_thresholds(self, mock_analyzer_cls, mock_scanner_cls):
        """Test that Analyzer is initialized with config thresholds."""
        MetricMancerApp(config=self.config)

        # Verify Analyzer was created with correct thresholds from config
        mock_analyzer_cls.assert_called_once()
        call_kwargs = mock_analyzer_cls.call_args[1]
        self.assertEqual(call_kwargs['threshold_low'], self.config.threshold_low)
        self.assertEqual(call_kwargs['threshold_high'], self.config.threshold_high)

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.app.metric_mancer_app.ReportGenerator')
    def test_run_uses_config_directories(self, mock_report, mock_analyzer_cls, mock_scanner_cls):
        """Test that run() method uses directories from config."""
        # Setup mocks
        mock_scanner = Mock()
        mock_scanner.scan.return_value = []
        mock_scanner_cls.return_value = mock_scanner

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {}
        mock_analyzer.timing = None  # Avoid timing dict subscript error
        mock_analyzer_cls.return_value = mock_analyzer

        app = MetricMancerApp(config=self.config)
        app.run()

        # Verify scanner.scan was called with config directories
        mock_scanner.scan.assert_called_once_with(self.config.directories)

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_run_uses_config_report_settings(self, mock_analyzer_cls, mock_scanner_cls):
        """Test that run() uses report settings from config."""
        # Setup mocks
        mock_scanner = Mock()
        mock_scanner.scan.return_value = []
        mock_scanner_cls.return_value = mock_scanner

        mock_analyzer = Mock()
        mock_repo_info = Mock()
        mock_repo_info.repo_root_path = self.temp_dir
        mock_repo_info.repo_name = 'test_repo'
        mock_repo_info.files = {}
        mock_repo_info.scan_dirs = {}
        mock_analyzer.analyze.return_value = {self.temp_dir: mock_repo_info}
        mock_analyzer.timing = None  # Avoid timing dict subscript error
        mock_analyzer_cls.return_value = mock_analyzer

        # Mock report generator
        mock_report_instance = Mock()
        mock_report_cls = Mock(return_value=mock_report_instance)

        config = AppConfig(
            directories=[self.temp_dir],
            output_format='json',
            level='function',
            hierarchical=True,
            report_folder='custom_output'
        )

        app = MetricMancerApp(config=config, report_generator_cls=mock_report_cls)
        app.run()

        # Verify report.generate was called with config settings
        mock_report_instance.generate.assert_called_once()
        call_kwargs = mock_report_instance.generate.call_args[1]
        self.assertEqual(call_kwargs['level'], 'function')
        self.assertEqual(call_kwargs['hierarchical'], True)
        self.assertEqual(call_kwargs['output_format'], 'json')

    def test_config_validation_on_app_creation(self):
        """Test that invalid config is rejected when creating app."""
        # Create invalid config (thresholds in wrong order)
        invalid_config = AppConfig(
            directories=[self.temp_dir],
            threshold_low=20.0,
            threshold_high=10.0  # Invalid: high < low
        )

        # Should raise ValueError during validation
        with self.assertRaises(ValueError):
            MetricMancerApp(config=invalid_config)

    def test_app_without_any_parameters_raises_error(self):
        """Test that creating app without config or directories raises error."""
        with self.assertRaises(TypeError):
            # Should fail - no config and no directories
            MetricMancerApp()


class TestMetricMancerAppConfigDefaults(unittest.TestCase):
    """Test that AppConfig defaults work correctly with MetricMancerApp."""

    def test_minimal_config_with_defaults(self):
        """Test app creation with minimal config using defaults."""
        config = AppConfig(directories=['/test/path'])
        app = MetricMancerApp(config=config)

        # Should use default values from AppConfig
        self.assertEqual(app.config.threshold_low, 10.0)
        self.assertEqual(app.config.threshold_high, 20.0)
        self.assertEqual(app.config.output_format, 'summary')  # Corrected default
        self.assertEqual(app.config.level, 'file')
        self.assertEqual(app.config.hierarchical, False)
        self.assertEqual(app.config.report_folder, 'output')

    def test_partial_config_overrides(self):
        """Test that partial config correctly overrides only specified values."""
        config = AppConfig(
            directories=['/test/path'],
            threshold_low=5.0,  # Override
            output_format='json'  # Override
            # Other values should use defaults
        )
        app = MetricMancerApp(config=config)

        # Overridden values
        self.assertEqual(app.config.threshold_low, 5.0)
        self.assertEqual(app.config.output_format, 'json')

        # Default values
        self.assertEqual(app.config.threshold_high, 20.0)
        self.assertEqual(app.config.level, 'file')


if __name__ == '__main__':
    unittest.main()
