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

if __name__ == '__main__':
    unittest.main()
