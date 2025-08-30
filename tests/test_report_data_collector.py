import unittest
from src.report.report_data_collector import ReportDataCollector
from src.report.file_info import FileInfo
from src.report.root_info import RootInfo

class TestReportDataCollector(unittest.TestCase):
    def setUp(self):
        # Test data setup
        self.results = {
            'python': {
                'root1': [
                    {'path': 'fileA.py', 'complexity': 15, 'functions': 3, 'grade': None},
                    {'path': 'fileB.py', 'complexity': 25, 'functions': 2, 'grade': None},
                ],
                'root2': [
                    {'path': 'fileC.py', 'complexity': 22, 'functions': 4, 'grade': None}
                ]
            }
        }
        self.collector = ReportDataCollector(self.results)

    def test_sort_files(self):
        files = [
            {'path': 'fileB.py', 'complexity': 20, 'functions': 2, 'grade': None},
            {'path': 'fileA.py', 'complexity': 10, 'functions': 4, 'grade': None},
        ]
        sorted_files = self.collector.sort_files(files)
        self.assertEqual(sorted_files[0].path, 'fileA.py')
        self.assertEqual(sorted_files[1].path, 'fileB.py')

    def test_average_complexity(self):
        files = [
            {'path': 'fileA.py', 'complexity': 10, 'functions': 2, 'grade': None},
            {'path': 'fileB.py', 'complexity': 20, 'functions': 4, 'grade': None}
        ]
        avg_complexity = self.collector.average_complexity(files)
        self.assertEqual(avg_complexity, 15)

    def test_average_grade(self):
        files = [
            FileInfo(path='fileA.py', complexity=10),
            FileInfo(path='fileB.py', complexity=20)
        ]
        avg_grade = self.collector.average_grade(files)
        self.assertIsInstance(avg_grade, dict)
        self.assertIn('value', avg_grade)
        self.assertIn('label', avg_grade)
        self.assertIn('formatted', avg_grade)

    def test_build_root_info(self):
        root_info = self.collector.build_root_info('python', 'root1', self.results['python']['root1'])
        self.assertIsInstance(root_info, RootInfo)
        self.assertEqual(root_info.path, 'root1')

    def test_prepare_structured_data(self):
        structured_data = self.collector.prepare_structured_data()
        self.assertIsInstance(structured_data, list)
        self.assertEqual(len(structured_data), 1)  # One language 'python'
        self.assertEqual(structured_data[0]['name'], 'python')

if __name__ == '__main__':
    unittest.main()