import unittest
from unittest.mock import patch, MagicMock
from src.churn.code_churn import CodeChurnAnalyzer

class TestCodeChurnAnalyzer(unittest.TestCase):
    @patch('pydriller.Repository')
    def test_analyze_mocked_git(self, MockRepository):
        # Setup mock commit and modified_files
        mock_commit = MagicMock()
        mock_commit.modified_files = []
        MockRepository.return_value.traverse_commits.return_value = [mock_commit]
        analyzer = CodeChurnAnalyzer([('/fake/repo', '/fake/scan')])
        churn = analyzer.analyze()
        self.assertIsInstance(churn, dict)

    def test_churn_in_src_with_repo_root_dot(self):
        from src.churn.code_churn import CodeChurnAnalyzer
        import os
        repo_root = os.path.abspath('.')
        scan_dir = os.path.abspath('./src')
        analyzer = CodeChurnAnalyzer([(repo_root, scan_dir)])
        churn_data = analyzer.analyze()
        # There should be at least one file with churn > 0 if there is git history
        churn_values = list(churn_data.values())
        assert isinstance(churn_data, dict)
        # If repo has history, at least one file should have churn > 0
        assert any(val > 0 for val in churn_values) or churn_values == [], 'No churn detected, check git history and file paths.'

if __name__ == '__main__':
    unittest.main()
