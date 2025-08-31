import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.report.report_data_analyzer import ReportDataAnalyzer
from src.report.file_info import FileInfo

class TestReportDataAnalyzer(unittest.TestCase):
    def setUp(self):
        results = {
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
        class RepoInfo:
            pass
        self.repo_info = RepoInfo()
        self.repo_info.results = results
        self.patcher_exists = patch('os.path.exists', return_value=True)
        self.patcher_open = patch('builtins.open', mock_open(read_data="dummy code"))
        self.patcher_exists.start()
        self.patcher_open.start()
        self.addCleanup(self.patcher_exists.stop)
        self.addCleanup(self.patcher_open.stop)

    def test_find_problematic_roots(self):
        analyzer = ReportDataAnalyzer(self.repo_info, threshold=20.0, problem_file_threshold=20.0)
        problematic_roots = analyzer.find_problematic_roots()
        print('ACTUAL:', problematic_roots)

        expected_output = [
            {
                'language': 'python',
                'root': 'root1',
                'repo_root': '',
                'average': 20.0,
                'grade': 'Medium ⚠️',
                'problem_files': [FileInfo(path='file2.py', complexity=25, functions=2, grade='High ❌', test_cases=0, churn=0, repo_root='')],
                'files': [
                    FileInfo(path='file1.py', complexity=15, functions=3, grade='Medium ⚠️', test_cases=0, churn=0, repo_root=''),
                    FileInfo(path='file2.py', complexity=25, functions=2, grade='High ❌', test_cases=0, churn=0, repo_root='')
                ],
                'hotspot_risk_files': []
            },
            {
                'language': 'python',
                'root': 'root2',
                'repo_root': '',
                'average': 22.0,
                'grade': 'High ❌',
                'problem_files': [FileInfo(path='file3.py', complexity=22, functions=4, grade='High ❌', test_cases=0, churn=0, repo_root='')],
                'files': [FileInfo(path='file3.py', complexity=22, functions=4, grade='High ❌', test_cases=0, churn=0, repo_root='')],
                'hotspot_risk_files': []
            }
        ]

        # Compare dicts, not object identity for FileInfo
        def fileinfo_to_dict(fi):
            return {'path': fi.path, 'complexity': fi.complexity}
        def normalize(entry):
            entry = entry.copy()
            entry['problem_files'] = [fileinfo_to_dict(fi) for fi in entry['problem_files']]
            return entry
        normalized_actual = [normalize(e) for e in problematic_roots]
        normalized_expected = [normalize(e) for e in expected_output]
        self.assertEqual(normalized_actual, normalized_expected)

if __name__ == '__main__':
    unittest.main()