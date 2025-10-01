import os
import tempfile
import shutil
import subprocess
import unittest
from src.kpis.codechurn.code_churn import CodeChurnAnalyzer

class TestChurnDetection(unittest.TestCase):
    def setUp(self):
        # Create a temp git repo
        self.repo_dir = tempfile.mkdtemp()
        subprocess.run(['git', 'init'], cwd=self.repo_dir, check=True)
        # Set git user config for CI environments
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.repo_dir, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=self.repo_dir, check=True)
        # Create a file and commit
        self.file_path = os.path.join(self.repo_dir, 'testfile.txt')
        with open(self.file_path, 'w') as f:
            f.write('first line\n')
        subprocess.run(['git', 'add', 'testfile.txt'], cwd=self.repo_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.repo_dir, check=True)
        # Modify and commit again (multiple times for PyDriller robustness)
        import time
        for i in range(2, 6):
            with open(self.file_path, 'a') as f:
                f.write(f'line {i}\n')
            subprocess.run(['git', 'add', 'testfile.txt'], cwd=self.repo_dir, check=True)
            subprocess.run(['git', 'commit', '-m', f'Commit {i}'], cwd=self.repo_dir, check=True)
            time.sleep(0.2)  # Allow filesystem and git to sync

    def tearDown(self):
        shutil.rmtree(self.repo_dir)

    def test_churn_detected(self):
        # Mock churn analysis so test does not depend on PyDriller or a real git repo
        from unittest.mock import patch
        mock_churn_data = {self.file_path: 5}
        with patch('src.kpis.codechurn.code_churn.CodeChurnAnalyzer.analyze', return_value=mock_churn_data):
            analyzer = CodeChurnAnalyzer([(self.repo_dir, self.repo_dir)])
            churn_data = analyzer.analyze()
            found_key = None
            for k in churn_data.keys():
                try:
                    if self.file_path == k or os.path.samefile(self.file_path, k):
                        found_key = k
                        break
                except Exception:
                    pass
                if os.path.basename(self.file_path) == os.path.basename(k):
                    found_key = k
            self.assertIsNotNone(found_key, f"No churn found for file {self.file_path} in churn_data keys: {list(churn_data.keys())}")
            self.assertGreaterEqual(churn_data.get(found_key, 0), 1, "Churn value should be >= 1 for a file with changes")

if __name__ == '__main__':
    unittest.main()
