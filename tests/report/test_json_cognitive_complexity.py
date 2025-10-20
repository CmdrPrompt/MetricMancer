"""
TDD tests for cognitive complexity in JSON report format.
Following RED-GREEN-REFACTOR methodology.

Phase 4.4: JSON Report - Cognitive Complexity Integration
"""

import json
import unittest
from src.report.json.json_report_format import JSONReportFormat
from src.kpis.model import RepoInfo, ScanDir, File, Function
from src.kpis.base_kpi import BaseKPI


class DummyKPI(BaseKPI):
    """Test helper KPI class."""
    def __init__(self, name, value):
        super().__init__(name=name, value=value)
        self._value = value

    def calculate(self, *args, **kwargs):
        return self._value


class TestJSONReportCognitiveComplexity(unittest.TestCase):
    """RED phase tests for cognitive complexity in JSON reports."""

    def test_flat_file_level_includes_cognitive_complexity(self):
        """Should include cognitive_complexity in flat file-level JSON output."""
        # Arrange
        file1 = File(
            name="example.py",
            file_path="src/example.py",
            kpis={
                "complexity": DummyKPI("complexity", 10),
                "cognitive_complexity": DummyKPI("cognitive_complexity", 8),
                "churn": DummyKPI("churn", 5),
                "hotspot": DummyKPI("hotspot", 50),
                "Code Ownership": DummyKPI("Code Ownership", {"Alice": 100.0}),
                "Shared Ownership": DummyKPI("Shared Ownership", {"num_significant_authors": 1})
            },
            functions=[]
        )

        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test-repo",
            dir_name="test-repo",
            scan_dir_path=".",
            files={"example.py": file1},
            scan_dirs={}
        )

        # Act
        report_format = JSONReportFormat()
        data = report_format.get_report_data(repo_info, level="file", hierarchical=False)
        json_str = json.dumps(data)
        loaded = json.loads(json_str)

        # Assert
        file_items = [item for item in loaded if item.get("filename") == "src/example.py"]
        self.assertEqual(len(file_items), 1, "Should have exactly one file entry")

        file_data = file_items[0]
        self.assertIn("cognitive_complexity", file_data,
                     "File-level JSON should include cognitive_complexity field")
        self.assertEqual(file_data["cognitive_complexity"], 8,
                        "Cognitive complexity value should be 8")

    def test_flat_function_level_includes_cognitive_complexity(self):
        """Should include cognitive_complexity in flat function-level JSON output."""
        # Arrange
        func1 = Function(
            name="calculate",
            kpis={
                "complexity": DummyKPI("complexity", 5),
                "cognitive_complexity": DummyKPI("cognitive_complexity", 3),
                "Code Ownership": DummyKPI("Code Ownership", {"Alice": 100.0}),
                "Shared Ownership": DummyKPI("Shared Ownership", {"num_significant_authors": 1})
            }
        )

        file1 = File(
            name="example.py",
            file_path="src/example.py",
            kpis={
                "complexity": DummyKPI("complexity", 10),
                "cognitive_complexity": DummyKPI("cognitive_complexity", 8),
                "churn": DummyKPI("churn", 5),
                "Code Ownership": DummyKPI("Code Ownership", {"Alice": 100.0}),
            },
            functions=[func1]
        )

        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test-repo",
            dir_name="test-repo",
            scan_dir_path=".",
            files={"example.py": file1},
            scan_dirs={}
        )

        # Act
        report_format = JSONReportFormat()
        data = report_format.get_report_data(repo_info, level="function", hierarchical=False)
        json_str = json.dumps(data)
        loaded = json.loads(json_str)

        # Assert
        func_items = [item for item in loaded
                     if item.get("function_name") == "calculate"]
        self.assertEqual(len(func_items), 1, "Should have exactly one function entry")

        func_data = func_items[0]
        self.assertIn("cognitive_complexity", func_data,
                     "Function-level JSON should include cognitive_complexity field")
        self.assertEqual(func_data["cognitive_complexity"], 3,
                        "Cognitive complexity value should be 3")

    def test_package_level_includes_cognitive_complexity(self):
        """Should include cognitive_complexity in package/directory-level JSON output."""
        # Arrange
        file1 = File(
            name="example.py",
            file_path="src/example.py",
            kpis={
                "complexity": DummyKPI("complexity", 10),
                "cognitive_complexity": DummyKPI("cognitive_complexity", 8),
                "Code Ownership": DummyKPI("Code Ownership", {"Alice": 100.0}),
            },
            functions=[]
        )

        scan_dir = ScanDir(
            dir_name="src",
            scan_dir_path="src",
            files={"example.py": file1},
            scan_dirs={},
            repo_root_path="/repo",
            repo_name="test-repo",
            kpis={
                "complexity": DummyKPI("complexity", 10),
                "cognitive_complexity": DummyKPI("cognitive_complexity", 8),
                "churn": DummyKPI("churn", 5),
            }
        )

        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test-repo",
            dir_name="test-repo",
            scan_dir_path=".",
            files={},
            scan_dirs={"src": scan_dir}
        )

        # Act
        report_format = JSONReportFormat()
        data = report_format.get_report_data(repo_info, level="file", hierarchical=False)
        json_str = json.dumps(data)
        loaded = json.loads(json_str)

        # Assert
        package_items = [item for item in loaded
                        if item.get("package") == "src"]
        self.assertGreaterEqual(len(package_items), 1, "Should have at least one package entry")

        package_data = package_items[0]
        self.assertIn("cognitive_complexity", package_data,
                     "Package-level JSON should include cognitive_complexity field")
        self.assertEqual(package_data["cognitive_complexity"], 8,
                        "Package cognitive complexity should be 8")

    def test_hierarchical_mode_includes_cognitive_complexity(self):
        """Should include cognitive_complexity in hierarchical JSON output."""
        # Arrange
        file1 = File(
            name="example.py",
            file_path="src/example.py",
            kpis={
                "complexity": DummyKPI("complexity", 10),
                "cognitive_complexity": DummyKPI("cognitive_complexity", 8),
            },
            functions=[]
        )

        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test-repo",
            dir_name="test-repo",
            scan_dir_path=".",
            files={"example.py": file1},
            scan_dirs={}
        )

        # Act
        report_format = JSONReportFormat()
        data = report_format.get_report_data(repo_info, level="file", hierarchical=True)
        json_str = json.dumps(data)
        loaded = json.loads(json_str)

        # Assert
        self.assertIn("files", loaded, "Hierarchical output should have 'files' key")
        files = loaded["files"]
        self.assertIn("example.py", files, "Should contain example.py")

        file_data = files["example.py"]
        self.assertIn("kpis", file_data, "File should have kpis")
        self.assertIn("cognitive_complexity", file_data["kpis"],
                     "File KPIs should include cognitive_complexity")
        self.assertEqual(file_data["kpis"]["cognitive_complexity"], 8,
                        "Cognitive complexity value should be 8")

    def test_missing_cognitive_complexity_returns_none(self):
        """Should return None when cognitive_complexity KPI is missing."""
        # Arrange
        file1 = File(
            name="example.py",
            file_path="src/example.py",
            kpis={
                "complexity": DummyKPI("complexity", 10),
                # Note: No cognitive_complexity KPI
                "churn": DummyKPI("churn", 5),
            },
            functions=[]
        )

        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test-repo",
            dir_name="test-repo",
            scan_dir_path=".",
            files={"example.py": file1},
            scan_dirs={}
        )

        # Act
        report_format = JSONReportFormat()
        data = report_format.get_report_data(repo_info, level="file", hierarchical=False)
        json_str = json.dumps(data)
        loaded = json.loads(json_str)

        # Assert
        file_items = [item for item in loaded if item.get("filename") == "src/example.py"]
        self.assertEqual(len(file_items), 1)

        file_data = file_items[0]
        self.assertIn("cognitive_complexity", file_data,
                     "Should include cognitive_complexity field even when missing")
        self.assertIsNone(file_data["cognitive_complexity"],
                         "Missing cognitive_complexity should be None")


if __name__ == '__main__':
    unittest.main()
