import unittest
from unittest.mock import patch, MagicMock
from src.kpis.codechurn.code_churn import CodeChurnAnalyzer

class TestCodeChurnAnalyzerEdgeCases(unittest.TestCase):
    def test_empty_repo_scan_pairs(self):
        analyzer = CodeChurnAnalyzer([])
        result = analyzer.analyze()
        self.assertEqual(result, {})

    @patch('src.kpis.codechurn.code_churn.find_git_repo_root', return_value=None)
    def test_find_git_repo_root_none(self, mock_find_git):
        import os
        analyzer = CodeChurnAnalyzer([('/repo', '/repo/scan')])
        # None as git root should still be handled gracefully
        expected_scan = os.path.abspath('/repo/scan')
        self.assertIn((None, expected_scan), analyzer.repo_scan_pairs)

    @patch('src.kpis.codechurn.code_churn.find_git_repo_root', side_effect=Exception('fail'))
    def test_find_git_repo_root_exception(self, mock_find_git):
        # Should not raise, but skip or handle
        try:
            analyzer = CodeChurnAnalyzer([('/repo', '/repo/scan')])
            self.assertTrue(any(isinstance(pair[0], str) or pair[0] is None for pair in analyzer.repo_scan_pairs))
        except Exception as e:
            self.fail(f"Exception should be handled, got: {e}")

    @patch('src.kpis.codechurn.code_churn.find_git_repo_root', return_value='/repo')
    @patch('src.kpis.codechurn.code_churn.debug_print')
    @patch('pydriller.Repository', side_effect=Exception('fail'))
    def test_analyze_handles_pydriller_exception(self, MockRepository, mock_debug_print, mock_find_git):
        analyzer = CodeChurnAnalyzer([('/repo', '/repo')])
        result = analyzer.analyze()
        self.assertEqual(result, {})
        self.assertTrue(any('Could not analyze churn' in str(call[0][0]) for call in mock_debug_print.call_args_list))

    @patch('src.kpis.codechurn.code_churn.find_git_repo_root', return_value='/repo')
    @patch('src.kpis.codechurn.code_churn.debug_print')
    @patch('pydriller.Repository')
    def test_analyze_no_churn_data(self, MockRepository, mock_debug_print, mock_find_git):
        # No commits, no churn data
        MockRepository.return_value.traverse_commits.return_value = []
        analyzer = CodeChurnAnalyzer([('/repo', '/repo')])
        result = analyzer.analyze()
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
