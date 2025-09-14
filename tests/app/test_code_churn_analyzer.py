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

    @patch('src.kpis.codechurn.code_churn.find_git_repo_root', side_effect=lambda x: x)
    @patch('src.kpis.codechurn.code_churn.debug_print')
    @patch('pydriller.Repository')
    def test_analyze_churn_data(self, MockRepository, mock_debug_print, mock_find_git_repo_root):
        # Setup fake commit/modification structure
        class FakeModification:
            def __init__(self, new_path):
                self.new_path = new_path
        class FakeCommit:
            def __init__(self, mods):
                self.modifications = mods
        fake_commit = FakeCommit([FakeModification('file1.py'), FakeModification('file2.py')])
        MockRepository.return_value.traverse_commits.return_value = [fake_commit, fake_commit]
        analyzer = CodeChurnAnalyzer([('/repo', '/repo')])
        churn_data = analyzer.analyze()
        abs_file1 = os.path.normpath(os.path.join(os.path.abspath('/repo'), 'file1.py'))
        abs_file2 = os.path.normpath(os.path.join(os.path.abspath('/repo'), 'file2.py'))
        # Robust path comparison
        def find_key(target, d):
            for k in d:
                if os.path.normcase(os.path.normpath(k)) == os.path.normcase(target):
                    return k
            return None
        k1 = find_key(abs_file1, churn_data)
        k2 = find_key(abs_file2, churn_data)
        self.assertIsNotNone(k1, f"{abs_file1} not found in churn_data keys: {list(churn_data.keys())}")
        self.assertIsNotNone(k2, f"{abs_file2} not found in churn_data keys: {list(churn_data.keys())}")
        self.assertEqual(churn_data[k1], 2)
        self.assertEqual(churn_data[k2], 2)
        mock_debug_print.assert_any_call('[DEBUG] Churn analysis complete. Found churn data for 2 files.')

    @patch('src.kpis.codechurn.code_churn.find_git_repo_root', side_effect=lambda x: x)
    @patch('src.kpis.codechurn.code_churn.debug_print')
    @patch('pydriller.Repository', side_effect=Exception('fail'))
    def test_analyze_handles_exception(self, MockRepository, mock_debug_print, mock_find_git_repo_root):
        analyzer = CodeChurnAnalyzer([('/repo', '/repo')])
        churn_data = analyzer.analyze()
        self.assertEqual(churn_data, {})
        self.assertTrue(any('Could not analyze churn' in str(call[0][0]) for call in mock_debug_print.call_args_list))

if __name__ == '__main__':
    unittest.main()
