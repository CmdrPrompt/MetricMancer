import unittest
import os
from unittest.mock import patch
from src.kpis.codeownership.code_ownership import CodeOwnershipKPI


class TestCodeOwnershipKPICache(unittest.TestCase):
    def setUp(self):
        from src.utilities.git_cache import get_git_cache
        get_git_cache().clear_cache()

    @patch("src.utilities.git_cache.subprocess.run")
    @patch("src.utilities.git_cache.subprocess.check_output")
    def test_cache_usage(self, mock_check_output, mock_run):
        """
        Test that CodeOwnershipKPI uses a cache for git calls.
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
            # Create CodeOwnershipKPI instance - this should trigger git calls
            kpi = CodeOwnershipKPI(file_path=file_path, repo_root=".")

            # Check that git blame was called once (cache should be used)
            self.assertEqual(mock_check_output.call_count, 1, "Git blame should be called once for cache.")

            # Create another instance for the same file - should use cache
            kpi2 = CodeOwnershipKPI(file_path=file_path, repo_root=".")

            # Git blame should still only be called once (cache hit)
            self.assertEqual(mock_check_output.call_count, 1, "Cache should prevent second git call.")

        finally:
            # Clean up test file
            os.remove(file_path)


if __name__ == "__main__":
    unittest.main()
