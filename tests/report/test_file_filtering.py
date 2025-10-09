import unittest
from unittest.mock import MagicMock
from src.report.cli.cli_report_format import CLIReportFormat
from src.report.json.json_report_format import JSONReportFormat
from src.report.cli.cli_csv_report_format import CLICSVReportFormat
from src.kpis.model import RepoInfo, ScanDir, File


class TestFileFiltering(unittest.TestCase):
    def setUp(self):
        # Tracked file (should be included)
        self.tracked_file = File(name='tracked.py', file_path='tracked.py', kpis={
            'complexity': MagicMock(value=5),
            'churn': MagicMock(value=3),
            'hotspot': MagicMock(value=15),
            'Code Ownership': MagicMock(value={'Alice': 100.0})
        })
        # Untracked file (should be filtered out)
        self.untracked_file = File(name='untracked.py', file_path='untracked.py', kpis={
            'complexity': MagicMock(value=7),
            'churn': MagicMock(value=2),
            'hotspot': MagicMock(value=10),
            'Code Ownership': MagicMock(value={'ownership': 'N/A'})
        })
        self.scan_dir = ScanDir(
            dir_name='repo',
            scan_dir_path='.',
            repo_root_path='/repo',
            repo_name='repo',
            files={'tracked.py': self.tracked_file, 'untracked.py': self.untracked_file},
            scan_dirs={},
            kpis={}
        )
        self.repo_info = RepoInfo(
            dir_name='repo',
            scan_dir_path='.',
            repo_root_path='/repo',
            repo_name='repo',
            files={'tracked.py': self.tracked_file, 'untracked.py': self.untracked_file},
            scan_dirs={},
            kpis={}
        )

    def test_cli_report_filters_untracked(self):
        fmt = CLIReportFormat()
        files = fmt._collect_all_files(self.repo_info)
        names = [f.name for f in files]
        self.assertIn('tracked.py', names)
        self.assertNotIn('untracked.py', names)

    def test_json_report_filters_untracked(self):
        fmt = JSONReportFormat()
        items = fmt._collect_flat_list(self.repo_info, level='file')
        filenames = [item['filename'] for item in items]
        self.assertIn('tracked.py', filenames)
        self.assertNotIn('untracked.py', filenames)

    def test_csv_report_filters_untracked(self):
        fmt = CLICSVReportFormat()
        items = fmt._collect_flat_list(self.repo_info, level='file')
        filenames = [item['filename'] for item in items]
        self.assertIn('tracked.py', filenames)
        self.assertNotIn('untracked.py', filenames)


if __name__ == '__main__':
    unittest.main()
