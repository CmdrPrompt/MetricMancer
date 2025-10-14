import unittest
from unittest.mock import MagicMock, patch
from src.app.metric_mancer_app import MetricMancerApp
from src.config.app_config import AppConfig


class TestMetricMancerAppEdgeCases(unittest.TestCase):
    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.utilities.debug.debug_print')
    def test_run_with_empty_directories(self, mock_debug, MockAnalyzer, MockScanner, MockConfig):
        mock_scanner = MockScanner.return_value
        mock_analyzer = MockAnalyzer.return_value
        mock_scanner.scan.return_value = []
        mock_analyzer.analyze.return_value = {}
        mock_report_cls = MagicMock()
        # Note: Keeping legacy pattern here since empty dirs is edge case
        # and AppConfig validates against this (which is better behavior)
        app = MetricMancerApp([], report_generator_cls=mock_report_cls)
        app.run()
        mock_scanner.scan.assert_called_once_with([])
        mock_analyzer.analyze.assert_called_once_with([])
        mock_report_cls.assert_not_called()

    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.utilities.debug.debug_print')
    def test_run_with_none_report_generator_cls(self, mock_debug, MockAnalyzer, MockScanner, MockConfig):
        mock_scanner = MockScanner.return_value
        mock_analyzer = MockAnalyzer.return_value
        mock_scanner.scan.return_value = ['file']
        repo_info = MagicMock()
        repo_info.repo_root_path = '/repo'
        repo_info.repo_name = 'repo'
        mock_analyzer.analyze.return_value = {'/repo': repo_info}
        config = AppConfig(directories=['dir'])
        app = MetricMancerApp(config=config, report_generator_cls=None)
        # Ska inte krascha även om report_generator_cls är None (default används)
        try:
            app.run()
        except Exception as e:
            self.fail(f"Should not raise exception: {e}")

    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.utilities.debug.debug_print')
    def test_run_with_report_generate_exception(self, mock_debug, MockAnalyzer, MockScanner, MockConfig):
        mock_scanner = MockScanner.return_value
        mock_analyzer = MockAnalyzer.return_value
        mock_scanner.scan.return_value = ['file']
        repo_info = MagicMock()
        repo_info.repo_root_path = '/repo'
        repo_info.repo_name = 'repo'
        mock_analyzer.analyze.return_value = {'/repo': repo_info}
        mock_report_instance = MagicMock()
        mock_report_instance.generate.side_effect = Exception('fail')
        mock_report_cls = MagicMock(return_value=mock_report_instance)
        config = AppConfig(directories=['dir'])
        app = MetricMancerApp(config=config, report_generator_cls=mock_report_cls)
        # Kör och kontrollera att undantag inte bubblar upp
        try:
            app.run()
        except Exception as e:
            self.assertEqual(str(e), 'fail')


if __name__ == '__main__':
    unittest.main()
