import unittest
from unittest.mock import Mock

from src.report.report_data_analyzer import ReportDataAnalyzer
from src.report.file_info import FileInfo


class TestReportDataAnalyzer(unittest.TestCase):
    """Test cases for ReportDataAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock repo info
        self.mock_repo_info = Mock()
        self.mock_repo_info.scan_dirs = {}

        # Create analyzer instance
        self.analyzer = ReportDataAnalyzer(self.mock_repo_info)

    def test_calculate_root_metrics_basic(self):
        """Test _calculate_root_metrics calculates basic metrics correctly."""
        # Create FileInfo objects (what the real code uses)
        file1 = FileInfo(path='test1.py', complexity=15, churn=3)
        file2 = FileInfo(path='test2.py', complexity=25, churn=7)

        # Create mock root_info
        root_info = Mock()
        root_info.average = 20.0
        root_info.files = [file1, file2]

        # Call the method
        metrics = self.analyzer._calculate_root_metrics(root_info)

        # Verify results
        self.assertEqual(metrics['average_complexity'], 20.0)
        self.assertIsInstance(metrics['problem_files'], list)
        self.assertIsInstance(metrics['hotspot_risk_files'], list)

    def test_calculate_root_metrics_with_problem_files(self):
        """Test _calculate_root_metrics identifies problem files correctly."""
        # Create analyzer with problem threshold
        analyzer = ReportDataAnalyzer(self.mock_repo_info, threshold=15.0, problem_file_threshold=20.0)

        # Create FileInfo objects - one above threshold
        file1 = FileInfo(path='normal.py', complexity=15)  # Below threshold
        file2 = FileInfo(path='problem.py', complexity=25)  # Above threshold

        # Create mock root_info
        root_info = Mock()
        root_info.average = 20.0
        root_info.files = [file1, file2]

        # Call the method
        metrics = analyzer._calculate_root_metrics(root_info)

        # Verify problem files are identified
        self.assertEqual(len(metrics['problem_files']), 1)
        self.assertIn(file2, metrics['problem_files'])

    def test_calculate_root_metrics_no_problem_threshold(self):
        """Test _calculate_root_metrics when problem threshold is set high (effectively disabled)."""
        # Create analyzer with very high problem threshold (effectively disabled)
        analyzer = ReportDataAnalyzer(self.mock_repo_info, threshold=15.0, problem_file_threshold=100.0)

        # Create FileInfo object with complexity below the high threshold
        file1 = FileInfo(path='test.py', complexity=25)  # Below 100.0 threshold

        # Create mock root_info
        root_info = Mock()
        root_info.average = 20.0
        root_info.files = [file1]

        # Call the method
        metrics = analyzer._calculate_root_metrics(root_info)

        # Verify no problem files when threshold is too high
        self.assertEqual(len(metrics['problem_files']), 0)

    def test_calculate_root_metrics_hotspot_risk_files(self):
        """Test _calculate_root_metrics identifies hotspot risk files correctly."""
        # Create FileInfo objects (what the real code uses)
        file1 = FileInfo(path='normal.py', complexity=15, churn=3)  # Not hotspot risk
        file2 = FileInfo(path='hotspot.py', complexity=25, churn=15)  # Hotspot risk

        # Create mock root_info
        root_info = Mock()
        root_info.average = 20.0
        root_info.files = [file1, file2]

        # Call the method
        metrics = self.analyzer._calculate_root_metrics(root_info)

        # Verify hotspot risk files are identified
        self.assertEqual(len(metrics['hotspot_risk_files']), 1)
        self.assertIn(file2, metrics['hotspot_risk_files'])
        metrics = self.analyzer._calculate_root_metrics(root_info)

        # Verify hotspot risk files are identified
        self.assertIsInstance(metrics['hotspot_risk_files'], list)
        # Note: Actual filtering logic is tested in file_helpers tests


if __name__ == '__main__':
    unittest.main()
