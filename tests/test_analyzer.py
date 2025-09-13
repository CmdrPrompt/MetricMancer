import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.app.analyzer import Analyzer
from src.kpis.complexity.fileanalyzer import FileAnalyzer
from src.kpis.churn.code_churn import FileMetrics

@patch('src.utilities.debug.debug_print', lambda *a, **k: None)
class MockConfig:
    def __init__(self, languages):
        self.languages = languages

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.files = [
            {'ext': '.py', 'path': 'file1.py', 'root': '/path/to/project'},
            {'ext': '.js', 'path': 'file2.js', 'root': '/path/to/project'}
        ]
        self.config = MockConfig({'.py': {}, '.js': {}})
        # Patch open and file existence for dummy files
        self.patcher_exists = patch('os.path.exists', return_value=True)
        self.patcher_open = patch('builtins.open', mock_open(read_data="dummy code"))
        self.patcher_exists.start()
        self.patcher_open.start()
        self.addCleanup(self.patcher_exists.stop)
        self.addCleanup(self.patcher_open.stop)

    def test_group_files_by_repo(self):
        """Test the _group_files_by_repo private method."""
        analyzer = Analyzer(self.config, 10.0, 20.0)
        files = [
            {'path': 'file1.py', 'root': '/repo1'},
            {'path': 'file2.py', 'root': '/repo1'},
            {'path': 'file3.js', 'root': '/repo2'},
        ]
        files_by_root, scan_dirs_by_root = analyzer._group_files_by_repo(files)

        self.assertEqual(len(files_by_root), 2)
        self.assertIn('/repo1', files_by_root)
        self.assertIn('/repo2', files_by_root)
        self.assertEqual(len(files_by_root['/repo1']), 2)
        self.assertEqual(len(files_by_root['/repo2']), 1)
        self.assertEqual(files_by_root['/repo1'][0]['path'], 'file1.py')

        self.assertEqual(len(scan_dirs_by_root), 2)
        self.assertEqual(scan_dirs_by_root['/repo1'], {'/repo1'})
        self.assertEqual(scan_dirs_by_root['/repo2'], {'/repo2'})

    @patch('src.app.analyzer.FileAnalyzer')
    @patch('src.app.analyzer.MetricsCollector')
    @patch('src.app.analyzer.os.path.abspath', side_effect=lambda p: f'/path/to/project/{p}' if not p.startswith('/') else p)
    def test_analyze_repo(self, mock_abspath, MockMetricsCollector, MockFileAnalyzer):
        """Test the _analyze_repo private method."""
        # Arrange
        mock_metrics_collector = MockMetricsCollector.return_value
        mock_metrics_collector.collect.return_value = [
            FileMetrics(filename='file1.py', abs_path='/path/to/project/file1.py', complexity=12, churn=5)
        ]

        mock_file_analyzer = MockFileAnalyzer.return_value
        mock_file_analyzer.load.return_value = True
        mock_file_analyzer.analyze.return_value = {
            'complexity': 12, 'language': 'python', 'root': '/path/to/project'
        }

        analyzer = Analyzer(self.config, 10.0, 20.0)
        repo_root = '/path/to/project'
        files_in_repo = [{'path': 'file1.py', 'root': repo_root, 'ext': '.py'}]
        scan_dirs = [repo_root]

        # Act
        repo_info = analyzer._analyze_repo(repo_root, files_in_repo, scan_dirs)

        # Assert
        self.assertEqual(repo_info.repo_name, 'project')
        self.assertEqual(repo_info.results['python']['/path/to/project'][0]['grade'], 'Medium ⚠️')
        self.assertEqual(repo_info.results['python']['/path/to/project'][0]['churn'], 5)
        self.assertIn('/path/to/project/file1.py', repo_info.hotspot_data)
        self.assertEqual(repo_info.hotspot_data['/path/to/project/file1.py'], 60)

    @patch('src.app.analyzer.FileAnalyzer')
    def test_analyze(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'complexity': 12,
            'language': 'python',
            'root': '/path/to/project'
        }
        analyzer = Analyzer(self.config, 10.0, 20.0)
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
        analyzer = Analyzer(self.config, 10.0, 20.0)
        results = analyzer.analyze(self.files)
        # Should be empty results in all repo_infos
        for repo_info in results.values():
            self.assertEqual(repo_info.results, {})

    def test_analyze_empty_files(self):
        analyzer = Analyzer(self.config, 10.0, 20.0)
        results = analyzer.analyze([])
        self.assertEqual(results, {})

    @patch('src.app.analyzer.FileAnalyzer', **{'return_value.load.return_value': True})
    def test_analyze_grade_low(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'complexity': 5,
            'language': 'python',
            'root': '/path/to/project'
        }
        analyzer = Analyzer(self.config, 10.0, 20.0)
        results = analyzer.analyze(self.files)
        for repo_info in results.values():
            res = repo_info.results
            self.assertEqual(res['python']['/path/to/project'][0]['grade'], 'Low ✅')

    @patch('src.app.analyzer.FileAnalyzer', **{'return_value.load.return_value': True})
    def test_analyze_grade_high(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'complexity': 25,
            'language': 'python',
            'root': '/path/to/project'
        }
        analyzer = Analyzer(self.config, 10.0, 20.0)
        results = analyzer.analyze(self.files)
        for repo_info in results.values():
            res = repo_info.results
            self.assertEqual(res['python']['/path/to/project'][0]['grade'], 'High ❌')

    @patch('src.app.analyzer.FileAnalyzer', **{'return_value.load.return_value': True})
    def test_analyze_missing_language_or_root(self, MockFileAnalyzer):
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'complexity': 12
        }
        analyzer = Analyzer(self.config, 10.0, 20.0)
        results = analyzer.analyze(self.files)
        # Should not add anything to results since language/root missing
        for repo_info in results.values():
            self.assertEqual(repo_info.results, {})

if __name__ == '__main__':
    unittest.main()