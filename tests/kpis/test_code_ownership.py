import unittest
from unittest.mock import patch
from src.kpis.codeownership.code_ownership import CodeOwnershipKPI

class TestCodeOwnershipKPI(unittest.TestCase):
    @patch('subprocess.check_output')
    def test_calculate_ownership_basic(self, mock_check_output):
        # Simulate git blame output for a file with 4 lines, 2 authors
        mock_check_output.return_value = (
            'author Alice\n' * 3 + 'author Bob\n'
        )
        kpi = CodeOwnershipKPI('dummy.py', '/repo')
        self.assertIn('Alice', kpi.value)
        self.assertIn('Bob', kpi.value)
        self.assertEqual(kpi.value['Alice'], 75.0)
        self.assertEqual(kpi.value['Bob'], 25.0)

    @patch('subprocess.check_output', side_effect=Exception('not a git repo'))
    def test_calculate_ownership_error(self, mock_check_output):
        kpi = CodeOwnershipKPI('dummy.py', '/repo')
        self.assertIn('error', kpi.value)
        self.assertIn('not a git repo', kpi.value['error'])

if __name__ == '__main__':
    unittest.main()
