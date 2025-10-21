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
        # Updated: RepoInfo now contains scan_dirs instead of files directly
        self.repo_info = RepoInfo(
            dir_name='repo',
            scan_dir_path='.',
            repo_root_path='/repo',
            repo_name='repo',
            files={},  # No files directly in RepoInfo
            scan_dirs={'repo': self.scan_dir},  # Contains scan_dirs with files
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

    def test_csv_is_tracked_file_with_valid_ownership(self):
        fmt = CLICSVReportFormat()
        self.assertTrue(fmt._is_tracked_file(self.tracked_file))

    def test_csv_is_tracked_file_with_na_ownership(self):
        fmt = CLICSVReportFormat()
        self.assertFalse(fmt._is_tracked_file(self.untracked_file))

    def test_csv_is_tracked_file_without_ownership_kpi(self):
        fmt = CLICSVReportFormat()
        file_without_ownership = File(name='no_ownership.py', file_path='no_ownership.py', kpis={
            'complexity': MagicMock(value=5)
        })
        self.assertTrue(fmt._is_tracked_file(file_without_ownership))

    def test_csv_get_file_churn_with_churn_kpi(self):
        fmt = CLICSVReportFormat()
        self.assertEqual(fmt._get_file_churn(self.tracked_file), 3)

    def test_csv_get_file_churn_without_churn_kpi(self):
        fmt = CLICSVReportFormat()
        file_without_churn = File(name='no_churn.py', file_path='no_churn.py', kpis={
            'complexity': MagicMock(value=5)
        })
        self.assertIsNone(fmt._get_file_churn(file_without_churn))

    def test_csv_get_kpi_value_with_kpi(self):
        fmt = CLICSVReportFormat()
        self.assertEqual(fmt._get_kpi_value(self.tracked_file, 'complexity'), 5)

    def test_csv_get_kpi_value_without_kpi(self):
        fmt = CLICSVReportFormat()
        self.assertIsNone(fmt._get_kpi_value(self.tracked_file, 'nonexistent'))

    def test_csv_create_file_level_item(self):
        fmt = CLICSVReportFormat()
        item = fmt._create_file_level_item(self.tracked_file, 3)
        expected = {
            'filename': 'tracked.py',
            'cyclomatic_complexity': 5,
            'churn': 3,
            'hotspot_score': 15
        }
        self.assertEqual(item, expected)

    def test_csv_create_items_for_file_tracked(self):
        fmt = CLICSVReportFormat()
        items = fmt._create_items_for_file(self.tracked_file, 'file')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['filename'], 'tracked.py')

    def test_csv_create_items_for_file_untracked(self):
        fmt = CLICSVReportFormat()
        items = fmt._create_items_for_file(self.untracked_file, 'file')
        self.assertEqual(len(items), 0)

    def test_csv_create_header_with_data(self):
        fmt = CLICSVReportFormat()
        data = [{'filename': 'test.py', 'complexity': 5}]
        header = fmt._create_header(data)
        self.assertEqual(header, ['filename', 'complexity', 'repo_name'])

    def test_csv_create_header_empty_data(self):
        fmt = CLICSVReportFormat()
        header = fmt._create_header([])
        self.assertEqual(header, [])


if __name__ == '__main__':
    unittest.main()
