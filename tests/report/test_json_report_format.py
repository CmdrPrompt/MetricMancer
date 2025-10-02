
# Rewritten as unittest
import json
import unittest
from src.report.json.json_report_format import JSONReportFormat
from src.kpis.model import RepoInfo, ScanDir, File
from src.kpis.base_kpi import BaseKPI

class DummyKPI(BaseKPI):
    def __init__(self, name, value):
        super().__init__(name=name, value=value)
        self._value = value
    def calculate(self, *args, **kwargs):
        return self._value

class TestJSONReportFormat(unittest.TestCase):
    def test_json_report_includes_ownership_and_shared_ownership(self):
        # Arrange: Skapa en dummy RepoInfo med File-objekt och KPI:er
        file1 = File(
            name="main.py",
            file_path="main.py",
            kpis={
                "complexity": DummyKPI("complexity", 10),
                "churn": DummyKPI("churn", 5),
                "hotspot": DummyKPI("hotspot", 50),
                "Code Ownership": DummyKPI("Code Ownership", {"Alice": 80.0, "Bob": 20.0}),
                "Shared Ownership": DummyKPI("Shared Ownership", {"num_significant_authors": 1, "significant_authors": ["Alice"]}),
            },
            functions=[]
        )
        file2 = File(
            name="utils.py",
            file_path="utils.py",
            kpis={
                "complexity": DummyKPI("complexity", 7),
                "churn": DummyKPI("churn", 2),
                "hotspot": DummyKPI("hotspot", 14),
                "Code Ownership": DummyKPI("Code Ownership", {"Alice": 60.0, "Bob": 40.0}),
                "Shared Ownership": DummyKPI("Shared Ownership", {"num_significant_authors": 2, "significant_authors": ["Alice", "Bob"]}),
            },
            functions=[]
        )
        scan_dir = ScanDir(
            dir_name="root",
            scan_dir_path=".",
            files={"main.py": file1, "utils.py": file2},
            scan_dirs={},
            repo_root_path="/repo",
            repo_name="repo"
        )
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="repo",
            dir_name="repo",
            scan_dir_path=".",
            files=scan_dir.files,
            scan_dirs={}
        )

        report_format = JSONReportFormat()
        data = report_format.get_report_data(repo_info, level="file", hierarchical=False)

        # Act: Serialisera till JSON och ladda tillbaka
        json_str = json.dumps(data)
        loaded = json.loads(json_str)

        # Assert: Kontrollera att ownership och shared ownership finns med
        filenames = {item["filename"]: item for item in loaded}
        self.assertIn("main.py", filenames)
        self.assertIn("utils.py", filenames)
        main_kpis = filenames["main.py"]
        utils_kpis = filenames["utils.py"]
        self.assertEqual(main_kpis["code_ownership"], {"Alice": 80.0, "Bob": 20.0})
        self.assertEqual(main_kpis["shared_ownership"], {"num_significant_authors": 1, "significant_authors": ["Alice"]})
        self.assertEqual(utils_kpis["code_ownership"], {"Alice": 60.0, "Bob": 40.0})
        self.assertEqual(utils_kpis["shared_ownership"], {"num_significant_authors": 2, "significant_authors": ["Alice", "Bob"]})
