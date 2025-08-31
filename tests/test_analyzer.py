import unittest
from unittest.mock import patch, MagicMock
from src.app.analyzer import Analyzer
from src.complexity.fileanalyzer import FileAnalyzer

class MockConfig:
    def __init__(self, languages):
        self.languages = languages

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.files = [
            {'ext': 'py', 'path': 'file1.py', 'root': '/path/to/project'},
            {'ext': 'js', 'path': 'file2.js', 'root': '/path/to/project'}
        ]
        self.config = MockConfig({'py': {}, 'js': {}})

    @patch('src.app.analyzer.FileAnalyzer')
    def test_analyze(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'complexity': 12,
            'language': 'python',
            'root': '/path/to/project'
        }
        analyzer = Analyzer(self.config)
        results = analyzer.analyze(self.files)
        # results is {repo_root: GitRepoInfo}
        for repo_info in results.values():
            res = repo_info.results
            self.assertIn('python', res)
            self.assertIn('/path/to/project', res['python'])
            self.assertEqual(len(res['python']['/path/to/project']), 2)
            self.assertEqual(res['python']['/path/to/project'][0]['complexity'], 12)
            self.assertEqual(res['python']['/path/to/project'][0]['grade'], 'Medium ⚠️')

    @patch('src.app.analyzer.FileAnalyzer')
    def test_analyze_load_false(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = False
        analyzer = Analyzer(self.config)
        results = analyzer.analyze(self.files)
        # Should be empty results in all repo_infos
        for repo_info in results.values():
            self.assertEqual(repo_info.results, {})

    def test_analyze_empty_files(self):
        analyzer = Analyzer(self.config)
        results = analyzer.analyze([])
        self.assertEqual(results, {})

    @patch('src.app.analyzer.FileAnalyzer')
    def test_analyze_grade_low(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'complexity': 5,
            'language': 'python',
            'root': '/path/to/project'
        }
        analyzer = Analyzer(self.config)
        results = analyzer.analyze(self.files)
        for repo_info in results.values():
            res = repo_info.results
            self.assertEqual(res['python']['/path/to/project'][0]['grade'], 'Low ✅')

    @patch('src.app.analyzer.FileAnalyzer')
    def test_analyze_grade_high(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'complexity': 25,
            'language': 'python',
            'root': '/path/to/project'
        }
        analyzer = Analyzer(self.config)
        results = analyzer.analyze(self.files)
        for repo_info in results.values():
            res = repo_info.results
            self.assertEqual(res['python']['/path/to/project'][0]['grade'], 'High ❌')

    @patch('src.app.analyzer.FileAnalyzer')
    def test_analyze_missing_ext(self, MockFileAnalyzer):
        files = [{'path': 'file1.py', 'root': '/path/to/project'}]
        analyzer = Analyzer(self.config)
        with self.assertRaises(KeyError):
            analyzer.analyze(files)

    @patch('src.app.analyzer.FileAnalyzer')
    def test_analyze_missing_language_or_root(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'complexity': 12
        }
        analyzer = Analyzer(self.config)
        results = analyzer.analyze(self.files)
        # Should not add anything to results since language/root missing
        for repo_info in results.values():
            self.assertEqual(repo_info.results, {})

if __name__ == '__main__':
    unittest.main()