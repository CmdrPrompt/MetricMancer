
import unittest
import os
from src.kpis.model import RepoInfo
from src.report.report_generator import ReportGenerator


class TestHTMLReportFilename(unittest.TestCase):
    def setUp(self):
        self.repo_info = RepoInfo(
            dir_name="repo",
            scan_dir_path="src",
            repo_root_path="/repo",
            repo_name="repo",
            files={},
            scan_dirs={})
        self.output_file = "test_report.html"
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        if os.path.exists("complexity_report.html"):
            os.remove("complexity_report.html")

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        if os.path.exists("complexity_report.html"):
            os.remove("complexity_report.html")

    def test_html_report_is_saved_as_html_file_by_default(self):
        generator = ReportGenerator(self.repo_info)
        generator.generate()
        self.assertTrue(os.path.exists("complexity_report.html"),
                        "HTML report should be saved as .html file by default.")


if __name__ == "__main__":
    unittest.main()
