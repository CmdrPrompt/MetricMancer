
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

    def test_init_default_values(self):
        """Test that default values are set correctly in __init__."""
        generator = ReportGenerator(self.repo_info)
        self.assertEqual(generator.threshold_low, 10.0)
        self.assertEqual(generator.threshold_high, 20.0)
        self.assertIsNone(generator.problem_file_threshold)
        self.assertEqual(generator.template_dir, 'src/report/templates')
        self.assertEqual(generator.template_file, 'report.html')

    @patch("src.report.report_generator.HTMLReportFormat")
    def test_generate_with_default_output_file(self, MockHTMLReportFormat):
        """Test generate method with default output file."""
        mock_format = MockHTMLReportFormat.return_value
        mock_format.print_report = MagicMock()
        generator = ReportGenerator(self.repo_info)
        generator.generate()
        mock_format.print_report.assert_called_once()
        args, kwargs = mock_format.print_report.call_args
        self.assertEqual(args[0], self.repo_info)
        self.assertEqual(kwargs["output_file"], "complexity_report.html")

    @patch("src.report.report_generator.HTMLReportFormat")
    def test_generate_passes_thresholds_correctly(self, MockHTMLReportFormat):
        """Test that threshold values are passed correctly to HTMLReportFormat."""
        mock_format = MockHTMLReportFormat.return_value
        mock_format.print_report = MagicMock()
        generator = ReportGenerator(
            self.repo_info,
            threshold_low=5.0,
            threshold_high=25.0,
            problem_file_threshold=30.0
        )
        generator.generate()
        mock_format.print_report.assert_called_once()
        args, kwargs = mock_format.print_report.call_args
        self.assertEqual(kwargs["threshold_low"], 5.0)
        self.assertEqual(kwargs["threshold_high"], 25.0)
        self.assertEqual(kwargs["problem_file_threshold"], 30.0)

    @patch("src.report.report_generator.HTMLReportFormat")
    def test_generate_passes_kwargs_through(self, MockHTMLReportFormat):
        """Test that additional kwargs are passed through to print_report."""
        mock_format = MockHTMLReportFormat.return_value
        mock_format.print_report = MagicMock()
        generator = ReportGenerator(self.repo_info)
        generator.generate(
            include_review_tab=True,
            review_branch_only=False,
            custom_param="test_value"
        )
        mock_format.print_report.assert_called_once()
        args, kwargs = mock_format.print_report.call_args
        self.assertTrue(kwargs["include_review_tab"])
        self.assertFalse(kwargs["review_branch_only"])
        self.assertEqual(kwargs["custom_param"], "test_value")

    @patch("src.report.report_generator.HTMLReportFormat")
    def test_generate_with_empty_report_links(self, MockHTMLReportFormat):
        """Test generate method with empty report links."""
        mock_format = MockHTMLReportFormat.return_value
        mock_format.print_report = MagicMock()
        generator = ReportGenerator(self.repo_info)
        generator.generate(report_links=[])
        mock_format.print_report.assert_called_once()
        args, kwargs = mock_format.print_report.call_args
        self.assertEqual(kwargs["report_links"], [])

    @patch("src.report.report_generator.HTMLReportFormat")
    def test_generate_with_none_report_links(self, MockHTMLReportFormat):
        """Test generate method with None report links."""
        mock_format = MockHTMLReportFormat.return_value
        mock_format.print_report = MagicMock()
        generator = ReportGenerator(self.repo_info)
        generator.generate(report_links=None)
        mock_format.print_report.assert_called_once()
        args, kwargs = mock_format.print_report.call_args
        self.assertIsNone(kwargs["report_links"])

    def test_init_with_custom_template_dir_and_file(self):
        """Test initialization with custom template directory and file."""
        generator = ReportGenerator(
            self.repo_info,
            template_dir="/custom/templates",
            template_file="custom_report.html"
        )
        self.assertEqual(generator.template_dir, "/custom/templates")
        self.assertEqual(generator.template_file, "custom_report.html")


if __name__ == "__main__":
    unittest.main()
