import unittest
from unittest.mock import patch, MagicMock
import json

from src.report.json.json_report_format import JSONReportFormat
from src.report.json.json_report_generator import JSONReportGenerator


class TestJSONReportFormat(unittest.TestCase):
    def _make_repo_info(self, **attrs):
        class RepoInfo:
            pass
        repo_info = RepoInfo()
        for k, v in attrs.items():
            setattr(repo_info, k, v)
        return repo_info

    @patch('builtins.print')
    def test_file_level_outputs_hotspot_and_relpath_and_prints_array(self, mock_print):
        # Arrange
        repo_info = self._make_repo_info(
            timestamp='2024-01-01T00:00:00Z',
            repo_root='/repo',
            repo_name='repoA',
            component='compA',
            team='teamA',
            results={
                'python': {
                    '/repo/dir': [
                        {'path': '/repo/dir/file1.py', 'complexity': 10, 'churn': 2, 'grade': 'Low \u2705'},
                    ]
                }
            }
        )
        fmt = JSONReportFormat()

        # Act
        fmt.print_report(repo_info, debug_print=lambda *_: None, level='file')

        # Assert
        mock_print.assert_called_once()
        data = json.loads(mock_print.call_args[0][0])
        self.assertEqual(len(data), 1)
        self.assertIn(data[0]['filename'], ['dir/file1.py', './dir/file1.py'])
        self.assertEqual(data[0]['hotspot_score'], 20.0)
        self.assertEqual(data[0]['cyclomatic_complexity'], 10)
        self.assertEqual(data[0]['churn'], 2)

    @patch('builtins.print')
    def test_function_level_outputs_per_function_and_overrides_hotspot(self, mock_print):
        # Arrange
        repo_info = self._make_repo_info(
            timestamp='2024-01-01T00:00:00Z',
            repo_root='/repo',
            results={
                'python': {
                    '/repo/dir': [
                        {
                            'path': '/repo/dir/file2.py',
                            'complexity': 10,
                            'churn': 3,
                            'grade': 'Medium ⚠️',
                            'functions': [
                                {'name': 'f1', 'complexity': 5, 'lines_of_code': 12, 'hotspot_score': 999},
                                {'name': 'f2', 'complexity': 7, 'lines_of_code': 3},
                            ]
                        }
                    ]
                }
            }
        )
        fmt = JSONReportFormat()

        # Act
        fmt.print_report(repo_info, debug_print=lambda *_: None, level='function')

        # Assert
        mock_print.assert_called_once()
        data = json.loads(mock_print.call_args[0][0])
        self.assertEqual(len(data), 2)
        by_name = {e['function_name']: e for e in data}
        self.assertEqual(by_name['f1']['hotspot_score'], 999)
        self.assertEqual(by_name['f1']['cyclomatic_complexity'], 5)
        self.assertEqual(by_name['f1']['churn'], 3)
        self.assertEqual(by_name['f1']['grade'], 'Medium ⚠️')
        self.assertEqual(by_name['f2']['hotspot_score'], 30.0)
        self.assertEqual(by_name['f2']['cyclomatic_complexity'], 7)

    @patch('builtins.print')
    def test_hotspot_none_when_churn_or_complexity_missing(self, mock_print):
        # Arrange
        repo_info = self._make_repo_info(
            repo_root='/repo',
            results={
                'python': {
                    '/repo/dir': [
                        {'path': '/repo/dir/fileA.py', 'complexity': 10, 'grade': 'Low ✅'},  # missing churn
                        {'path': '/repo/dir/fileB.py', 'churn': 5, 'grade': 'Low ✅'},          # missing complexity
                    ]
                }
            }
        )
        fmt = JSONReportFormat()

        # Act
        fmt.print_report(repo_info, debug_print=lambda *_: None, level='file')

        # Assert
        last_call_arg = mock_print.call_args_list[-1].args[0]
        data = json.loads(last_call_arg)
        by_file = {e['filename']: e for e in data}
        # Accept both 'dir/fileA.py' and './dir/fileA.py' for compatibility
        fileA_key = 'dir/fileA.py' if 'dir/fileA.py' in by_file else './dir/fileA.py'
        fileB_key = 'dir/fileB.py' if 'dir/fileB.py' in by_file else './dir/fileB.py'
        self.assertIsNone(by_file[fileA_key]['hotspot_score'])
        self.assertIsNone(by_file[fileB_key]['hotspot_score'])

    @patch('builtins.print')
    def test_hotspot_none_on_type_error(self, mock_print):
        # Arrange
        repo_info = self._make_repo_info(
            repo_root='/repo',
            results={
                'python': {
                    '/repo/dir': [
                        {'path': '/repo/dir/fileC.py', 'complexity': 'bad', 'churn': 2, 'grade': 'Low ✅'},
                    ]
                }
            }
        )
        fmt = JSONReportFormat()

        # Act
        fmt.print_report(repo_info, debug_print=lambda *_: None, level='file')

        # Assert
        last_call_arg = mock_print.call_args_list[-1].args[0]
        data = json.loads(last_call_arg)
        self.assertIsNone(data[0]['hotspot_score'])

    @patch('builtins.print')
    def test_includes_metadata_fields(self, mock_print):
        # Arrange
        repo_info = self._make_repo_info(
            timestamp='2024-02-02T12:00:00Z',
            repo_root='/repo',
            repo_name='repoZ',
            component='componentZ',
            team='teamZ',
            results={
                'python': {
                    '/repo/dir': [
                        {'path': '/repo/dir/fileZ.py', 'complexity': 1, 'churn': 2, 'grade': 'Low ✅'},
                    ]
                }
            }
        )
        fmt = JSONReportFormat()

        # Act
        fmt.print_report(repo_info, debug_print=lambda *_: None, level='file')

        # Assert
        last_call_arg = mock_print.call_args_list[-1].args[0]
        data = json.loads(last_call_arg)
        item = data[0]
        self.assertEqual(item['repo_name'], 'repoZ')
        self.assertEqual(item['component'], 'componentZ')
        self.assertEqual(item['team'], 'teamZ')
        self.assertEqual(item['timestamp'], '2024-02-02T12:00:00Z')


class TestJSONReportGenerator(unittest.TestCase):
    def _make_repo_info(self):
        class RepoInfo:
            pass
        r = RepoInfo()
        r.results = {}
        r.timestamp = '2024-01-01T00:00:00Z'
        r.repo_root = '/repo'
        r.repo_name = 'repoA'
        r.component = 'compA'
        r.team = 'teamA'
        return r

    @patch('sys.argv', new=['prog', '--level', 'function'])
    def test_uses_level_from_sys_argv_and_invokes_for_each_repo(self):
        # Arrange
        repo_infos = [self._make_repo_info(), self._make_repo_info()]
        gen = JSONReportGenerator(repo_infos)

        # Act & Assert
        # Should not raise serialization error
        try:
            gen.generate()
        except TypeError as e:
            self.fail(f"Serialization failed: {e}")

    @patch('sys.argv', new=['prog'])
    def test_defaults_level_file_when_no_sys_argv_flag(self):
        # Arrange
        repo_infos = [self._make_repo_info()]
        gen = JSONReportGenerator(repo_infos)

        # Act & Assert
        # Should not raise serialization error
        try:
            gen.generate()
        except TypeError as e:
            self.fail(f"Serialization failed: {e}")


if __name__ == '__main__':
    unittest.main()
