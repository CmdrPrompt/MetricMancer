import unittest
from unittest.mock import patch
from src.kpis.codeownership.code_ownership import CodeOwnershipKPI


class TestCodeOwnershipKPI(unittest.TestCase):
    @patch('os.path.exists', return_value=False)
    def test_file_does_not_exist(self, mock_exists):
        kpi = CodeOwnershipKPI(file_path='missing.py', repo_root='.')
        self.assertEqual(kpi.value, {})

    @patch('os.path.exists', return_value=True)
    @patch('subprocess.run')
    def test_file_not_tracked_by_git(self, mock_run, mock_exists):
        mock_run.return_value.returncode = 1  # Simulate not tracked
        kpi = CodeOwnershipKPI(file_path='not_tracked.py', repo_root='.')
        self.assertEqual(kpi.value, {})

    @patch('os.path.exists', return_value=True)
    @patch('src.utilities.git_cache.subprocess.run')
    @patch('src.utilities.git_cache.subprocess.check_output')
    def test_file_tracked_and_blame_works(self, mock_check_output, mock_run, mock_exists):
        # Rensa cache för att undvika påverkan från andra tester
        from src.utilities.git_cache import get_git_cache
        get_git_cache().clear_cache()
        
        # Mock git ls-files (för tracked file check)
        mock_run.return_value.stdout = 'tracked.py\n'
        mock_run.return_value.returncode = 0
        
        # Mock git blame
        mock_check_output.return_value = 'author Alice\nauthor Bob\nauthor Alice\n'
        
        kpi = CodeOwnershipKPI(file_path='tracked.py', repo_root='.')
        # Alice: 2/3, Bob: 1/3
        self.assertAlmostEqual(kpi.value['Alice'], 66.7, places=1)
        self.assertAlmostEqual(kpi.value['Bob'], 33.3, places=1)

    @patch('os.path.exists', return_value=True)
    @patch('subprocess.run')
    @patch('subprocess.check_output', side_effect=Exception('blame error'))
    def test_blame_fails(self, mock_check_output, mock_run, mock_exists):
        mock_run.return_value.returncode = 0  # Tracked
        kpi = CodeOwnershipKPI(file_path='tracked.py', repo_root='.')
        self.assertEqual(kpi.value, {})


if __name__ == '__main__':
    unittest.main()
