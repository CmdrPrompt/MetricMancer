import unittest
from unittest.mock import patch, MagicMock
from src.report.report_data_analyzer import ReportDataAnalyzer
from src.report.file_info import FileInfo

class TestReportDataAnalyzer(unittest.TestCase):
    def setUp(self):
        self.results = {
            'python': {
                'root1': [
                    {'path': 'file1.py', 'complexity': 15, 'functions': 3, 'grade': None},
                    {'path': 'file2.py', 'complexity': 25, 'functions': 2, 'grade': None},
                ],
                'root2': [
                    {'path': 'file3.py', 'complexity': 22, 'functions': 4, 'grade': None}
                ]
            }
        }

    @patch('src.report.report_data_analyzer.ReportDataCollector')
    def test_find_problematic_roots(self, MockReportDataCollector):
        # Mock the ReportDataCollector
        mock_collector = MockReportDataCollector.return_value
        # Create separate mocked RootInfo for root1 and root2
        root_info_mock_root1 = MagicMock()
        root_info_mock_root1.files = [FileInfo(path='file2.py', complexity=25)]
        root_info_mock_root1.average = 20

        root_info_mock_root2 = MagicMock()
        root_info_mock_root2.files = [FileInfo(path='file3.py', complexity=22)]
        root_info_mock_root2.average = 22

        def side_effect(language, root, files):
            if root == 'root1':
                return root_info_mock_root1
            if root == 'root2':
                return root_info_mock_root2

        mock_collector.build_root_info.side_effect = side_effect
        # Set threshold_low and threshold_high to numeric values to avoid MagicMock comparison error
        mock_collector.threshold_low = 10.0
        mock_collector.threshold_high = 20.0

        analyzer = ReportDataAnalyzer(self.results, threshold=20.0, problem_file_threshold=20.0)
        problematic_roots = analyzer.find_problematic_roots()

        expected_output = [
            {
                'language': 'python',
                'root': 'root2',
                'average': 22,
                'grade': 'High ❌',
                'problem_files': [FileInfo(path='file3.py', complexity=22)]
            },
            {
                'language': 'python',
                'root': 'root1',
                'average': 20,
                'grade': 'Medium ⚠️',
                'problem_files': [FileInfo(path='file2.py', complexity=25)]
            }
        ]

        self.assertEqual(problematic_roots, expected_output)

if __name__ == '__main__':
    unittest.main()