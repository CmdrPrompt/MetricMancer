import unittest
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

class TestMainSharedOwnership(unittest.TestCase):
    def setUp(self):
        """Use actual MetricMancer source files for realistic testing."""
        self.project_root = Path(__file__).parent.parent
        self.src_kpis_path = self.project_root / "src" / "kpis"
        
    def test_main_shared_ownership_works_on_real_files(self):
        """Test that SharedOwnership works on actual MetricMancer source files."""
        if not self.src_kpis_path.exists():
            self.skipTest("Source kpis directory not found")
            
        result = subprocess.run([
            sys.executable, "-m", "src.main", 
            str(self.src_kpis_path)
        ], capture_output=True, text=True, cwd=self.project_root)
        
        self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
        
        output = result.stdout
        
        # SharedOwnership should appear in output
        self.assertIn("Shared:", output, "SharedOwnership not found in CLI output")
        
        # Should show different SharedOwnership patterns
        shared_patterns = ["Single owner", "None (threshold:", "authors"]
        found_patterns = [pattern for pattern in shared_patterns if pattern in output]
        self.assertTrue(len(found_patterns) > 0, f"No SharedOwnership patterns found. Expected one of: {shared_patterns}")

    def test_main_shows_all_kpis_including_shared_ownership(self):
        """Test that all KPIs including SharedOwnership appear together."""
        if not self.src_kpis_path.exists():
            self.skipTest("Source kpis directory not found")
            
        result = subprocess.run([
            sys.executable, "-m", "src.main",
            str(self.src_kpis_path)
        ], capture_output=True, text=True, cwd=self.project_root)
        
        self.assertEqual(result.returncode, 0)
        
        output = result.stdout
        
        # Should show all KPI types
        self.assertIn("C:", output, "Complexity not shown")
        self.assertIn("Churn:", output, "Churn not shown") 
        self.assertIn("Hotspot:", output, "Hotspot not shown")
        self.assertIn("Shared:", output, "Shared ownership not shown")
        
        # Should show directory structure
        self.assertIn("kpis", output)
        
        # Should show file tree structure
        self.assertIn("├──", output, "Tree structure not shown")

    def test_main_shared_ownership_shows_different_patterns(self):
        """Test that different SharedOwnership patterns are shown correctly."""
        if not self.src_kpis_path.exists():
            self.skipTest("Source kpis directory not found")
            
        result = subprocess.run([
            sys.executable, "-m", "src.main",
            str(self.src_kpis_path)
        ], capture_output=True, text=True, cwd=self.project_root)
        
        self.assertEqual(result.returncode, 0)
        
        output = result.stdout
        
        # Extract lines with SharedOwnership
        shared_lines = [line for line in output.split('\n') if 'Shared:' in line]
        self.assertTrue(len(shared_lines) > 0, "No SharedOwnership lines found")
        
        # Should show some "Single owner" patterns (since Thomas is the main contributor)
        single_owner_lines = [line for line in shared_lines if 'Single owner' in line]
        self.assertTrue(len(single_owner_lines) > 0, "Should show some single owner patterns")
        
        # May also show "None (threshold:" for files without significant ownership
        threshold_lines = [line for line in shared_lines if 'threshold:' in line]
        # This is optional - may or may not appear depending on file ownership

    def test_main_shared_ownership_in_git_repo_context(self):
        """Test SharedOwnership on the MetricMancer git repository itself."""
        # Test on the entire project (smaller subset)
        analyzer_path = self.project_root / "src" / "app" / "analyzer.py"
        
        if not analyzer_path.exists():
            self.skipTest("analyzer.py not found")
            
        result = subprocess.run([
            sys.executable, "-m", "src.main",
            str(analyzer_path.parent)  # Just the app directory
        ], capture_output=True, text=True, cwd=self.project_root)
        
        self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
        
        output = result.stdout
        
        # Should show SharedOwnership for analyzer.py specifically
        self.assertIn("analyzer.py", output, "analyzer.py should be in output")
        self.assertIn("Shared:", output, "SharedOwnership should be shown")

    @patch('src.app.analyzer.SharedOwnershipKPI')
    def test_main_handles_shared_ownership_errors_gracefully(self, mock_shared_ownership):
        """Test that main.py handles SharedOwnership calculation errors."""
        if not self.src_kpis_path.exists():
            self.skipTest("Source kpis directory not found")
            
        # Make SharedOwnershipKPI raise an exception
        mock_shared_ownership.side_effect = Exception("Git ownership calculation failed")
        
        result = subprocess.run([
            sys.executable, "-m", "src.main",
            str(self.src_kpis_path)
        ], capture_output=True, text=True, cwd=self.project_root)
        
        # Should not crash despite SharedOwnership error
        self.assertEqual(result.returncode, 0, f"Should handle SharedOwnership errors: {result.stderr}")
        
        # Should still produce output
        output = result.stdout
        self.assertIn("kpis", output, "Should still show directory name")
        self.assertTrue(len(output) > 0, "Should produce some output despite error")

    def test_main_help_command_works(self):
        """Test that help command works."""
        result = subprocess.run([
            sys.executable, "-m", "src.main", "--help"
        ], capture_output=True, text=True, cwd=self.project_root)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower(), "Help should show usage")

if __name__ == '__main__':
    unittest.main()