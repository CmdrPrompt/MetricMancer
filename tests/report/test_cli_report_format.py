import unittest
from unittest.mock import patch, MagicMock
from src.report.cli_report_format import CLIReportFormat
from src.kpis.model import RepoInfo, ScanDir, File, Function

class TestCLIReportFormat(unittest.TestCase):
    def setUp(self):
        # Minimal RepoInfo with one file and one function
        self.file = File(name='test.py', file_path='test.py', kpis={
            'complexity': MagicMock(value=5),
            'churn': MagicMock(value=3),
            'hotspot': MagicMock(value=15)
        })
        self.func = Function(name='foo', kpis={
            'complexity': MagicMock(value=2)
        })
        self.file.functions = [self.func]
        self.scan_dir = ScanDir(
            dir_name='repo',
            scan_dir_path='.',
            repo_root_path='/repo',
            repo_name='repo',
            files={'test.py': self.file},
            scan_dirs={},
            kpis={}
        )
        self.repo_info = RepoInfo(
            dir_name='repo',
            scan_dir_path='.',
            repo_root_path='/repo',
            repo_name='repo',
            files={'test.py': self.file},
            scan_dirs={},
            kpis={}
        )

    def test_get_repo_stats_with_files(self):
        fmt = CLIReportFormat()
        stats, files = fmt._get_repo_stats(self.repo_info)
        self.assertIn('C:5', stats)
        self.assertIn('Churn:3', stats)
        self.assertEqual(files[0].name, 'test.py')

    def test_get_repo_stats_no_files(self):
        fmt = CLIReportFormat()
        empty_repo = RepoInfo(
            dir_name='repo',
            scan_dir_path='.',
            repo_root_path='/repo',
            repo_name='repo',
            files={},
            scan_dirs={},
            kpis={}
        )
        stats, files = fmt._get_repo_stats(empty_repo)
        self.assertIn('No files analyzed', stats)
        self.assertEqual(files, [])

    def test_format_file_stats(self):
        fmt = CLIReportFormat()
        stats = fmt._format_file_stats(self.file)
        self.assertIn('C:5', stats)
        self.assertIn('Churn:3', stats)
        self.assertIn('Hotspot:15', stats)

    def test_print_report_runs(self):
        fmt = CLIReportFormat()
        # Patch print to capture output
        with patch('builtins.print') as mock_print:
            fmt.print_report(self.repo_info, debug_print=lambda x: None)
            self.assertTrue(mock_print.called)

if __name__ == '__main__':
    unittest.main()
