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

        repo_root = "."
        file_path = "some_file.py"
        # Skapa dummy-fil så att os.path.exists returnerar True
        with open(file_path, "w") as f:
            f.write("# dummy\n")

        try:
            # Skapa två KPI-instans för samma fil
            kpi1 = CodeOwnershipKPI(file_path, repo_root)
            kpi2 = CodeOwnershipKPI(file_path, repo_root)

            # Kontrollera att git-anropet sker en gång (cache används)
            self.assertEqual(mock_check_output.call_count, 1, "Cache should be used, but git called twice.")
        finally:
            # Städa upp testfilen
            os.remove(file_path)


if __name__ == "__main__":
    unittest.main()
