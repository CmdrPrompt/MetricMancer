# tests/test_collector.py

import unittest
from unittest.mock import patch, MagicMock
from src.collector import collect_results

class TestCollector(unittest.TestCase):
    
    @patch('src.collector.os.path.isdir')
    @patch('src.collector.os.walk')
    @patch('src.collector.FileAnalyzer')
    def test_collect_results(self, MockFileAnalyzer, mock_os_walk, mock_isdir):
        # Mock directory check and directory structure
        mock_isdir.return_value = True
        mock_os_walk.return_value = [
            ('/mock/dir', ('subdir',), ('file1.py', 'file2.txt')),
        ]

        # Mock FileAnalyzer
        mock_analyzer_instance = MockFileAnalyzer.return_value
        mock_analyzer_instance.load.return_value = True
        mock_analyzer_instance.analyze.return_value = {
            'language': 'Python',
            'complexity': 5,
            'root': '/mock/dir'
        }
        
        # Call the function
        results, report_filename = collect_results(['/mock/dir'])
        
        # Assertions
        self.assertTrue('/mock/dir' in results['Python'])
        self.assertEqual(len(results['Python']['/mock/dir']), 1)
        self.assertTrue(report_filename.startswith('report_mock_dir_'))
    
    @patch('src.collector.os.path.isdir')
    def test_collect_results_dir_not_exists(self, mock_isdir):
        mock_isdir.return_value = False
        results, report_filename = collect_results(['/does/not/exist'])
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
