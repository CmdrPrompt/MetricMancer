import unittest
from unittest.mock import MagicMock, patch
from src.app.metric_mancer_app import MetricMancerApp
from src.config.app_config import AppConfig


class TestMetricMancerApp(unittest.TestCase):
    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    def test_init_sets_attributes(self, MockAnalyzer, MockScanner, MockConfig):
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
        app = MetricMancerApp(config=config)
        # After Refactoring #6: Use app.app_config instead of duplicate attributes
        self.assertEqual(app.app_config.directories, ['dir1', 'dir2'])
        self.assertEqual(app.app_config.threshold_low, 1)
        self.assertEqual(app.app_config.threshold_high, 2)
        self.assertEqual(app.app_config.problem_file_threshold, 3)
        self.assertEqual(app.app_config.output_file, 'out.html')
        self.assertEqual(app.app_config.level, 'file')
        self.assertTrue(app.app_config.hierarchical)
        self.assertEqual(app.app_config.output_format, 'human')
        self.assertIsNotNone(app.config)  # Backward compatibility alias
        self.assertIs(app.config, app.app_config)  # Should be same object
        self.assertIsNotNone(app.scanner)
        self.assertIsNotNone(app.analyzer)

    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.utilities.debug.debug_print')
    def test_run_single_repo(self, mock_debug, MockAnalyzer, MockScanner, MockConfig):
        # Setup mocks
        mock_scanner = MockScanner.return_value
        mock_analyzer = MockAnalyzer.return_value
        mock_report_instance = MagicMock()
        mock_report_cls = MagicMock(return_value=mock_report_instance)
        mock_scanner.scan.return_value = ['file1', 'file2']
        repo_info = MagicMock()
        repo_info.repo_root_path = '/repo'
        repo_info.repo_name = 'repo'
        mock_analyzer.analyze.return_value = {'/repo': repo_info}
        config = AppConfig(
            directories=['dir'],
            output_file='report.html',
            output_format='human'  # Match legacy default
        )
        app = MetricMancerApp(config=config, report_generator_cls=mock_report_cls)
        app.run()
        mock_scanner.scan.assert_called_once_with(['dir'])
        mock_analyzer.analyze.assert_called_once_with(['file1', 'file2'])
        mock_report_cls.assert_called_once_with(repo_info, 10.0, 20.0, None)
        mock_report_instance.generate.assert_called_once()
        args, kwargs = mock_report_instance.generate.call_args
        self.assertEqual(kwargs['output_file'], 'output/report.html')
        self.assertEqual(kwargs['level'], 'file')
        self.assertEqual(kwargs['hierarchical'], False)
        self.assertEqual(kwargs['output_format'], 'human')
        self.assertEqual(kwargs['report_links'], [])

    @patch('src.app.metric_mancer_app.Config')
    @patch('src.app.metric_mancer_app.Scanner')
    @patch('src.app.metric_mancer_app.Analyzer')
    @patch('src.utilities.debug.debug_print')
    def test_run_multiple_repos(self, mock_debug, MockAnalyzer, MockScanner, MockConfig):
        mock_scanner = MockScanner.return_value
        mock_analyzer = MockAnalyzer.return_value
        mock_report_instance = MagicMock()
        mock_report_cls = MagicMock(return_value=mock_report_instance)
        mock_scanner.scan.return_value = ['file1', 'file2']
        repo_info1 = MagicMock()
        repo_info1.repo_root_path = '/repo1'
        repo_info1.repo_name = 'repo1'
        repo_info2 = MagicMock()
        repo_info2.repo_root_path = '/repo2'
        repo_info2.repo_name = 'repo2'
        mock_analyzer.analyze.return_value = {'/repo1': repo_info1, '/repo2': repo_info2}
        config = AppConfig(
            directories=['dir'],
            output_file='report.html',
            output_format='human'  # Match legacy default
        )
        app = MetricMancerApp(config=config, report_generator_cls=mock_report_cls)
        app.run()
        self.assertEqual(mock_report_cls.call_count, 2)
        self.assertEqual(mock_report_instance.generate.call_count, 2)
        # Check that output_file is suffixed for each repo and includes report_folder
        call_args = [call[1]['output_file'] for call in mock_report_instance.generate.call_args_list]
        self.assertIn('output/report_1.html', call_args)
        self.assertIn('output/report_2.html', call_args)


if __name__ == '__main__':
    unittest.main()
