import unittest
from unittest.mock import patch
from src.kpis.codeownership.code_ownership import CodeOwnershipKPI


class TestCodeOwnershipKPI(unittest.TestCase):
    def setUp(self):
        # Rensa cache före varje test för att undvika delad state
        from src.utilities.git_cache import get_git_cache
        get_git_cache().clear_cache()

    @patch('os.path.exists', return_value=True)
    @patch('src.utilities.git_helpers.subprocess.run')
    def test_calculate_ownership_basic(self, mock_run, mock_exists):
        def mock_run_side_effect(cmd, **kwargs):
            result = unittest.mock.MagicMock()
            if 'ls-files' in cmd:
                result.stdout = 'dummy.py\n'
                result.returncode = 0
            elif 'blame' in cmd:
                # Simulate git blame output for a file with 4 lines, 2 authors
                result.stdout = 'author Alice\n' * 3 + 'author Bob\n'
                result.returncode = 0
            return result

        mock_run.side_effect = mock_run_side_effect

        kpi = CodeOwnershipKPI('/repo/dummy.py', '/repo')
        self.assertIn('Alice', kpi.value)
        self.assertIn('Bob', kpi.value)
        self.assertEqual(kpi.value['Alice'], 75.0)
        self.assertEqual(kpi.value['Bob'], 25.0)

    @patch('os.path.exists', return_value=True)
    @patch('src.utilities.git_helpers.subprocess.run')
    def test_calculate_ownership_error(self, mock_run, mock_exists):
        def mock_run_side_effect(cmd, **kwargs):
            result = unittest.mock.MagicMock()
            if 'ls-files' in cmd:
                result.stdout = 'dummy.py\n'
                result.returncode = 0
            elif 'blame' in cmd:
                raise Exception('not a git repo')
            return result

        mock_run.side_effect = mock_run_side_effect

        kpi = CodeOwnershipKPI('/repo/dummy.py', '/repo')
        self.assertEqual(kpi.value, {})


if __name__ == '__main__':
    unittest.main()
