import unittest
from unittest.mock import patch
from src.kpis.codeownership.code_ownership import CodeOwnershipKPI


class TestCodeOwnershipKPI(unittest.TestCase):
    def setUp(self):
        # Rensa cache före varje test för att undvika delad state
        from src.utilities.git_cache import get_git_cache
        get_git_cache().clear_cache()

    @patch('os.path.exists', return_value=True)
    @patch('src.utilities.git_cache.subprocess.run')
    @patch('src.utilities.git_cache.subprocess.check_output')
    def test_calculate_ownership_basic(self, mock_check_output, mock_run, mock_exists):
        # Mock git ls-files
        mock_run.return_value.stdout = 'dummy.py\n'
        mock_run.return_value.returncode = 0

        # Simulate git blame output for a file with 4 lines, 2 authors
        mock_check_output.return_value = (
            'author Alice\n' * 3 + 'author Bob\n'
        )

        kpi = CodeOwnershipKPI('/repo/dummy.py', '/repo')
        self.assertIn('Alice', kpi.value)
        self.assertIn('Bob', kpi.value)
        self.assertEqual(kpi.value['Alice'], 75.0)
        self.assertEqual(kpi.value['Bob'], 25.0)

    @patch('os.path.exists', return_value=True)
    @patch('src.utilities.git_cache.subprocess.run')
    @patch('src.utilities.git_cache.subprocess.check_output', side_effect=Exception('not a git repo'))
    def test_calculate_ownership_error(self, mock_check_output, mock_run, mock_exists):
        # Mock git ls-files to indicate file is tracked
        mock_run.return_value.stdout = 'dummy.py\n'
        mock_run.return_value.returncode = 0

        kpi = CodeOwnershipKPI('/repo/dummy.py', '/repo')
        self.assertEqual(kpi.value, {})


if __name__ == '__main__':
    unittest.main()
