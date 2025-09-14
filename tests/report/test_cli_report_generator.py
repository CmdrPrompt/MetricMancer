import unittest
from unittest.mock import MagicMock, patch
from src.report.cli.cli_report_generator import CLIReportGenerator
from src.kpis.model import RepoInfo

class TestCLIReportGenerator(unittest.TestCase):
    def setUp(self):
        self.repo_info = RepoInfo(
            dir_name="repo",
            scan_dir_path="./",
            repo_root_path="./",
            repo_name="repo"
        )

    @patch("src.report.cli.cli_report_generator.CLIReportFormat")
    def test_generate_human_calls_cli_report_format(self, MockCLIReportFormat):
        mock_format = MockCLIReportFormat.return_value
        mock_format.print_report = MagicMock()
        generator = CLIReportGenerator(self.repo_info)
        generator.generate(output_format="human", level="file")
        mock_format.print_report.assert_called_once()
        args, kwargs = mock_format.print_report.call_args
        self.assertEqual(args[0], self.repo_info)
        self.assertEqual(kwargs["level"], "file")

    @patch("src.report.cli.cli_report_generator.CLICSVReportFormat")
    def test_generate_machine_calls_cli_csv_report_format(self, MockCLICSVReportFormat):
        mock_format = MockCLICSVReportFormat.return_value
        mock_format.print_report = MagicMock()
        generator = CLIReportGenerator(self.repo_info)
        generator.generate(output_format="machine", level="file")
        mock_format.print_report.assert_called_once()
        args, kwargs = mock_format.print_report.call_args
        self.assertEqual(args[0], self.repo_info)
        self.assertEqual(kwargs["level"], "file")

    def test_generate_unsupported_format_raises(self):
        generator = CLIReportGenerator(self.repo_info)
        with self.assertRaises(ValueError):
            generator.generate(output_format="unknown")

    def test_init_sets_attributes(self):
        generator = CLIReportGenerator(self.repo_info, threshold_low=5, threshold_high=15, problem_file_threshold=3)
        self.assertEqual(generator.repo_infos, [self.repo_info])
        self.assertEqual(generator.threshold_low, 5)
        self.assertEqual(generator.threshold_high, 15)
        self.assertEqual(generator.problem_file_threshold, 3)

if __name__ == "__main__":
    unittest.main()
