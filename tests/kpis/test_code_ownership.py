import unittest
from unittest.mock import patch
from src.kpis.codeownership.code_ownership import CodeOwnershipKPI


class TestCodeOwnershipKPI(unittest.TestCase):
    def setUp(self):
        # Rensa cache före varje test för att undvika delad state
        from src.kpis.codeownership.code_ownership import CodeOwnershipKPI
        CodeOwnershipKPI._ownership_cache.clear()
    @patch('os.path.exists', return_value=True)
    @patch('subprocess.run')
    @patch('subprocess.check_output')
    def test_calculate_ownership_basic(self, mock_check_output, mock_run, mock_exists):
        # Simulate git blame output for a file with 4 lines, 2 authors
        mock_check_output.return_value = (
            'author Alice\n' * 3 + 'author Bob\n'
        )
        mock_run.return_value.returncode = 0  # File is tracked by git
        kpi = CodeOwnershipKPI('dummy.py', '/repo')
        self.assertIn('Alice', kpi.value)
        self.assertIn('Bob', kpi.value)
        self.assertEqual(kpi.value['Alice'], 75.0)
        self.assertEqual(kpi.value['Bob'], 25.0)

    @patch('os.path.exists', return_value=True)
    @patch('subprocess.run')
    @patch('subprocess.check_output', side_effect=Exception('not a git repo'))
    def test_calculate_ownership_error(self, mock_check_output, mock_run, mock_exists):
        mock_run.return_value.returncode = 0  # File is tracked by git
        kpi = CodeOwnershipKPI('dummy.py', '/repo')
        self.assertEqual(kpi.value, {'ownership': 'N/A'})


if __name__ == '__main__':
    unittest.main()
