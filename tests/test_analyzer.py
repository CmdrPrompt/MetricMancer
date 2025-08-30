import unittest
from unittest.mock import patch, MagicMock
from src.analyzer import Analyzer
from src.fileanalyzer import FileAnalyzer

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

    @patch('src.analyzer.FileAnalyzer')
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

        self.assertIn('python', results)
        self.assertIn('/path/to/project', results['python'])
        self.assertEqual(len(results['python']['/path/to/project']), 2)
        self.assertEqual(results['python']['/path/to/project'][0]['complexity'], 12)
        self.assertEqual(results['python']['/path/to/project'][0]['grade'], 'Medium ⚠️')

    @patch('src.analyzer.FileAnalyzer')
    def test_analyze_load_false(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = False
        analyzer = Analyzer(self.config)
        results = analyzer.analyze(self.files)
        self.assertEqual(results, {})

    def test_analyze_empty_files(self):
        analyzer = Analyzer(self.config)
        results = analyzer.analyze([])
        self.assertEqual(results, {})

    @patch('src.analyzer.FileAnalyzer')
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
        self.assertEqual(results['python']['/path/to/project'][0]['grade'], 'Low ✅')

    @patch('src.analyzer.FileAnalyzer')
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
        self.assertEqual(results['python']['/path/to/project'][0]['grade'], 'High ❌')

    @patch('src.analyzer.FileAnalyzer')
    def test_analyze_missing_ext(self, MockFileAnalyzer):
        files = [{'path': 'file1.py', 'root': '/path/to/project'}]
        analyzer = Analyzer(self.config)
        with self.assertRaises(KeyError):
            analyzer.analyze(files)

    @patch('src.analyzer.FileAnalyzer')
    def test_analyze_missing_language_or_root(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'complexity': 12
        }
        analyzer = Analyzer(self.config)
        results = analyzer.analyze(self.files)
        # Should not add anything to results since language/root missing
        self.assertEqual(results, {})

if __name__ == '__main__':
    unittest.main()