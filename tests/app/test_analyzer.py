import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.app.analyzer import Analyzer
from src.kpis.codechurn import ChurnKPI
from src.kpis.complexity import ComplexityAnalyzer, ComplexityKPI
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
             patch.object(ChurnKPI, 'calculate', side_effect=lambda file_path, **kwargs: ChurnKPI(value=mock_churn_data.get(file_path, 0))) as mock_churn_calc, \
             patch.object(HotspotKPI, 'calculate', side_effect=lambda complexity, churn, **kwargs: HotspotKPI(value=complexity * churn)) as mock_hotspot_calc:

            # --- Run the analysis ---
            summary = self.analyzer.analyze(self.scanner_files)

            # --- Assertions ---
            self.assertEqual(len(summary), 2)  # Two repos found
            self.assertIn(str(self.repo1_path), summary)
            self.assertIn(str(self.repo2_path), summary)

            # --- Verify Repo 1 ---
            repo1_info = summary[str(self.repo1_path)]
            self.assertIsInstance(repo1_info, RepoInfo)
            self.assertEqual(repo1_info.repo_name, "repo1")

            # Check directory structure: repo1 -> src
            self.assertIn("src", repo1_info.scan_dirs)
            src_dir = repo1_info.scan_dirs["src"]
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

            # --- Verify Repo 2 ---
            repo2_info = summary[str(self.repo2_path)]
            self.assertIsInstance(repo2_info, RepoInfo)
            self.assertEqual(repo2_info.repo_name, "repo2")

            # Repo 2 has a file in the root, so it should be in the RepoInfo's `files` dict.
            self.assertEqual(len(repo2_info.scan_dirs), 0)
            self.assertIn("app.java", repo2_info.files)
            app_java_file = repo2_info.files["app.java"]
            self.assertIsInstance(app_java_file, File)
            self.assertEqual(app_java_file.kpis["complexity"].value, 15)
            self.assertEqual(app_java_file.kpis["churn"].value, 20)
            self.assertEqual(app_java_file.kpis["hotspot"].value, 300)  # 15 * 20

    @patch('src.app.analyzer.debug_print')
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
             patch.object(ChurnKPI, 'calculate', side_effect=lambda file_path, **kwargs: ChurnKPI(value=mock_churn_data.get(file_path, 0))), \
             patch.object(HotspotKPI, 'calculate', side_effect=lambda complexity, churn, **kwargs: HotspotKPI(value=complexity * churn)):
            summary = self.analyzer.analyze(files)

            # Repo1 exists
            repo1_info = summary[str(self.repo1_path)]
            # README.md is unsupported and must not be present under repo root files
            self.assertNotIn("README.md", repo1_info.files)
            # Logga alla debug_print-anrop för felsökning
            print("DEBUG_PRINT CALLS:")
            for call in mock_debug_print.call_args_list:
                print(call)
            # Robust substring-match mot debug_print-anropet
            expected_substr = f"_analyze_repo: Skipping file with unknown extension: {str(Path(readme_path).resolve())}"
            self.assertTrue(any(expected_substr in call.args[0] for call in mock_debug_print.call_args_list),
                            f"Expected debug_print call containing: {expected_substr}\nActual calls: {[call.args[0] for call in mock_debug_print.call_args_list]}")

    @patch('src.app.file_processor.debug_print')  # Phase 5: debug_print now in FileProcessor
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
             patch.object(ChurnKPI, 'calculate', side_effect=lambda file_path, **kwargs: ChurnKPI(value=mock_churn_data.get(file_path, 0))), \
             patch.object(HotspotKPI, 'calculate', side_effect=lambda complexity, churn, **kwargs: HotspotKPI(value=complexity * churn)):
            summary = self.analyzer.analyze(files)

        repo1_info = summary[str(self.repo1_path)]
        # The file should not exist under the directory where Python files were placed
        container = repo1_info.scan_dirs.get("src", repo1_info)
        self.assertNotIn("blocked_missing.py", container.files)
        # A warning should have been printed
        self.assertTrue(any(
            "Unable to read" in call.args[0] and str(blocked_missing_path) in call.args[0]
            for call in mock_debug_print.call_args_list
        ))

    def test_builds_nested_scandir_hierarchy(self):
        """Analyzer should create nested ScanDir objects for deep paths."""
        nested_path = self.repo1_path / "src" / "pkg" / "module" / "utils" / "helper.py"
        (nested_path.parent).mkdir(parents=True, exist_ok=True)
        nested_path.write_text("def helper(): pass")

        files = list(self.scanner_files) + [
            {'path': str(nested_path), 'root': str(self.repo1_path), 'ext': '.py'},
        ]

        # Mock churn data  
        mock_churn_data = {
            str(self.main_py_path): 1,
            str(self.utils_py_path): 2,
            str(nested_path): 3,
        }
        mock_functions_data = [
            {'name': 'a', 'complexity': 6},
            {'name': 'b', 'complexity': 3},
        ]
        with patch.object(ComplexityAnalyzer, 'analyze_functions', return_value=mock_functions_data):
            summary = self.analyzer.analyze(files)

        repo1_info = summary[str(self.repo1_path)]
        src_dir = repo1_info.scan_dirs["src"]
        self.assertIn("pkg", src_dir.scan_dirs)
        pkg_dir = src_dir.scan_dirs["pkg"]
        self.assertIn("module", pkg_dir.scan_dirs)
        module_dir = pkg_dir.scan_dirs["module"]
        self.assertIn("utils", module_dir.scan_dirs)
        utils_dir = module_dir.scan_dirs["utils"]
        self.assertIn("helper.py", utils_dir.files)
        helper_file = utils_dir.files["helper.py"]
        # file_path should be relative to repo root
        self.assertEqual(helper_file.file_path.replace("\\", "/"), "src/pkg/module/utils/helper.py")

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

        repo1_info = summary[str(self.repo1_path)]
        src_dir = repo1_info.scan_dirs["src"]
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
             patch.object(ChurnKPI, 'calculate', side_effect=lambda file_path, **kwargs: ChurnKPI(value=mock_churn_data.get(file_path, 0))), \
             patch.object(HotspotKPI, 'calculate', side_effect=lambda complexity, churn, **kwargs: HotspotKPI(value=complexity * churn)):
            summary = self.analyzer.analyze(self.scanner_files)

        repo1_info = summary[str(self.repo1_path)]
        src_dir = repo1_info.scan_dirs["src"]
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
