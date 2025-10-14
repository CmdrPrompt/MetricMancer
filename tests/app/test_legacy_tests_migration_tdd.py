"""
TDD tests for verifying legacy test migration to AppConfig pattern.

These tests are written BEFORE migrating existing tests to verify that:
1. AppConfig can represent all parameter combinations used in legacy tests
2. MetricMancerApp behavior is identical with AppConfig vs individual params
3. Migration is safe and won't break existing functionality

These tests will initially PASS (showing compatibility exists),
then guide the migration of actual test files.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.config.app_config import AppConfig
from src.app.metric_mancer_app import MetricMancerApp


class TestLegacyTestMigrationCompatibility(unittest.TestCase):
    """Verify that AppConfig can replace all legacy parameter patterns."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_legacy_init_pattern_equivalence(self, MockAnalyzer, MockScanner, MockConfig):
        """Test that AppConfig produces same result as legacy parameters."""
        # Legacy pattern (from test_metric_mancer_app.py:11)
        legacy_app = MetricMancerApp(
            ['dir1', 'dir2'],
            threshold_low=1,
            threshold_high=2,
            problem_file_threshold=3,
            output_file='out.html',
            level='file',
            hierarchical=True,
            output_format='human'
        )

        # New AppConfig pattern
        config = AppConfig(
            directories=['dir1', 'dir2'],
            threshold_low=1,
            threshold_high=2,
            problem_file_threshold=3,
            output_file='out.html',
            level='file',
            hierarchical=True,
            output_format='human'
        )
        new_app = MetricMancerApp(config=config)

        # Verify identical attributes
        self.assertEqual(legacy_app.directories, new_app.directories)
        self.assertEqual(legacy_app.threshold_low, new_app.threshold_low)
        self.assertEqual(legacy_app.threshold_high, new_app.threshold_high)
        self.assertEqual(legacy_app.problem_file_threshold, new_app.problem_file_threshold)
        self.assertEqual(legacy_app.output_file, new_app.output_file)
        self.assertEqual(legacy_app.level, new_app.level)
        self.assertEqual(legacy_app.hierarchical, new_app.hierarchical)
        self.assertEqual(legacy_app.output_format, new_app.output_format)

    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_legacy_minimal_params_equivalence(self, MockAnalyzer, MockScanner, MockConfig):
        """Test AppConfig with minimal parameters (from test_metric_mancer_app.py:39)."""
        mock_report_cls = MagicMock()

        # Legacy pattern
        legacy_app = MetricMancerApp(
            ['dir'],
            output_file='report.html',
            report_generator_cls=mock_report_cls
        )

        # New AppConfig pattern
        config = AppConfig(
            directories=['dir'],
            output_file='report.html'
        )
        new_app = MetricMancerApp(config=config, report_generator_cls=mock_report_cls)

        # Verify identical attributes
        self.assertEqual(legacy_app.directories, new_app.directories)
        self.assertEqual(legacy_app.output_file, new_app.output_file)
        self.assertEqual(legacy_app.report_generator_cls, new_app.report_generator_cls)

    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_legacy_edge_case_empty_dirs(self, MockAnalyzer, MockScanner, MockConfig):
        """Test AppConfig with empty directories (from test_metric_mancer_app_edge.py:17).

        Note: Legacy pattern allows empty dirs, but AppConfig validates.
        For migration, we'll need to handle this edge case specially.
        This test documents the difference - legacy test should stay as-is.
        """
        mock_report_cls = MagicMock()

        # Legacy pattern - allows empty directories
        legacy_app = MetricMancerApp([], report_generator_cls=mock_report_cls)
        self.assertEqual(legacy_app.directories, [])

        # New AppConfig pattern - validates and rejects empty dirs
        # This is actually BETTER behavior (fail fast), but for backward compat
        # during migration, this specific edge case test should keep legacy pattern
        with self.assertRaises(ValueError) as cm:
            config = AppConfig(directories=[])
            MetricMancerApp(config=config, report_generator_cls=mock_report_cls)

        self.assertIn("At least one directory", str(cm.exception))

    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_legacy_report_generator_cls_none(self, MockAnalyzer, MockScanner, MockConfig):
        """Test AppConfig with None report_generator_cls (from test_metric_mancer_app_edge.py:35)."""
        # Legacy pattern
        legacy_app = MetricMancerApp(['dir'], report_generator_cls=None)

        # New AppConfig pattern
        config = AppConfig(directories=['dir'])
        new_app = MetricMancerApp(config=config, report_generator_cls=None)

        # Verify both use default ReportGenerator
        self.assertIsNotNone(legacy_app.report_generator_cls)
        self.assertIsNotNone(new_app.report_generator_cls)
        self.assertEqual(
            legacy_app.report_generator_cls.__name__,
            new_app.report_generator_cls.__name__
        )


