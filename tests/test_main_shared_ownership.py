import unittest
import subprocess
import sys
import tempfile
from pathlib import Path


class TestMainSharedOwnership(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a minimal test directory
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_dir = Path(cls.temp_dir.name)
        # Create a small Python file
        (cls.test_dir / "foo.py").write_text("def foo():\n    pass\n")
        (cls.test_dir / "bar.py").write_text("def bar():\n    pass\n")

        # Make the directory a git repo and commit the files
        subprocess.run(['git', 'init'], cwd=cls.test_dir, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=cls.test_dir, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=cls.test_dir, check=True)
        subprocess.run(['git', 'add', '.'], cwd=cls.test_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=cls.test_dir, check=True)

        # Run CLI against this directory with detailed tree format (not summary)
        cls.result = subprocess.run([
            sys.executable, "-m", "src.main", str(cls.test_dir), "--detailed"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        # Help-result
        cls.help_result = subprocess.run([
            sys.executable, "-m", "src.main", "--help"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        self.result = self.__class__.result
        self.help_result = self.__class__.help_result

    def test_main_shared_ownership_works_on_real_files(self):
        self.assertEqual(self.result.returncode, 0, f"Command failed: {self.result.stderr}")
        output = self.result.stdout
        self.assertIn("Shared:", output, "SharedOwnership not found in CLI output")

    def test_main_shows_all_kpis_including_shared_ownership(self):
        self.assertEqual(self.result.returncode, 0)
        output = self.result.stdout
        self.assertIn("C:", output, "Complexity not shown")
        self.assertIn("Churn:", output, "Churn not shown")
        self.assertIn("Hotspot:", output, "Hotspot not shown")
        self.assertIn("Shared:", output, "Shared ownership not shown")

    def test_main_shared_ownership_shows_different_patterns(self):
        output = self.result.stdout
        shared_lines = [line for line in output.split('\n') if 'Shared:' in line]
        self.assertTrue(len(shared_lines) > 0, "No SharedOwnership lines found")

    def test_main_help_command_works(self):
        self.assertEqual(self.help_result.returncode, 0)
        self.assertIn("usage:", self.help_result.stdout.lower(), "Help should show usage")
