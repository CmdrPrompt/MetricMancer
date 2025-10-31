import unittest
import os
from unittest.mock import patch
from src.kpis.codeownership.code_ownership import CodeOwnershipKPI


class TestCodeOwnershipKPICache(unittest.TestCase):
    def setUp(self):
        from src.utilities.git_cache import get_git_cache
        get_git_cache().clear_cache()

    @patch("os.path.exists", return_value=True)
    @patch("src.utilities.git_cache.subprocess.run")
    @patch("src.utilities.git_cache.subprocess.check_output")
    def test_cache_usage_and_value(self, mock_check_output, mock_run, mock_exists):
        """
        Test that CodeOwnershipKPI uses cache and returns correct value.
        Should call git only once per file, even if called multiple times.
        """
        # Mock git ls-files (tracked files check)
        mock_run.return_value.stdout = "some_file.py\n"
        mock_run.return_value.returncode = 0

        # Mock git blame output
        mock_check_output.return_value = "author Thomas\n" * 10

        file_path = "some_file.py"
        # Create dummy file so that os.path.exists returns True
        with open(file_path, "w") as f:
            f.write("# dummy\n")

        try:
            kpi1 = CodeOwnershipKPI(file_path=file_path, repo_root=".")
            # Check that git blame was called once (cache should be used)
            self.assertEqual(mock_check_output.call_count, 1, "Git blame should be called once for cache.")

            # Check the value calculation
            self.assertEqual(kpi1.value, {"Thomas": 100.0}, "KPI value calculation is incorrect.")

            # Second instance should use cache
            kpi2 = CodeOwnershipKPI(file_path=file_path, repo_root=".")
            # Git blame should still only be called once (cache hit)
            self.assertEqual(mock_check_output.call_count, 1, "Cache should prevent second git call.")
            self.assertEqual(kpi2.value, {"Thomas": 100.0}, "KPI value calculation is incorrect on cache hit.")
        finally:
            # Clean up test file
            os.remove(file_path)

    @patch("os.path.exists", return_value=False)
    def test_file_does_not_exist(self, mock_exists):
        """
        Test that CodeOwnershipKPI returns empty value for non-existent files.
        """
        kpi = CodeOwnershipKPI(file_path="missing.py", repo_root=".")
        self.assertEqual(kpi.value, {}, "KPI value should be empty for non-existent files.")

    @patch("os.path.exists", return_value=True)
    @patch("subprocess.run")
    def test_file_not_tracked_by_git(self, mock_run, mock_exists):
        """
        Test that CodeOwnershipKPI returns empty value for files not tracked by git.
        """
        mock_run.return_value.returncode = 1  # Simulate not tracked
        kpi = CodeOwnershipKPI(file_path="not_tracked.py", repo_root=".")
        self.assertEqual(kpi.value, {}, "KPI value should be empty for files not tracked by git.")

    @patch("os.path.exists", return_value=True)
    @patch("src.utilities.git_cache.subprocess.run")
    @patch("src.utilities.git_cache.subprocess.check_output", side_effect=Exception("blame error"))
    def test_blame_fails(self, mock_check_output, mock_run, mock_exists):
        """
        Test that CodeOwnershipKPI handles git blame failures gracefully.
        """
        mock_run.return_value.returncode = 0  # Tracked
        kpi = CodeOwnershipKPI(file_path="tracked.py", repo_root=".")
        self.assertEqual(kpi.value, {}, "KPI value should be empty if git blame fails.")


if __name__ == "__main__":
    unittest.main()
