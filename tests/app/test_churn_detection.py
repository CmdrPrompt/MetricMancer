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
        # Create a file and commit
        self.file_path = os.path.join(self.repo_dir, 'testfile.txt')
        with open(self.file_path, 'w') as f:
            f.write('first line\n')
        subprocess.run(['git', 'add', 'testfile.txt'], cwd=self.repo_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.repo_dir, check=True)
        # Modify and commit again
        with open(self.file_path, 'a') as f:
            f.write('second line\n')
        subprocess.run(['git', 'add', 'testfile.txt'], cwd=self.repo_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Second commit'], cwd=self.repo_dir, check=True)

    def tearDown(self):
        shutil.rmtree(self.repo_dir)

    def test_churn_detected(self):
        analyzer = CodeChurnAnalyzer([(self.repo_dir, self.repo_dir)])
        churn_data = analyzer.analyze()
        # There should be churn for the file
        found = any(self.file_path in k or os.path.basename(self.file_path) in k for k in churn_data.keys())
        self.assertTrue(found, f"No churn found for file {self.file_path} in churn_data keys: {list(churn_data.keys())}")
        self.assertGreaterEqual(churn_data.get(self.file_path, 0), 1, "Churn value should be >= 1 for a file with changes")

if __name__ == '__main__':
    unittest.main()
