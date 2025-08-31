import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.report.report_data import ReportDataBuilder
from src.report.file_info import FileInfo
from src.report.file_helpers import sort_files, average_complexity, average_grade

class TestReportDataBuilder(unittest.TestCase):
    def setUp(self):
        # Patch open and file existence for dummy files
        # Example data
        results = {
            'python': {
                'root1': [
                    {'path': 'file1.py', 'complexity': 15, 'functions': 3, 'grade': None},
                    {'path': 'file2.py', 'complexity': 7, 'functions': 2, 'grade': None},
                ],
                'root2': [
                    {'path': 'file3.py', 'complexity': 22, 'functions': 4, 'grade': None}
                ]
            }
        }
        class RepoInfo:
            pass
        repo_info = RepoInfo()
        repo_info.results = results
        self.builder = ReportDataBuilder(repo_info)
        self.patcher_exists = patch('os.path.exists', return_value=True)
        self.patcher_open = patch('builtins.open', mock_open(read_data="dummy code"))
        self.patcher_exists.start()
        self.patcher_open.start()
        self.addCleanup(self.patcher_exists.stop)
        self.addCleanup(self.patcher_open.stop)

    def test_sort_files(self):
        # Test sorting functionality
        files = [
            {'path': 'fileB.py', 'complexity': 10, 'functions': 2, 'grade': None},
            {'path': 'fileA.py', 'complexity': 20, 'functions': 4, 'grade': None}
        ]
        sorted_files = sort_files(files)
        self.assertEqual(sorted_files[0].path, 'fileA.py')
        self.assertEqual(sorted_files[1].path, 'fileB.py')

    def test_average_complexity(self):
        # Test average complexity calculation
        files = [
            {'path': 'file1.py', 'complexity': 10, 'functions': 2, 'grade': None},
            {'path': 'file2.py', 'complexity': 20, 'functions': 4, 'grade': None}
        ]
        avg_complexity = average_complexity(files)
        self.assertEqual(avg_complexity, 15)

    def test_average_grade(self):
        # Test average grade calculation
        files = [
            {'path': 'file1.py', 'complexity': 10, 'functions': 2, 'grade': None},
            {'path': 'file2.py', 'complexity': 20, 'functions': 4, 'grade': None}
        ]
        avg_grade = average_grade(files, self.builder.threshold_low, self.builder.threshold_high)
        self.assertIsInstance(avg_grade, dict)
        self.assertIn('value', avg_grade)
        self.assertIn('label', avg_grade)
        self.assertIn('formatted', avg_grade)

if __name__ == '__main__':
    unittest.main()