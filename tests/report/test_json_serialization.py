
import unittest
from src.kpis.model import RepoInfo, ScanDir, File
from src.kpis.complexity.kpi import ComplexityKPI
from src.report.json.json_report_format import JSONReportFormat
import json


class TestJSONSerialization(unittest.TestCase):
    def test_json_serialization_fails_on_kpi_object(self):
        # Skapa ett RepoInfo med en File som har en KPI-klass som värde
        file = File(name="test.py", file_path="test.py", kpis={"complexity": ComplexityKPI(value=42)}, functions=[])
        scan_dir = ScanDir(dir_name="src", scan_dir_path="src", repo_root_path="/repo", repo_name="repo", files={"test.py": file}, scan_dirs={})
        repo_info = RepoInfo(dir_name="repo", scan_dir_path="src", repo_root_path="/repo", repo_name="repo", files={}, scan_dirs={"src": scan_dir})
        format_strategy = JSONReportFormat()
        # _to_dict är trasig, så KPI-objekt finns kvar i dicten
        data = format_strategy._to_dict(repo_info)
        # Försök serialisera till JSON, ska ge TypeError
        try:
            json.dumps(data)
            self.fail("JSON serialization succeeded, but it should fail with KPI object present.")
        except TypeError:
            pass  # Expected exception


if __name__ == "__main__":
    unittest.main()
