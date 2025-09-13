import unittest
from unittest.mock import patch, MagicMock

from src.app.app import ComplexityScannerApp


class TestComplexityScannerApp(unittest.TestCase):
    def _repo_info(self, root='/repo', name='repo', files_count=1):
        class RepoInfo:
            pass
        r = RepoInfo()
        r.repo_root = root
        r.repo_name = name
        r.files = [1] * files_count
        r.results = {'python': {root: []}}
        return r

    @patch('src.utilities.debug.debug_print', lambda *a, **k: None)
    @patch('src.app.app.Analyzer')
    @patch('src.app.app.Scanner')
    @patch('src.app.app.Config')
    def test_default_report_generator_called_with_single_repo_info(self, MockConfig, MockScanner, MockAnalyzer):
        # Arrange
        mock_scanner = MockScanner.return_value
        mock_scanner.scan.return_value = ['a.py', 'b.py']
        mock_analyzer = MockAnalyzer.return_value
        repo_info = self._repo_info()
        mock_analyzer.analyze.return_value = {repo_info.repo_root: repo_info}

        ReportGenMock = MagicMock()
        ReportGenMock.__name__ = 'SomeOtherGenerator'  # not CLI/JSON
        thresholds = (11.0, 21.0)

        app = ComplexityScannerApp(
            directories=['/x'],
            threshold_low=thresholds[0],
            threshold_high=thresholds[1],
            problem_file_threshold=3.0,
            output_file='out.html',
            report_generator_cls=ReportGenMock
        )

        # Act
        app.run()

        # Assert
        ReportGenMock.assert_called_once_with(repo_info, thresholds[0], thresholds[1], 3.0)
        ReportGenMock.return_value.generate.assert_called_once_with('out.html', report_links=[])

    @patch('src.utilities.debug.debug_print', lambda *a, **k: None)
    @patch('src.app.app.Analyzer')
    @patch('src.app.app.Scanner')
    @patch('src.app.app.Config')
    def test_cli_generator_gets_list_of_repo_infos(self, MockConfig, MockScanner, MockAnalyzer):
        # Arrange
        mock_scanner = MockScanner.return_value
        mock_scanner.scan.return_value = ['a.py']
        mock_analyzer = MockAnalyzer.return_value
        repo_info = self._repo_info()
        mock_analyzer.analyze.return_value = {repo_info.repo_root: repo_info}

        ReportGenMock = MagicMock()
        ReportGenMock.__name__ = 'CLIReportGenerator'

        app = ComplexityScannerApp(
            directories=['/x'],
            threshold_low=5.0,
            threshold_high=15.0,
            problem_file_threshold=8.0,
            output_file='cli.html',
            report_generator_cls=ReportGenMock
        )

        # Act
        app.run()

        # Assert
        ReportGenMock.assert_called_once_with([repo_info], 5.0, 15.0, 8.0)
        ReportGenMock.return_value.generate.assert_called_once_with('cli.html')

    @patch('src.utilities.debug.debug_print', lambda *a, **k: None)
    @patch('src.app.app.Analyzer')
    @patch('src.app.app.Scanner')
    @patch('src.app.app.Config')
    def test_json_generator_gets_list_of_repo_infos(self, MockConfig, MockScanner, MockAnalyzer):
        # Arrange
        mock_scanner = MockScanner.return_value
        mock_scanner.scan.return_value = ['a.py']
        mock_analyzer = MockAnalyzer.return_value
        repo_info = self._repo_info()
        mock_analyzer.analyze.return_value = {repo_info.repo_root: repo_info}

        ReportGenMock = MagicMock()
        ReportGenMock.__name__ = 'JSONReportGenerator'

        app = ComplexityScannerApp(
            directories=['/x'],
            threshold_low=6.0,
            threshold_high=16.0,
            problem_file_threshold=9.0,
            output_file='json.html',
            report_generator_cls=ReportGenMock
        )

        # Act
        app.run()

        # Assert
        ReportGenMock.assert_called_once_with(repo_info, 6.0, 16.0, 9.0)
        ReportGenMock.return_value.generate.assert_called_once_with('json.html', report_links=[])

    @patch('src.utilities.debug.debug_print', lambda *a, **k: None)
    @patch('src.app.app.Analyzer')
    @patch('src.app.app.Scanner')
    @patch('src.app.app.Config')
    def test_multiple_repo_infos_append_index_to_filename(self, MockConfig, MockScanner, MockAnalyzer):
        # Arrange
        mock_scanner = MockScanner.return_value
        mock_scanner.scan.return_value = ['a.py']
        mock_analyzer = MockAnalyzer.return_value
        repo_info1 = self._repo_info(root='/repo1', name='r1')
        repo_info2 = self._repo_info(root='/repo2', name='r2')
        mock_analyzer.analyze.return_value = {
            repo_info1.repo_root: repo_info1,
            repo_info2.repo_root: repo_info2,
        }

        ReportGenMock = MagicMock()
        ReportGenMock.__name__ = 'SomeOtherGenerator'
        inst1 = MagicMock()
        inst2 = MagicMock()
        ReportGenMock.side_effect = [inst1, inst2]

        app = ComplexityScannerApp(
            directories=['/x'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=12.0,
            output_file='report.html',
            report_generator_cls=ReportGenMock
        )

        # Act
        app.run()

        # Assert
        self.assertEqual(ReportGenMock.call_count, 2)
        
        # Check call for first instance
        args1, kwargs1 = inst1.generate.call_args
        self.assertEqual(args1[0], 'report_1.html')
        self.assertEqual(len(kwargs1['report_links']), 1)
        self.assertEqual(kwargs1['report_links'][0]['href'], 'report_2.html')

        # Check call for second instance
        args2, kwargs2 = inst2.generate.call_args
        self.assertEqual(args2[0], 'report_2.html')
        self.assertEqual(len(kwargs2['report_links']), 1)
        self.assertEqual(kwargs2['report_links'][0]['href'], 'report_1.html')

    @patch('src.utilities.debug.debug_print', lambda *a, **k: None)
    @patch('src.app.app.Analyzer')
    @patch('src.app.app.Scanner')
    @patch('src.app.app.Config')
    def test_default_output_filename_when_none(self, MockConfig, MockScanner, MockAnalyzer):
        # Arrange
        mock_scanner = MockScanner.return_value
        mock_scanner.scan.return_value = ['a.py']
        mock_analyzer = MockAnalyzer.return_value
        repo_info = self._repo_info()
        mock_analyzer.analyze.return_value = {repo_info.repo_root: repo_info}

        ReportGenMock = MagicMock()
        ReportGenMock.__name__ = 'SomeOtherGenerator'

        app = ComplexityScannerApp(
            directories=['/x'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=None,
            output_file=None,
            report_generator_cls=ReportGenMock
        )

        # Act
        app.run()

        # Assert
        ReportGenMock.return_value.generate.assert_called_once_with('complexity_report.html', report_links=[])  # Acceptera extra argument

    @patch('src.utilities.debug.debug_print', lambda *a, **k: None)
    @patch('src.app.app.Analyzer')
    @patch('src.app.app.Scanner')
    @patch('src.app.app.Config')
    def test_no_repos_no_generator_called(self, MockConfig, MockScanner, MockAnalyzer):
        # Arrange
        mock_scanner = MockScanner.return_value
        mock_scanner.scan.return_value = []
        mock_analyzer = MockAnalyzer.return_value
        mock_analyzer.analyze.return_value = {}

        ReportGenMock = MagicMock()
        ReportGenMock.__name__ = 'SomeOtherGenerator'

        app = ComplexityScannerApp(
            directories=['/x'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=None,
            output_file='out.html',
            report_generator_cls=ReportGenMock
        )

        # Act
        app.run()

        # Assert
        ReportGenMock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
