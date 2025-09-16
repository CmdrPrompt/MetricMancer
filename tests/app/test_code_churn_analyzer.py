import unittest
from unittest.mock import patch, MagicMock
import os
from src.kpis.codechurn.code_churn import CodeChurnAnalyzer

class TestCodeChurnAnalyzer(unittest.TestCase):
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root', side_effect=lambda x: x + '/.git')
    def test_init_repo_scan_pairs(self, mock_find_git_repo_root):
        analyzer = CodeChurnAnalyzer([('/repo', '/repo/scan')])
        self.assertEqual(len(analyzer.repo_scan_pairs), 1)
        git_root, scan_dir = analyzer.repo_scan_pairs[0]
        self.assertTrue(git_root.endswith('.git'))
        self.assertTrue(os.path.isabs(git_root))
        self.assertTrue(os.path.isabs(scan_dir))

    @patch('os.path.isdir', side_effect=lambda path: True if path in ['/tmp/repo', '/tmp/repo/.git'] else False)
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root', side_effect=lambda x: x)
    @patch('src.kpis.codechurn.code_churn.debug_print')
    @patch('pydriller.Repository')
    def test_analyze_churn_data(self, MockRepository, mock_debug_print, mock_find_git_repo_root, mock_isdir):
        # Setup fake commit/modification structure
        class FakeModification:
            def __init__(self, new_path):
                self.new_path = new_path
        class FakeCommit:
            def __init__(self, mods):
                self.modifications = mods
                self.modified_files = mods
        fake_commit = FakeCommit([FakeModification('file1.py'), FakeModification('file2.py')])
        MockRepository.return_value.traverse_commits.return_value = [fake_commit, fake_commit]
        # Use a real, non-None repo path and scan_dir
        repo_path = '/tmp/repo'
        scan_dir = '/tmp/repo'
        analyzer = CodeChurnAnalyzer([(repo_path, scan_dir)])
        churn_data = analyzer.analyze()
        # The code under test produces keys as os.path.join(repo_path, new_path)
        key1 = os.path.normpath(os.path.join(repo_path, 'file1.py'))
        key2 = os.path.normpath(os.path.join(repo_path, 'file2.py'))
        self.assertIn(key1, churn_data, f"{key1} not found in churn_data keys: {list(churn_data.keys())}")
        self.assertIn(key2, churn_data, f"{key2} not found in churn_data keys: {list(churn_data.keys())}")
        self.assertEqual(churn_data[key1], 2)
        self.assertEqual(churn_data[key2], 2)
        mock_debug_print.assert_any_call('[DEBUG] Churn analysis complete. Found churn data for 2 files.')

    @patch('os.path.isdir', side_effect=lambda path: True if path in ['/repo', '/repo/.git'] else False)
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root', side_effect=lambda x: x)
    @patch('src.kpis.codechurn.code_churn.debug_print')
    @patch('pydriller.Repository', side_effect=Exception('fail'))
    def test_analyze_handles_exception(self, MockRepository, mock_debug_print, mock_find_git_repo_root, mock_isdir):
        analyzer = CodeChurnAnalyzer([('/repo', '/repo')])
        churn_data = analyzer.analyze()
        self.assertEqual(churn_data, {})
        self.assertTrue(any('Could not analyze churn' in str(call[0][0]) for call in mock_debug_print.call_args_list))

if __name__ == '__main__':
    unittest.main()
