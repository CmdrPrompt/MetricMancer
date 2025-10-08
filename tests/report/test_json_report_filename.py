
import unittest
import os
from src.kpis.model import RepoInfo
from src.report.json.json_report_generator import JSONReportGenerator

class TestJSONReportFilename(unittest.TestCase):
    def setUp(self):
        self.repo_info = RepoInfo(dir_name="repo", scan_dir_path="src", repo_root_path="/repo", repo_name="repo", files={}, scan_dirs={})
        self.output_file = "test_report.json"
        # Ta bort filen om den finns
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_json_report_is_saved_as_json_file_by_default(self):
        generator = JSONReportGenerator(self.repo_info)
        generator.generate()
        # Default ska vara .json-fil
        self.assertTrue(os.path.exists("complexity_report.json"), "JSON report should be saved as .json file by default.")

if __name__ == "__main__":
    unittest.main()
