# tests/test_collector.py

import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.collector import collect_results

class TestCollector(unittest.TestCase):
    def setUp(self):
        # Patch open and file existence for dummy files
        self.patcher_exists = patch('os.path.exists', return_value=True)
        self.patcher_open = patch('builtins.open', mock_open(read_data="dummy code"))
        self.patcher_exists.start()
        self.patcher_open.start()
        self.addCleanup(self.patcher_exists.stop)
        self.addCleanup(self.patcher_open.stop)

    @patch('src.collector.os.path.isdir')
    def test_collect_results_dir_not_exists(self, mock_isdir):
        import sys
        from io import StringIO
        mock_isdir.return_value = False
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            results, report_filename = collect_results(['/does/not/exist'])
        finally:
            sys.stdout = old_stdout
        self.assertEqual(dict(results), {})

    @patch('src.collector.os.path.isdir')
    @patch('src.collector.os.walk')
    @patch('src.collector.FileAnalyzer')
    def test_collect_results_load_false(self, MockFileAnalyzer, mock_os_walk, mock_isdir):
        mock_isdir.return_value = True
        mock_os_walk.return_value = [('/mock/dir', ('subdir',), ('file1.py',))]
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = False
        results, report_filename = collect_results(['/mock/dir'])
        self.assertEqual(dict(results), {})

    @patch('src.collector.os.path.isdir')
    @patch('src.collector.os.walk')
    @patch('src.collector.FileAnalyzer')
    def test_collect_results_unsupported_extension(self, MockFileAnalyzer, mock_os_walk, mock_isdir):
        mock_isdir.return_value = True
        mock_os_walk.return_value = [('/mock/dir', ('subdir',), ('file1.unknown',))]
        results, report_filename = collect_results(['/mock/dir'])
        self.assertEqual(dict(results), {})

    @patch('src.collector.os.path.isdir')
    @patch('src.collector.os.walk')
    @patch('src.collector.FileAnalyzer')
    def test_collect_results_multiple_dirs(self, MockFileAnalyzer, mock_os_walk, mock_isdir):
        mock_isdir.side_effect = [True, True]
        mock_os_walk.side_effect = [
            [('/mock/dir1', (), ('file1.py',))],
            [('/mock/dir2', (), ('file2.py',))]
        ]
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'language': 'Python',
            'complexity': 5,
            'root': '/mock/dir1'
        }
        results, report_filename = collect_results(['/mock/dir1', '/mock/dir2'])
        self.assertTrue('Python' in results)

    def test_collect_results_empty_dirs(self):
        results, report_filename = collect_results([])
        self.assertEqual(dict(results), {})

    @patch('src.collector.os.path.isdir')
    @patch('src.collector.os.walk')
    @patch('src.collector.FileAnalyzer')
    @patch('src.collector.os.environ', {'THRESHOLD_LOW': '5', 'THRESHOLD_HIGH': '10'})
    def test_collect_results_env_thresholds(self, MockFileAnalyzer, mock_os_walk, mock_isdir):
        mock_isdir.return_value = True
        mock_os_walk.return_value = [('/mock/dir', (), ('file1.py',))]
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'language': 'Python',
            'complexity': 12,
            'root': '/mock/dir'
        }
        results, report_filename = collect_results(['/mock/dir'])
        # Should be graded as High ❌ since threshold_high=10
        self.assertEqual(results['Python']['/mock/dir'][0]['grade'], 'High ❌')
    
if __name__ == '__main__':
    unittest.main()
