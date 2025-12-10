import unittest
from unittest.mock import patch, MagicMock
from src.report.cli.cli_report_format import CLIReportFormat
from src.kpis.model import RepoInfo, ScanDir, File, Function


class TestCLIReportFormat(unittest.TestCase):
    def setUp(self):
        # Minimal RepoInfo with one file and one function
        self.file = File(name='test.py', file_path='test.py', kpis={
            'complexity': MagicMock(value=5),
            'churn': MagicMock(value=3),
            'hotspot': MagicMock(value=15),
            'Code Ownership': MagicMock(value={'Alice': 100.0})
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

    # === RED PHASE: Tests for new helper methods ===

    def test_format_code_ownership_with_valid_data(self):
        """Test formatting code ownership with valid author percentages."""
        fmt = CLIReportFormat()
        ownership_kpi = MagicMock(value={
            'Alice': 60.0,
            'Bob': 30.0,
            'Charlie': 10.0
        })
        result = fmt._format_code_ownership(ownership_kpi)
        self.assertIn('Alice 60.0%', result)
        self.assertIn('Bob 30.0%', result)
        self.assertIn('Charlie 10.0%', result)

    def test_format_code_ownership_with_more_than_three_owners(self):
        """Test that ownership formatting limits to 3 owners + count."""
        fmt = CLIReportFormat()
        ownership_kpi = MagicMock(value={
            'Alice': 40.0,
            'Bob': 25.0,
            'Charlie': 20.0,
            'Dave': 10.0,
            'Eve': 5.0
        })
        result = fmt._format_code_ownership(ownership_kpi)
        self.assertIn('Alice 40.0%', result)
        self.assertIn('Bob 25.0%', result)
        self.assertIn('Charlie 20.0%', result)
        self.assertIn('+ 2 more', result)
        self.assertNotIn('Dave', result)

    def test_format_code_ownership_with_error(self):
        """Test formatting when ownership has an error."""
        fmt = CLIReportFormat()
        ownership_kpi = MagicMock(value={'error': 'Git not available'})
        result = fmt._format_code_ownership(ownership_kpi)
        self.assertEqual(result, " Ownership: ERROR")

    def test_format_code_ownership_with_none(self):
        """Test formatting when ownership is None."""
        fmt = CLIReportFormat()
        result = fmt._format_code_ownership(None)
        self.assertEqual(result, '')

    def test_format_shared_ownership_with_multiple_authors(self):
        """Test formatting shared ownership with multiple authors."""
        fmt = CLIReportFormat()
        shared_kpi = MagicMock(value={
            'num_significant_authors': 3,
            'authors': ['Alice', 'Bob', 'Charlie'],
            'threshold': 20.0
        })
        result = fmt._format_shared_ownership(shared_kpi)
        self.assertIn('3 authors', result)
        self.assertIn('Alice', result)

    def test_format_shared_ownership_with_single_owner(self):
        """Test formatting shared ownership with single owner."""
        fmt = CLIReportFormat()
        shared_kpi = MagicMock(value={
            'num_significant_authors': 1,
            'authors': ['Alice'],
            'threshold': 20.0
        })
        result = fmt._format_shared_ownership(shared_kpi)
        self.assertIn('Single owner', result)
        self.assertIn('Alice', result)

    def test_format_shared_ownership_with_none(self):
        """Test formatting when shared ownership is None."""
        fmt = CLIReportFormat()
        result = fmt._format_shared_ownership(None)
        self.assertEqual(result, '')

    def test_has_valid_ownership_with_valid_dict(self):
        """Test ownership validation with valid dict data."""
        fmt = CLIReportFormat()
        ownership_kpi = MagicMock(value={'Alice': 100.0})
        self.assertTrue(fmt._has_valid_ownership(ownership_kpi))

    def test_has_valid_ownership_with_none(self):
        """Test ownership validation with None."""
        fmt = CLIReportFormat()
        self.assertFalse(fmt._has_valid_ownership(None))

    def test_has_valid_ownership_with_empty_dict(self):
        """Test ownership validation with empty dict."""
        fmt = CLIReportFormat()
        ownership_kpi = MagicMock(value={})
        self.assertFalse(fmt._has_valid_ownership(ownership_kpi))

    def test_has_valid_ownership_with_na_format(self):
        """Test ownership validation with N/A format."""
        fmt = CLIReportFormat()
        ownership_kpi = MagicMock(value={'ownership': 'N/A'})
        self.assertFalse(fmt._has_valid_ownership(ownership_kpi))

    # === Additional tests for directory/file printing ===

    def test_get_visible_directories_filters_untracked(self):
        """Test that only directories with tracked files are visible."""
        fmt = CLIReportFormat()

        # Create subdirectory with tracked file
        tracked_file = File(name='tracked.py', file_path='tracked.py', kpis={
            'Code Ownership': MagicMock(value={'Alice': 100.0})
        })
        tracked_dir = ScanDir(
            dir_name='has_tracked',
            scan_dir_path='./has_tracked',
            repo_root_path='/repo',
            repo_name='repo',
            files={'tracked.py': tracked_file},
            scan_dirs={},
            kpis={}
        )

        # Create subdirectory with untracked file
        untracked_file = File(name='untracked.py', file_path='untracked.py', kpis={
            'Code Ownership': MagicMock(value={})
        })
        untracked_dir = ScanDir(
            dir_name='no_tracked',
            scan_dir_path='./no_tracked',
            repo_root_path='/repo',
            repo_name='repo',
            files={'untracked.py': untracked_file},
            scan_dirs={},
            kpis={}
        )

        parent_dir = ScanDir(
            dir_name='parent',
            scan_dir_path='.',
            repo_root_path='/repo',
            repo_name='repo',
            files={},
            scan_dirs={'has_tracked': tracked_dir, 'no_tracked': untracked_dir},
            kpis={}
        )

        visible = fmt._get_visible_directories(parent_dir)
        self.assertEqual(len(visible), 1)
        self.assertEqual(visible[0].dir_name, 'has_tracked')

    def test_print_directory_item(self):
        """Test printing a directory item."""
        fmt = CLIReportFormat()
        scan_dir = ScanDir(
            dir_name='test_dir',
            scan_dir_path='./test_dir',
            repo_root_path='/repo',
            repo_name='repo',
            files={},
            scan_dirs={},
            kpis={'complexity': MagicMock(value=10)}
        )

        with patch('builtins.print') as mock_print:
            fmt._print_directory_item(scan_dir, '├── ', '│   ', 'file')
            mock_print.assert_called_once()
            call_args = str(mock_print.call_args)
            self.assertIn('test_dir/', call_args)

    def test_print_file_item_without_functions(self):
        """Test printing a file item without functions."""
        fmt = CLIReportFormat()
        file_obj = File(name='test.py', file_path='test.py', kpis={
            'complexity': MagicMock(value=5),
            'churn': MagicMock(value=3),
            'hotspot': MagicMock(value=15)
        })

        with patch('builtins.print') as mock_print:
            fmt._print_file_item(file_obj, '├── ', '│   ', 'file', False)
            mock_print.assert_called_once()
            call_args = str(mock_print.call_args)
            self.assertIn('test.py', call_args)


if __name__ == '__main__':
    unittest.main()
