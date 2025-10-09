
import unittest
from unittest.mock import MagicMock, patch
from src.report.report_generator import ReportGenerator
from src.kpis.model import RepoInfo


class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        # Minimal RepoInfo mock
        self.repo_info = RepoInfo(
            dir_name="repo",
            scan_dir_path="./",
            repo_root_path="./",
            repo_name="repo"
        )

    @patch("src.report.report_generator.HTMLReportFormat")
    def test_generate_calls_html_report_format(self, MockHTMLReportFormat):
        mock_format = MockHTMLReportFormat.return_value
        mock_format.print_report = MagicMock()
        generator = ReportGenerator(self.repo_info)
        generator.generate(output_file="dummy.html", report_links=["link1"])
        mock_format.print_report.assert_called_once()
        args, kwargs = mock_format.print_report.call_args
        # repo_info är första positionella argumentet
        self.assertEqual(args[0], self.repo_info)
        self.assertEqual(kwargs["output_file"], "dummy.html")
        self.assertEqual(kwargs["report_links"], ["link1"])

    def test_init_sets_attributes(self):
        generator = ReportGenerator(self.repo_info, threshold_low=5, threshold_high=15, problem_file_threshold=3, template_dir="foo", template_file="bar.html")
        self.assertEqual(generator.repo_info, self.repo_info)
        self.assertEqual(generator.threshold_low, 5)
        self.assertEqual(generator.threshold_high, 15)
        self.assertEqual(generator.problem_file_threshold, 3)
        self.assertEqual(generator.template_dir, "foo")
        self.assertEqual(generator.template_file, "bar.html")


if __name__ == "__main__":
    unittest.main()
