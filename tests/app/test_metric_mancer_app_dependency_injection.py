"""
Unit tests for MetricMancerApp Dependency Injection (TDD for Refactoring #8).

These tests verify that dependencies (Scanner, Analyzer, ReportCoordinator) can be
injected for testing purposes, improving testability and following SOLID principles.

RED-GREEN-REFACTOR:
1. RED: These tests will FAIL initially because DI is not implemented yet
2. GREEN: Add optional parameters for injecting dependencies
3. REFACTOR: Clean up and simplify initialization
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
import shutil

from src.config.app_config import AppConfig
from src.app.metric_mancer_app import MetricMancerApp


class TestDependencyInjection(unittest.TestCase):
    """Test that dependencies can be injected into MetricMancerApp."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig(directories=[self.temp_dir])

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_can_inject_scanner(self):
        """Test that Scanner can be injected via constructor."""
        # This test will FAIL initially - that's expected in TDD!
        mock_scanner = Mock()

        app = MetricMancerApp(config=self.config, scanner=mock_scanner)

        # Should use injected scanner instead of creating new one
        self.assertIs(app.scanner, mock_scanner)

    def test_can_inject_analyzer(self):
        """Test that Analyzer can be injected via constructor."""
        mock_analyzer = Mock()

        app = MetricMancerApp(config=self.config, analyzer=mock_analyzer)

        # Should use injected analyzer instead of creating new one
        self.assertIs(app.analyzer, mock_analyzer)

    def test_can_inject_both_scanner_and_analyzer(self):
        """Test that both Scanner and Analyzer can be injected together."""
        mock_scanner = Mock()
        mock_analyzer = Mock()

        app = MetricMancerApp(
            config=self.config,
            scanner=mock_scanner,
            analyzer=mock_analyzer
        )

        # Should use both injected dependencies
        self.assertIs(app.scanner, mock_scanner)
        self.assertIs(app.analyzer, mock_analyzer)

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_creates_default_scanner_if_not_injected(self, mock_analyzer_cls, mock_scanner_cls):
        """Test that Scanner is created if not injected."""
        app = MetricMancerApp(config=self.config)

        # Should have created Scanner (not None)
        self.assertIsNotNone(app.scanner)
        # Should have called Scanner constructor
        mock_scanner_cls.assert_called_once()

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_creates_default_analyzer_if_not_injected(self, mock_analyzer_cls, mock_scanner_cls):
        """Test that Analyzer is created if not injected."""
        app = MetricMancerApp(config=self.config)

        # Should have created Analyzer (not None)
        self.assertIsNotNone(app.analyzer)
        # Should have called Analyzer constructor with config values
        mock_analyzer_cls.assert_called_once()
        call_kwargs = mock_analyzer_cls.call_args[1]
        self.assertEqual(call_kwargs['threshold_low'], self.config.threshold_low)
        self.assertEqual(call_kwargs['threshold_high'], self.config.threshold_high)

    @patch('src.app.metric_mancer_app.Scanner')
    def test_injected_scanner_not_overwritten(self, mock_scanner_cls):
        """Test that injected Scanner is not overwritten by default creation."""
        mock_scanner = Mock()

        app = MetricMancerApp(config=self.config, scanner=mock_scanner)

        # Should NOT have called Scanner constructor
        mock_scanner_cls.assert_not_called()
        # Should still use injected scanner
        self.assertIs(app.scanner, mock_scanner)

    @patch('src.app.metric_mancer_app.Analyzer')
    def test_injected_analyzer_not_overwritten(self, mock_analyzer_cls):
        """Test that injected Analyzer is not overwritten by default creation."""
        mock_analyzer = Mock()

        app = MetricMancerApp(config=self.config, analyzer=mock_analyzer)

        # Should NOT have called Analyzer constructor
        mock_analyzer_cls.assert_not_called()
        # Should still use injected analyzer
        self.assertIs(app.analyzer, mock_analyzer)


class TestDependencyInjectionInRun(unittest.TestCase):
    """Test that injected dependencies are used in run() method."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig(directories=[self.temp_dir])

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_uses_injected_scanner(self):
        """Test that run() method uses injected Scanner."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = []

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {}
        mock_analyzer.timing = None

        app = MetricMancerApp(
            config=self.config,
            scanner=mock_scanner,
            analyzer=mock_analyzer
        )
        app.run()

        # Should have called scan() on injected scanner
        mock_scanner.scan.assert_called_once_with(self.config.directories)

    def test_run_uses_injected_analyzer(self):
        """Test that run() method uses injected Analyzer."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = ['file1.py', 'file2.py']

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {}
        mock_analyzer.timing = None

        app = MetricMancerApp(
            config=self.config,
            scanner=mock_scanner,
            analyzer=mock_analyzer
        )
        app.run()

        # Should have called analyze() on injected analyzer
        mock_analyzer.analyze.assert_called_once_with(['file1.py', 'file2.py'])


class TestDependencyInjectionDocumentation(unittest.TestCase):
    """Test that dependency injection is documented."""

    def test_init_docstring_mentions_dependency_injection(self):
        """Test that __init__ docstring mentions dependency injection parameters."""
        from src.app.metric_mancer_app import MetricMancerApp

        docstring = MetricMancerApp.__init__.__doc__
        self.assertIsNotNone(docstring, "__init__ should have a docstring")

        # Docstring should mention scanner and analyzer parameters
        # (or at least one of them for DI)
        mentions_di = ('scanner' in docstring.lower() or
                      'analyzer' in docstring.lower() or
                      'inject' in docstring.lower())
        self.assertTrue(mentions_di,
                       "Docstring should mention dependency injection parameters")


class TestBackwardCompatibilityWithDI(unittest.TestCase):
    """Test that DI doesn't break existing code."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig(directories=[self.temp_dir])

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_existing_code_without_di_still_works(self, mock_analyzer_cls, mock_scanner_cls):
        """Test that existing code (without DI) still works as before."""
        # Simulate existing code that doesn't use DI
        app = MetricMancerApp(config=self.config)

        # Should still create dependencies automatically
        self.assertIsNotNone(app.scanner)
        self.assertIsNotNone(app.analyzer)
        mock_scanner_cls.assert_called_once()
        mock_analyzer_cls.assert_called_once()

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_report_generator_cls_still_works_with_di(self, mock_analyzer_cls, mock_scanner_cls):
        """Test that report_generator_cls parameter still works alongside DI."""
        mock_report_cls = Mock()
        mock_scanner = Mock()
        mock_analyzer = Mock()

        app = MetricMancerApp(
            config=self.config,
            scanner=mock_scanner,
            analyzer=mock_analyzer,
            report_generator_cls=mock_report_cls
        )

        # Should have both DI and report_generator_cls
        self.assertIs(app.scanner, mock_scanner)
        self.assertIs(app.analyzer, mock_analyzer)
        self.assertIs(app.report_generator_cls, mock_report_cls)


if __name__ == '__main__':
    unittest.main()
