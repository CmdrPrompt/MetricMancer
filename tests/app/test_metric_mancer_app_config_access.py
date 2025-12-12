"""
Unit tests for MetricMancerApp config access patterns (TDD for Refactoring #6).

These tests verify that all config values can be accessed via app.app_config
instead of duplicated instance attributes. This eliminates _expose_config_attributes.

RED-GREEN-REFACTOR:
1. RED: These tests will FAIL initially because we still have duplicate attributes
2. GREEN: Remove _expose_config_attributes and use app.app_config everywhere
3. REFACTOR: Clean up any remaining legacy attribute access

Note: Some tests intentionally use deprecated legacy parameters to verify
backward compatibility. DeprecationWarnings are suppressed in those tests.
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
import shutil

from src.config.app_config import AppConfig
from src.app.metric_mancer_app import MetricMancerApp


class TestMetricMancerAppConfigAccess(unittest.TestCase):
    """Test that config values are accessed via app.app_config (not duplicate attributes)."""

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
            churn_period=90,
            debug=True
        )

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_app_config_attribute_exists(self):
        """Test that app.app_config exists and contains all configuration."""
        app = MetricMancerApp(config=self.config)

        # app.app_config should be the primary source of truth
        self.assertIsNotNone(app.app_config)
        self.assertIsInstance(app.app_config, AppConfig)
        self.assertEqual(app.app_config.directories, [self.temp_dir])

    def test_app_config_contains_all_settings(self):
        """Test that app.app_config contains all configuration settings."""
        app = MetricMancerApp(config=self.config)

        # All config values should be accessible via app.app_config
        self.assertEqual(app.app_config.threshold_low, 5.0)
        self.assertEqual(app.app_config.threshold_high, 15.0)
        self.assertEqual(app.app_config.problem_file_threshold, 10)
        self.assertEqual(app.app_config.output_file, 'test_report.html')
        self.assertEqual(app.app_config.level, 'function')
        self.assertEqual(app.app_config.hierarchical, True)
        self.assertEqual(app.app_config.output_format, 'json')
        self.assertEqual(app.app_config.report_folder, 'test_output')
        self.assertEqual(app.app_config.list_hotspots, True)
        self.assertEqual(app.app_config.hotspot_threshold, 75)
        self.assertEqual(app.app_config.hotspot_output, 'hotspots.txt')
        self.assertEqual(app.app_config.review_strategy, True)
        self.assertEqual(app.app_config.review_output, 'review.md')
        self.assertEqual(app.app_config.review_branch_only, True)
        self.assertEqual(app.app_config.review_base_branch, 'develop')
        self.assertEqual(app.app_config.churn_period, 90)
        self.assertEqual(app.app_config.debug, True)

    def test_no_duplicate_attributes_for_directories(self):
        """Test that directories is not duplicated as instance attribute."""
        app = MetricMancerApp(config=self.config)

        # Should NOT have self.directories (only self.app_config.directories)
        # This test will FAIL initially - that's expected!
        if hasattr(app, 'directories'):
            self.fail("app.directories should not exist - use app.app_config.directories instead")

    def test_no_duplicate_attributes_for_thresholds(self):
        """Test that thresholds are not duplicated as instance attributes."""
        app = MetricMancerApp(config=self.config)

        # Should NOT have duplicate threshold attributes
        if hasattr(app, 'threshold_low'):
            self.fail("app.threshold_low should not exist - use app.app_config.threshold_low instead")
        if hasattr(app, 'threshold_high'):
            self.fail("app.threshold_high should not exist - use app.app_config.threshold_high instead")
        if hasattr(app, 'problem_file_threshold'):
            self.fail("app.problem_file_threshold should not exist - use app.app_config.problem_file_threshold instead")

    def test_no_duplicate_attributes_for_output_settings(self):
        """Test that output settings are not duplicated as instance attributes."""
        app = MetricMancerApp(config=self.config)

        # Should NOT have duplicate output attributes
        if hasattr(app, 'output_file'):
            self.fail("app.output_file should not exist - use app.app_config.output_file instead")
        if hasattr(app, 'output_format'):
            self.fail("app.output_format should not exist - use app.app_config.output_format instead")
        if hasattr(app, 'level'):
            self.fail("app.level should not exist - use app.app_config.level instead")
        if hasattr(app, 'hierarchical'):
            self.fail("app.hierarchical should not exist - use app.app_config.hierarchical instead")
        if hasattr(app, 'report_folder'):
            self.fail("app.report_folder should not exist - use app.app_config.report_folder instead")

    def test_no_duplicate_attributes_for_hotspot_settings(self):
        """Test that hotspot settings are not duplicated as instance attributes."""
        app = MetricMancerApp(config=self.config)

        # Should NOT have duplicate hotspot attributes
        if hasattr(app, 'list_hotspots'):
            self.fail("app.list_hotspots should not exist - use app.app_config.list_hotspots instead")
        if hasattr(app, 'hotspot_threshold'):
            self.fail("app.hotspot_threshold should not exist - use app.app_config.hotspot_threshold instead")
        if hasattr(app, 'hotspot_output'):
            self.fail("app.hotspot_output should not exist - use app.app_config.hotspot_output instead")

    def test_no_duplicate_attributes_for_review_settings(self):
        """Test that review settings are not duplicated as instance attributes."""
        app = MetricMancerApp(config=self.config)

        # Should NOT have duplicate review attributes
        if hasattr(app, 'review_strategy'):
            self.fail("app.review_strategy should not exist - use app.app_config.review_strategy instead")
        if hasattr(app, 'review_output'):
            self.fail("app.review_output should not exist - use app.app_config.review_output instead")
        if hasattr(app, 'review_branch_only'):
            self.fail("app.review_branch_only should not exist - use app.app_config.review_branch_only instead")
        if hasattr(app, 'review_base_branch'):
            self.fail("app.review_base_branch should not exist - use app.app_config.review_base_branch instead")

    def test_no_duplicate_attributes_for_churn_period(self):
        """Test that churn_period is not duplicated as instance attribute."""
        app = MetricMancerApp(config=self.config)

        # Should NOT have duplicate churn_period attribute
        if hasattr(app, 'churn_period'):
            self.fail("app.churn_period should not exist - use app.app_config.churn_period instead")

    def test_backward_compatibility_config_alias(self):
        """Test that app.config still exists as alias for app.app_config (backward compatibility)."""
        app = MetricMancerApp(config=self.config)

        # app.config should exist as alias to app.app_config
        self.assertIsNotNone(app.config)
        self.assertIs(app.config, app.app_config)  # Should be same object

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_internal_methods_use_app_config(self, mock_analyzer_cls, mock_scanner_cls):
        """Test that internal methods use app.app_config (not duplicate attributes)."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = []
        mock_scanner_cls.return_value = mock_scanner

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {}
        mock_analyzer.timing = None
        mock_analyzer_cls.return_value = mock_analyzer

        app = MetricMancerApp(config=self.config)

        # _scan_files should use app.app_config.directories (not app.directories)
        app._scan_files()
        mock_scanner.scan.assert_called_once_with(self.config.directories)

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_run_method_uses_app_config_directly(self, mock_analyzer_cls, mock_scanner_cls):
        """Test that run() method uses app.app_config throughout."""
        # Setup mocks
        mock_scanner = Mock()
        mock_scanner.scan.return_value = []
        mock_scanner_cls.return_value = mock_scanner

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {}  # Empty dict means no repos
        mock_analyzer.timing = None
        mock_analyzer_cls.return_value = mock_analyzer

        app = MetricMancerApp(config=self.config)
        app.run()

        # Scanner should be called with app.app_config.directories (not app.directories)
        mock_scanner.scan.assert_called_once_with(self.config.directories)


if __name__ == '__main__':
    unittest.main()
