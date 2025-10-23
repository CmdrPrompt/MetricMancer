import unittest
from unittest.mock import Mock

from src.report.report_data import ReportData, ReportDataBuilder


class TestReportData(unittest.TestCase):
    """Test cases for ReportData class."""

    def test_report_data_initialization(self):
        """Test that ReportData stores summary and details correctly."""
        summary = {"total_files": 10, "avg_complexity": 15.5}
        details = [{"file": "test.py", "complexity": 12}]

        report_data = ReportData(summary, details)

        self.assertEqual(report_data.summary, summary)
        self.assertEqual(report_data.details, details)


class TestReportDataBuilder(unittest.TestCase):
    """Test cases for ReportDataBuilder class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock KPI objects
        complexity_kpi = Mock()
        complexity_kpi.value = 15
        complexity_kpi.calculation_values = {'function_count': 3}

        churn_kpi = Mock()
        churn_kpi.value = 5

        # Create mock file objects
        self.mock_file1 = Mock()
        self.mock_file1.file_path = "src/main.py"
        self.mock_file1.kpis = {'complexity': complexity_kpi, 'churn': churn_kpi}

        self.mock_file2 = Mock()
        self.mock_file2.file_path = "src/utils.py"
        self.mock_file2.kpis = {'complexity': complexity_kpi, 'churn': churn_kpi}

        # Create mock scan directory
        self.mock_scan_dir = Mock()
        self.mock_scan_dir.files = [self.mock_file1, self.mock_file2]

        # Create mock repo info
        self.mock_repo_info = Mock()
        self.mock_repo_info.results = {
            'python': {
                'src': {
                    'files': [self.mock_file1, self.mock_file2],
                    'scan_dir': self.mock_scan_dir
                }
            }
        }

    def test_prepare_structured_data_single_language(self):
        """Test prepare_structured_data with single language and root."""
        builder = ReportDataBuilder(self.mock_repo_info)

        # Mock the collector's build_root_info method
        builder.collector.build_root_info = Mock(return_value={
            'name': 'src',
            'files': [
                {'path': 'src/main.py', 'complexity': 15, 'churn': 5, 'functions': 3},
                {'path': 'src/utils.py', 'complexity': 15, 'churn': 5, 'functions': 3}
            ],
            'summary': {'total_files': 2, 'avg_complexity': 15.0}
        })

        result = builder.prepare_structured_data()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'python')
        self.assertEqual(len(result[0]['roots']), 1)
        self.assertEqual(result[0]['roots'][0]['name'], 'src')

    def test_prepare_structured_data_multiple_languages(self):
        """Test prepare_structured_data with multiple languages."""
        # Add another language to results
        self.mock_repo_info.results['javascript'] = {
            'lib': {
                'files': [self.mock_file1],
                'scan_dir': self.mock_scan_dir
            }
        }

        builder = ReportDataBuilder(self.mock_repo_info)

        # Mock the collector's build_root_info method for both calls
        builder.collector.build_root_info = Mock(side_effect=[
            {'name': 'src', 'files': [], 'summary': {}},  # python/src
            {'name': 'lib', 'files': [], 'summary': {}}   # javascript/lib
        ])

        result = builder.prepare_structured_data()

        self.assertEqual(len(result), 2)
        language_names = [lang['name'] for lang in result]
        self.assertIn('python', language_names)
        self.assertIn('javascript', language_names)

    def test_prepare_structured_data_empty_results(self):
        """Test prepare_structured_data with empty results."""
        self.mock_repo_info.results = {}

        builder = ReportDataBuilder(self.mock_repo_info)

        result = builder.prepare_structured_data()

        self.assertEqual(result, [])

    def test_builder_initialization(self):
        """Test that ReportDataBuilder initializes correctly."""
        builder = ReportDataBuilder(
            self.mock_repo_info,
            threshold_low=5.0,
            threshold_high=25.0,
            problem_file_threshold=30.0
        )

        self.assertEqual(builder.repo_info, self.mock_repo_info)
        self.assertEqual(builder.threshold_low, 5.0)
        self.assertEqual(builder.threshold_high, 25.0)
        self.assertEqual(builder.problem_file_threshold, 30.0)
        self.assertIsNotNone(builder.collector)


if __name__ == '__main__':
    unittest.main()
