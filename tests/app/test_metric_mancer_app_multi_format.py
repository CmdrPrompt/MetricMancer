"""
TDD tests for multi-format report generation in MetricMancerApp.

Phase 3: MetricMancerApp.run() Multi-Format Support

These tests verify that MetricMancerApp correctly:
1. Loops over config.output_formats instead of using singular format
2. Generates separate files for each format
3. Reuses scan/analysis results (doesn't re-scan)
4. Handles multiple repos with multiple formats
5. Maintains backward compatibility with single format
"""

import tempfile
from unittest.mock import Mock, patch
from src.app.metric_mancer_app import MetricMancerApp
from src.config.app_config import AppConfig


class TestMetricMancerAppMultiFormat:
    """Test MetricMancerApp with multiple output formats."""

    def test_app_uses_output_formats_from_config(self):
        """Test that app accesses config.output_formats."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json']
        )

        app = MetricMancerApp(config=config)

        assert hasattr(app.config, 'output_formats')
        assert app.config.output_formats == ['html', 'json']

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.app.metric_mancer_app.os.makedirs')
    def test_run_loops_over_multiple_formats(self, mock_makedirs, mock_analyzer_cls, mock_scanner_cls):
        """Test that run() loops over all formats in config.output_formats."""
        # Setup mocks
        mock_scanner = Mock()
        mock_scanner.scan.return_value = ['file1.py', 'file2.py']
        mock_scanner_cls.return_value = mock_scanner

        mock_repo_info = Mock()
        mock_repo_info.repo_root_path = '/test/path'
        mock_repo_info.repo_name = 'test_repo'

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {'/test/path': mock_repo_info}
        mock_analyzer.timing = {}
        mock_analyzer_cls.return_value = mock_analyzer

        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json', 'summary'],
            report_folder='output'
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config.report_folder = tmpdir

            # Mock report generator
            mock_report_gen = Mock()
            mock_report_gen_cls = Mock(return_value=mock_report_gen)

            app = MetricMancerApp(config=config, report_generator_cls=mock_report_gen_cls)
            app.run()

            # Should call report generator 3 times (once per format)
            assert mock_report_gen_cls.call_count == 3
            assert mock_report_gen.generate.call_count == 3

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.app.metric_mancer_app.os.makedirs')
    def test_run_scans_only_once_for_multiple_formats(self, mock_makedirs, mock_analyzer_cls, mock_scanner_cls):
        """Test that scanner.scan() is called only once regardless of format count."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = ['file1.py']
        mock_scanner_cls.return_value = mock_scanner

        mock_repo_info = Mock()
        mock_repo_info.repo_root_path = '/test'
        mock_repo_info.repo_name = 'test'

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {'/test': mock_repo_info}
        mock_analyzer.timing = {}
        mock_analyzer_cls.return_value = mock_analyzer

        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json', 'summary']  # 3 formats
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config.report_folder = tmpdir
            mock_report_gen_cls = Mock(return_value=Mock())
            app = MetricMancerApp(config=config, report_generator_cls=mock_report_gen_cls)
            app.run()

            # Scanner should be called exactly once
            assert mock_scanner.scan.call_count == 1

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.app.metric_mancer_app.os.makedirs')
    def test_run_analyzes_only_once_for_multiple_formats(self, mock_makedirs, mock_analyzer_cls, mock_scanner_cls):
        """Test that analyzer.analyze() is called only once regardless of format count."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = ['file1.py']
        mock_scanner_cls.return_value = mock_scanner

        mock_repo_info = Mock()
        mock_repo_info.repo_root_path = '/test'
        mock_repo_info.repo_name = 'test'

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {'/test': mock_repo_info}
        mock_analyzer.timing = {}
        mock_analyzer_cls.return_value = mock_analyzer

        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json', 'summary']  # 3 formats
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config.report_folder = tmpdir
            mock_report_gen_cls = Mock(return_value=Mock())
            app = MetricMancerApp(config=config, report_generator_cls=mock_report_gen_cls)
            app.run()

            # Analyzer should be called exactly once
            assert mock_analyzer.analyze.call_count == 1


class TestMetricMancerAppMultiFormatFilenames:
    """Test filename generation for multiple formats."""

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.app.metric_mancer_app.os.makedirs')
    def test_generates_separate_files_per_format(self, mock_makedirs, mock_analyzer_cls, mock_scanner_cls):
        """Test that separate output files are created for each format."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = ['file1.py']
        mock_scanner_cls.return_value = mock_scanner

        mock_repo_info = Mock()
        mock_repo_info.repo_root_path = '/test'
        mock_repo_info.repo_name = 'test'

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {'/test': mock_repo_info}
        mock_analyzer.timing = {}
        mock_analyzer_cls.return_value = mock_analyzer

        # Mock report generator for each format
        mock_report = Mock()
        mock_report_gen = Mock(return_value=mock_report)

        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json'],
            output_file='report.html'  # Base filename
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config.report_folder = tmpdir
            app = MetricMancerApp(config=config, report_generator_cls=mock_report_gen)
            app.run()

            # Check that generate was called with different output files
            assert mock_report.generate.call_count == 2
            # Files should be named differently based on format

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.app.metric_mancer_app.os.makedirs')
    def test_filename_includes_format_suffix(self, mock_makedirs, mock_analyzer_cls, mock_scanner_cls):
        """Test that generated filenames include format suffix."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = ['file1.py']
        mock_scanner_cls.return_value = mock_scanner

        mock_repo_info = Mock()
        mock_repo_info.repo_root_path = '/test'
        mock_repo_info.repo_name = 'test'

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {'/test': mock_repo_info}
        mock_analyzer.timing = {}
        mock_analyzer_cls.return_value = mock_analyzer

        mock_report = Mock()
        mock_report_gen_cls = Mock(return_value=mock_report)

        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json']
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config.report_folder = tmpdir
            app = MetricMancerApp(config=config, report_generator_cls=mock_report_gen_cls)
            app.run()

            # Check filenames passed to generate()
            generate_calls = mock_report.generate.call_args_list
            assert len(generate_calls) == 2

            # Extract output_file arguments
            output_files = [c.kwargs.get('output_file') or c[1].get('output_file', c[0][0])
                            for c in generate_calls]

            # Should have different filenames
            assert len(set(output_files)) == 2


class TestMetricMancerAppBackwardCompatibility:
    """Test backward compatibility with single format."""

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.app.metric_mancer_app.os.makedirs')
    def test_single_format_still_works(self, mock_makedirs, mock_analyzer_cls, mock_scanner_cls):
        """Test that single output_format (legacy) still works."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = ['file1.py']
        mock_scanner_cls.return_value = mock_scanner

        mock_repo_info = Mock()
        mock_repo_info.repo_root_path = '/test'
        mock_repo_info.repo_name = 'test'

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {'/test': mock_repo_info}
        mock_analyzer.timing = {}
        mock_analyzer_cls.return_value = mock_analyzer

        # Use singular output_format (old way)
        config = AppConfig(
            directories=['src'],
            output_format='html'  # Singular
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config.report_folder = tmpdir
            mock_report_gen_cls = Mock(return_value=Mock())
            app = MetricMancerApp(config=config, report_generator_cls=mock_report_gen_cls)
            app.run()

            # Should work and generate one report
            assert mock_report_gen_cls.call_count >= 1

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.app.metric_mancer_app.os.makedirs')
    def test_default_format_works(self, mock_makedirs, mock_analyzer_cls, mock_scanner_cls):
        """Test that default format (summary) still works."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = ['file1.py']
        mock_scanner_cls.return_value = mock_scanner

        mock_repo_info = Mock()
        mock_repo_info.repo_root_path = '/test'
        mock_repo_info.repo_name = 'test'

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {'/test': mock_repo_info}
        mock_analyzer.timing = {}
        mock_analyzer_cls.return_value = mock_analyzer

        # No format specified, should use default
        config = AppConfig(directories=['src'])

        with tempfile.TemporaryDirectory() as tmpdir:
            config.report_folder = tmpdir
            mock_report_gen_cls = Mock(return_value=Mock())
            app = MetricMancerApp(config=config, report_generator_cls=mock_report_gen_cls)
            app.run()

            # Should work with default format
            assert mock_report_gen_cls.call_count >= 1


class TestMetricMancerAppMultiRepoMultiFormat:
    """Test combination of multiple repos and multiple formats."""

    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.app.metric_mancer_app.os.makedirs')
    def test_multiple_repos_multiple_formats(self, mock_makedirs, mock_analyzer_cls, mock_scanner_cls):
        """Test that multiple repos × multiple formats works correctly."""
        mock_scanner = Mock()
        mock_scanner.scan.return_value = ['file1.py', 'file2.py']
        mock_scanner_cls.return_value = mock_scanner

        # Two repos
        mock_repo_info1 = Mock()
        mock_repo_info1.repo_root_path = '/test/repo1'
        mock_repo_info1.repo_name = 'repo1'

        mock_repo_info2 = Mock()
        mock_repo_info2.repo_root_path = '/test/repo2'
        mock_repo_info2.repo_name = 'repo2'

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = {
            '/test/repo1': mock_repo_info1,
            '/test/repo2': mock_repo_info2
        }
        mock_analyzer.timing = {}
        mock_analyzer_cls.return_value = mock_analyzer

        config = AppConfig(
            directories=['src', 'tests'],
            output_formats=['html', 'json']  # 2 formats
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config.report_folder = tmpdir
            mock_report_gen_cls = Mock(return_value=Mock())
            app = MetricMancerApp(config=config, report_generator_cls=mock_report_gen_cls)
            app.run()

            # Should generate: 2 repos × 2 formats = 4 reports
            assert mock_report_gen_cls.call_count == 4
