import unittest
from unittest.mock import patch
from src.kpis.codeownership.code_ownership import CodeOwnershipKPI



class TestCodeOwnershipKPICache(unittest.TestCase):
    @patch("src.kpis.codeownership.code_ownership.subprocess.run")
    @patch("src.kpis.codeownership.code_ownership.subprocess.check_output")
    def test_cache_usage(self, mock_check_output, mock_run):
        """
        Test that CodeOwnershipKPI uses a cache for git calls.
        Should call git only once per file, even if called multiple times.
        """
        # Mocka git ls-files så att filen alltid är spårad
        mock_run.return_value.returncode = 0
        mock_check_output.return_value = "author Thomas\n" * 10
        repo_root = "."
        file_path = "some_file.py"

        # Skapa två KPI-instans för samma fil
        kpi1 = CodeOwnershipKPI(file_path, repo_root)
        kpi2 = CodeOwnershipKPI(file_path, repo_root)

        # Kontrollera att git-anropet sker en gång (cache används)
        self.assertEqual(mock_check_output.call_count, 1, "Cache should be used, but git called twice.")


if __name__ == "__main__":
    unittest.main()
