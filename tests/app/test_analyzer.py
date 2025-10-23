import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from src.app import Analyzer
from src.kpis.codechurn import ChurnKPI
from src.kpis.complexity import ComplexityAnalyzer
from src.kpis.hotspot import HotspotKPI
from src.kpis.model import RepoInfo, ScanDir, File
from src.languages.config import Config


class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory structure and mock objects for testing."""
        self.test_dir = Path("test_analyzer_temp_dir").resolve()
        self.test_dir.mkdir(exist_ok=True)

        # Create a mock config
        self.config = Config()

        # --- Create test file structure ---
        self.repo1_path = self.test_dir / "repo1"
        (self.repo1_path / "src").mkdir(parents=True)
        (self.repo1_path / "src" / "main.py").write_text("def main(): pass")
        (self.repo1_path / "src" / "utils.py").write_text("def util(): pass")

        self.repo2_path = self.test_dir / "repo2"
        (self.repo2_path).mkdir()
        (self.repo2_path / "app.java").write_text("class App {}")

        # --- Create input for Analyzer.analyze (simulating Scanner output) ---
        self.main_py_path = self.repo1_path / "src" / "main.py"
        self.utils_py_path = self.repo1_path / "src" / "utils.py"
        self.app_java_path = self.repo2_path / "app.java"

        self.scanner_files = [
            {'path': str(self.main_py_path), 'root': str(self.repo1_path), 'ext': '.py'},
            {'path': str(self.utils_py_path), 'root': str(self.repo1_path), 'ext': '.py'},
            {'path': str(self.app_java_path), 'root': str(self.repo2_path), 'ext': '.java'},
        ]

        self.analyzer = Analyzer(self.config.languages, threshold_low=10, threshold_high=20)

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_analyze_structure_and_kpis(self):
        """
        Test that the analyzer correctly builds the RepoInfo structure and assigns KPIs.
        """
        # --- Mock external dependencies and KPI calculations ---

        # Mock churn data
        mock_churn_data = {
            str(self.main_py_path): 10,
            str(self.utils_py_path): 5,
            str(self.app_java_path): 20,
        }

        # Mock function analysis data
        mock_functions_data = [
            {'name': 'func_a', 'complexity': 8},
            {'name': 'func_b', 'complexity': 7}
        ]
        # Total complexity for the file will be 8 + 7 = 15

        # Mock KPI objects to return fixed values
        with patch.object(ComplexityAnalyzer, 'analyze_functions', return_value=mock_functions_data), \
            patch.object(ChurnKPI, 'calculate',
                         side_effect=lambda file_path, **kwargs: ChurnKPI(value=mock_churn_data.get(file_path, 0))), \
            patch.object(HotspotKPI, 'calculate',
                         # --- Run the analysis ---
                         side_effect=lambda complexity, churn, **kwargs: HotspotKPI(value=complexity * churn)):
            summary = self.analyzer.analyze(self.scanner_files)

            # --- Assertions ---
            # With the new logic, all files from the same git repo are grouped together
            # Since both repo1 and repo2 are within the same git repo in the test environment,
            # they should be combined into a single RepoInfo object
            self.assertEqual(len(summary), 1)  # One combined repo found

            # The repo root should be the git root (test directory or workspace)
            repo_keys = list(summary.keys())
            combined_repo_info = summary[repo_keys[0]]
            self.assertIsInstance(combined_repo_info, RepoInfo)

            # Check that both repo1 and repo2 structures are present
            # The structure is: RepoInfo -> test_analyzer_temp_dir -> repo1/repo2
            temp_dir_name = self.test_dir.name  # "test_analyzer_temp_dir"
            self.assertIn(temp_dir_name, combined_repo_info.scan_dirs)
            temp_dir = combined_repo_info.scan_dirs[temp_dir_name]
            self.assertIsInstance(temp_dir, ScanDir)

            # Repo1 structure: temp_dir -> repo1 -> src -> files
            self.assertIn("repo1", temp_dir.scan_dirs)
            repo1_dir = temp_dir.scan_dirs["repo1"]
            self.assertIsInstance(repo1_dir, ScanDir)

            self.assertIn("src", repo1_dir.scan_dirs)
            src_dir = repo1_dir.scan_dirs["src"]
            self.assertIsInstance(src_dir, ScanDir)
            self.assertEqual(src_dir.dir_name, "src")

            # Check files in src
            self.assertEqual(len(src_dir.files), 2)
            self.assertIn("main.py", src_dir.files)
            self.assertIn("utils.py", src_dir.files)

            # Check KPIs for main.py
            main_py_file = src_dir.files["main.py"]
            self.assertIsInstance(main_py_file, File)
            self.assertEqual(main_py_file.kpis["complexity"].value, 15)
            self.assertEqual(main_py_file.kpis["complexity"].calculation_values["function_count"], 2)
            self.assertEqual(main_py_file.kpis["churn"].value, 10)
            self.assertEqual(main_py_file.kpis["hotspot"].value, 150)  # 15 * 10

            # Check function data within the file
            self.assertEqual(len(main_py_file.functions), 2)
            self.assertEqual(main_py_file.functions[0].name, 'func_a')
            self.assertEqual(main_py_file.functions[0].kpis['complexity'].value, 8)
            self.assertEqual(main_py_file.functions[1].name, 'func_b')
            self.assertEqual(main_py_file.functions[1].kpis['complexity'].value, 7)

            # Check KPIs for utils.py
            utils_py_file = src_dir.files["utils.py"]
            self.assertEqual(utils_py_file.kpis["complexity"].value, 15)
            self.assertEqual(utils_py_file.kpis["churn"].value, 5)
            self.assertEqual(utils_py_file.kpis["hotspot"].value, 75)  # 15 * 5

            # Repo2 structure: temp_dir -> repo2 -> app.java file
            self.assertIn("repo2", temp_dir.scan_dirs)
            repo2_dir = temp_dir.scan_dirs["repo2"]
            self.assertIsInstance(repo2_dir, ScanDir)

            self.assertIn("app.java", repo2_dir.files)
            app_java_file = repo2_dir.files["app.java"]
            self.assertIsInstance(app_java_file, File)
            self.assertEqual(app_java_file.kpis["complexity"].value, 15)
            self.assertEqual(app_java_file.kpis["churn"].value, 20)
            self.assertEqual(app_java_file.kpis["hotspot"].value, 300)  # 15 * 20

    @patch('src.app.kpi.file_analyzer.debug_print')  # FileAnalyzer handles file processing
    def test_skips_unsupported_extension_files(self, mock_debug_print):
        """Unsupported extensions should be skipped and not appear in RepoInfo."""
        # Create an unsupported file in repo1 root
        readme_path = self.repo1_path / "README.md"
        readme_path.write_text("This is a README")

        # Extend scanner input to include unsupported file
        files = list(self.scanner_files) + [
            {'path': str(readme_path), 'root': str(self.repo1_path), 'ext': '.md'},
        ]

        # Mock churn and complexity
        mock_churn_data = {
            str(self.main_py_path): 3,
            str(self.utils_py_path): 2,
        }
        mock_functions_data = [
            {'name': 'f1', 'complexity': 5},
            {'name': 'f2', 'complexity': 4},
        ]
        with patch.object(ComplexityAnalyzer, 'analyze_functions', return_value=mock_functions_data), \
                patch.object(ChurnKPI, 'calculate',
                             side_effect=lambda file_path, **kwargs: ChurnKPI(value=mock_churn_data.get(file_path, 0))), \
                patch.object(HotspotKPI, 'calculate',
                             side_effect=lambda complexity, churn, **kwargs: HotspotKPI(value=complexity * churn)):
            summary = self.analyzer.analyze(files)

            # With the new logic, all files from the same git repo are grouped together
            self.assertEqual(len(summary), 1)  # One combined repo found
            repo_keys = list(summary.keys())
            combined_repo_info = summary[repo_keys[0]]

            # Navigate to repo1: RepoInfo -> test_analyzer_temp_dir -> repo1
            temp_dir_name = self.test_dir.name  # "test_analyzer_temp_dir"
            temp_dir = combined_repo_info.scan_dirs[temp_dir_name]
            repo1_dir = temp_dir.scan_dirs["repo1"]

            # README.md is unsupported and must not be present under repo1 root files
            self.assertNotIn("README.md", repo1_dir.files)
            # Logga alla debug_print-anrop för felsökning
            print("DEBUG_PRINT CALLS:")
            for call in mock_debug_print.call_args_list:
                print(call)
            # Robust substring-match mot debug_print-anropet
            expected_substr = "Skipping file with unknown extension"
            self.assertTrue(any(
                expected_substr in str(call.args[0]) and "README.md" in str(call.args[0])
                for call in mock_debug_print.call_args_list
            ), f"Expected debug_print call containing '{expected_substr}' and the file name. "
                f"Actual calls: {[str(call.args[0]) for call in mock_debug_print.call_args_list]}")

    @patch('src.app.kpi.file_analyzer.debug_print')  # FileAnalyzer handles file processing
    def test_unreadable_file_is_skipped_and_warned(self, mock_debug_print):
        """Analyzer should skip files it cannot read and continue processing others."""
        blocked_path = self.repo1_path / "src" / "blocked.py"
        blocked_path.write_text("def blocked(): pass")
        # Use a non-existent path to simulate read failure without patching I/O
        blocked_missing_path = self.repo1_path / "src" / "blocked_missing.py"

        files = list(self.scanner_files) + [
            {'path': str(blocked_missing_path), 'root': str(self.repo1_path), 'ext': '.py'},
        ]

        mock_churn_data = {
            str(self.main_py_path): 1,
            str(self.utils_py_path): 1,
            str(blocked_missing_path): 10,
        }

        mock_functions_data = [
            {'name': 'f1', 'complexity': 2},
        ]

        with patch.object(ComplexityAnalyzer, 'analyze_functions', return_value=mock_functions_data), \
                patch.object(ChurnKPI, 'calculate',
                             side_effect=lambda file_path, **kwargs: ChurnKPI(value=mock_churn_data.get(file_path, 0))), \
                patch.object(HotspotKPI, 'calculate',
                             side_effect=lambda complexity, churn, **kwargs: HotspotKPI(value=complexity * churn)):
            summary = self.analyzer.analyze(files)

        # With the new logic, all files from the same git repo are grouped together
        self.assertEqual(len(summary), 1)  # One combined repo found
        repo_keys = list(summary.keys())
        combined_repo_info = summary[repo_keys[0]]

        # Navigate to repo1 -> src: RepoInfo -> test_analyzer_temp_dir -> repo1 -> src
        temp_dir_name = self.test_dir.name  # "test_analyzer_temp_dir"
        temp_dir = combined_repo_info.scan_dirs[temp_dir_name]
        repo1_dir = temp_dir.scan_dirs["repo1"]
        src_dir = repo1_dir.scan_dirs["src"]

        # The file should not exist under the src directory
        self.assertNotIn("blocked_missing.py", src_dir.files)
        # A warning should have been printed
        self.assertTrue(any(
            "Unable to read" in str(call.args[0]) and str(blocked_missing_path) in str(call.args[0])
            for call in mock_debug_print.call_args_list
        ), f"Expected a debug_print call containing 'Unable to read' and the missing path. "
            f"Actual calls: {[str(call.args[0]) for call in mock_debug_print.call_args_list]}")

    def test_builds_nested_scandir_hierarchy(self):
        """Analyzer should create nested ScanDir objects for deep paths."""
        nested_path = self.repo1_path / "src" / "pkg" / "module" / "utils" / "helper.py"
        (nested_path.parent).mkdir(parents=True, exist_ok=True)
        nested_path.write_text("def helper(): pass")

        files = list(self.scanner_files) + [
            {'path': str(nested_path), 'root': str(self.repo1_path), 'ext': '.py'},
        ]

        mock_functions_data = [
            {'name': 'a', 'complexity': 6},
            {'name': 'b', 'complexity': 3},
        ]
        with patch.object(ComplexityAnalyzer, 'analyze_functions', return_value=mock_functions_data):
            summary = self.analyzer.analyze(files)

        # With the new logic, all files from the same git repo are grouped together
        self.assertEqual(len(summary), 1)  # One combined repo found
        repo_keys = list(summary.keys())
        combined_repo_info = summary[repo_keys[0]]

        # The structure is: RepoInfo -> test_analyzer_temp_dir -> repo1 -> src -> pkg -> module -> utils -> helper.py
        temp_dir_name = self.test_dir.name  # "test_analyzer_temp_dir"
        self.assertIn(temp_dir_name, combined_repo_info.scan_dirs)
        temp_dir = combined_repo_info.scan_dirs[temp_dir_name]

        # Navigate to repo1 -> src -> pkg -> module -> utils
        repo1_dir = temp_dir.scan_dirs["repo1"]
        src_dir = repo1_dir.scan_dirs["src"]
        self.assertIn("pkg", src_dir.scan_dirs)
        pkg_dir = src_dir.scan_dirs["pkg"]
        self.assertIn("module", pkg_dir.scan_dirs)
        module_dir = pkg_dir.scan_dirs["module"]
        self.assertIn("utils", module_dir.scan_dirs)
        utils_dir = module_dir.scan_dirs["utils"]
        self.assertIn("helper.py", utils_dir.files)
        helper_file = utils_dir.files["helper.py"]
        # file_path should be relative to repo root (which is now test_analyzer_temp_dir)
        expected_path = f"{self.test_dir.name}/repo1/src/pkg/module/utils/helper.py"
        self.assertEqual(helper_file.file_path.replace("\\", "/"), expected_path)

    @patch('src.utilities.git_cache.GitDataCache.get_churn_data')
    def test_hotspot_kpi_includes_calculation_values(self, mock_git_cache_churn):
        """Hotspot KPI should include complexity and churn in calculation_values."""
        churn_values = {
            str(self.main_py_path): 7,
            str(self.utils_py_path): 4,
            str(self.app_java_path): 0,
        }

        # Mock git cache to return expected churn values
        def mock_churn_lookup(repo_root, file_path):
            # Convert relative path back to absolute for lookup
            abs_path = str(Path(repo_root) / file_path)
            return churn_values.get(abs_path, 0)

        mock_git_cache_churn.side_effect = mock_churn_lookup

        mock_functions_data = [
            {'name': 'f1', 'complexity': 5},
            {'name': 'f2', 'complexity': 4},
        ]
        with patch.object(ComplexityAnalyzer, 'analyze_functions', return_value=mock_functions_data):
            summary = self.analyzer.analyze(self.scanner_files)

        # With the new logic, all files from the same git repo are grouped together
        self.assertEqual(len(summary), 1)  # One combined repo found
        repo_keys = list(summary.keys())
        combined_repo_info = summary[repo_keys[0]]

        # Navigate to the main.py file: RepoInfo -> test_analyzer_temp_dir -> repo1 -> src -> main.py
        temp_dir_name = self.test_dir.name  # "test_analyzer_temp_dir"
        temp_dir = combined_repo_info.scan_dirs[temp_dir_name]
        repo1_dir = temp_dir.scan_dirs["repo1"]
        src_dir = repo1_dir.scan_dirs["src"]
        main_file = src_dir.files["main.py"]
        # Complexity sum = 9
        self.assertEqual(main_file.kpis["complexity"].value, 9)
        self.assertEqual(main_file.kpis["complexity"].calculation_values["function_count"], 2)
        # Hotspot should store calculation inputs
        self.assertEqual(main_file.kpis["hotspot"].calculation_values, {"complexity": 9, "churn": 7})

    def test_zero_functions_results_in_zero_complexity_and_hotspot(self):
        """If no functions are found, complexity should be 0 and hotspot 0."""
        # Mock churn data
        mock_churn_data = {
            str(self.main_py_path): 5,
            str(self.utils_py_path): 1,
            str(self.app_java_path): 2,
        }

        with patch.object(ComplexityAnalyzer, 'analyze_functions', return_value=[]), \
                patch.object(ChurnKPI, 'calculate',
                             side_effect=lambda file_path, **kwargs: ChurnKPI(value=mock_churn_data.get(file_path, 0))), \
                patch.object(HotspotKPI, 'calculate',
                             side_effect=lambda complexity, churn, **kwargs: HotspotKPI(value=complexity * churn)):
            summary = self.analyzer.analyze(self.scanner_files)

        # With the new logic, all files from the same git repo are grouped together
        self.assertEqual(len(summary), 1)  # One combined repo found
        repo_keys = list(summary.keys())
        combined_repo_info = summary[repo_keys[0]]

        # Navigate to the main.py file: RepoInfo -> test_analyzer_temp_dir -> repo1 -> src -> main.py
        temp_dir_name = self.test_dir.name  # "test_analyzer_temp_dir"
        temp_dir = combined_repo_info.scan_dirs[temp_dir_name]
        repo1_dir = temp_dir.scan_dirs["repo1"]
        src_dir = repo1_dir.scan_dirs["src"]
        main_file = src_dir.files["main.py"]
        self.assertEqual(main_file.kpis["complexity"].value, 0)
        self.assertEqual(main_file.kpis["complexity"].calculation_values["function_count"], 0)
        self.assertEqual(main_file.kpis["hotspot"].value, 0)
        self.assertEqual(len(main_file.functions), 0)

    def test_analyze_empty_list(self):
        """Test that analyzing an empty list of files returns an empty dictionary."""
        summary = self.analyzer.analyze([])
        self.assertEqual(summary, {})


if __name__ == '__main__':
    unittest.main()