class TestLegacyTestBehaviorEquivalence(unittest.TestCase):
    """Verify that runtime behavior is identical between legacy and AppConfig patterns."""

    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.utilities.debug.debug_print')
    def test_run_behavior_identical(self, mock_debug, MockAnalyzer, MockScanner, MockConfig):
        """Test that run() behavior is identical with AppConfig."""
        # Setup mocks identically for both
        mock_scanner1 = Mock()
        mock_scanner1.scan.return_value = ['file1', 'file2']
        MockScanner.return_value = mock_scanner1

        mock_analyzer1 = Mock()
        repo_info = Mock()
        repo_info.repo_root_path = '/repo'
        repo_info.repo_name = 'repo'
        mock_analyzer1.analyze.return_value = {'/repo': repo_info}
        mock_analyzer1.timing = None
        MockAnalyzer.return_value = mock_analyzer1

        mock_report_instance1 = MagicMock()
        mock_report_cls1 = MagicMock(return_value=mock_report_instance1)

        # Run with legacy pattern
        legacy_app = MetricMancerApp(['dir'], output_file='report.html',
                                     report_generator_cls=mock_report_cls1)
        legacy_app.run()

        # Capture legacy calls
        legacy_scan_call = mock_scanner1.scan.call_args
        legacy_analyze_call = mock_analyzer1.analyze.call_args
        legacy_generate_call = mock_report_instance1.generate.call_args

        # Reset mocks
        MockScanner.reset_mock()
        MockAnalyzer.reset_mock()
        mock_scanner1.scan.reset_mock()
        mock_analyzer1.analyze.reset_mock()
        mock_report_instance1.generate.reset_mock()

        # Setup mocks again for AppConfig version
        mock_scanner2 = Mock()
        mock_scanner2.scan.return_value = ['file1', 'file2']
        MockScanner.return_value = mock_scanner2

        mock_analyzer2 = Mock()
        mock_analyzer2.analyze.return_value = {'/repo': repo_info}
        mock_analyzer2.timing = None
        MockAnalyzer.return_value = mock_analyzer2

        mock_report_instance2 = MagicMock()
        mock_report_cls2 = MagicMock(return_value=mock_report_instance2)

        # Run with AppConfig pattern
        # Note: Must specify output_format='human' to match legacy default
        config = AppConfig(directories=['dir'], output_file='report.html', output_format='human')
        new_app = MetricMancerApp(config=config, report_generator_cls=mock_report_cls2)
        new_app.run()

        # Capture AppConfig calls
        new_scan_call = mock_scanner2.scan.call_args
        new_analyze_call = mock_analyzer2.analyze.call_args
        new_generate_call = mock_report_instance2.generate.call_args

        # Verify identical behavior
        self.assertEqual(legacy_scan_call, new_scan_call)
        self.assertEqual(legacy_analyze_call, new_analyze_call)

        # Verify generate call parameters are identical
        legacy_kwargs = legacy_generate_call[1]
        new_kwargs = new_generate_call[1]
        self.assertEqual(legacy_kwargs['output_file'], new_kwargs['output_file'])
        self.assertEqual(legacy_kwargs['level'], new_kwargs['level'])
        self.assertEqual(legacy_kwargs['hierarchical'], new_kwargs['hierarchical'])
        self.assertEqual(legacy_kwargs['output_format'], new_kwargs['output_format'])


class TestLegacyTestMigrationSafety(unittest.TestCase):
    """Verify that migrating tests won't break anything."""

    def test_appconfig_supports_all_legacy_parameters(self):
        """Verify AppConfig dataclass has all fields needed by legacy tests."""
        # All parameters used in test_metric_mancer_app.py and test_metric_mancer_app_edge.py
        required_fields = [
            'directories',
            'threshold_low',
            'threshold_high',
            'problem_file_threshold',
            'output_file',
            'level',
            'hierarchical',
            'output_format',
            'report_folder',
            'list_hotspots',
            'hotspot_threshold',
            'hotspot_output',
            'review_strategy',
            'review_output',
            'review_branch_only',
            'review_base_branch',
            'debug'
        ]

        config = AppConfig(directories=['/test'])

        for field in required_fields:
            self.assertTrue(
                hasattr(config, field),
                f"AppConfig missing field '{field}' needed by legacy tests"
            )

    def test_metricmancerapp_accepts_both_patterns(self):
        """Verify MetricMancerApp can accept both legacy params and AppConfig."""
        # This should not raise any errors
        try:
            # Legacy pattern
            with patch('src.app.metric_mancer_app.Config'), \
                    patch('src.app.metric_mancer_app.Scanner'), \
                    patch('src.app.metric_mancer_app.Analyzer'):
                app1 = MetricMancerApp(['dir'], threshold_low=5.0)
                self.assertIsNotNone(app1)

            # AppConfig pattern
            with patch('src.app.metric_mancer_app.Config'), \
                    patch('src.app.metric_mancer_app.Scanner'), \
                    patch('src.app.metric_mancer_app.Analyzer'):
                config = AppConfig(directories=['dir'], threshold_low=5.0)
                app2 = MetricMancerApp(config=config)
                self.assertIsNotNone(app2)

        except Exception as e:
            self.fail(f"MetricMancerApp should accept both patterns: {e}")


if __name__ == '__main__':
    unittest.main()
