import os
from collections import Counter

from src.report.cli.cli_csv_report_format import CLICSVReportFormat
from src.report.cli.cli_report_format import CLIReportFormat
from src.report.report_interface import ReportInterface
from src.utilities.debug import debug_print


class CLIReportGenerator(ReportInterface):
    def __init__(self, repo_info, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None):
        self.repo_infos = [repo_info]  # Internally, we still work with a list
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold

    def generate(self, output_file=None, level="file", output_format="human", **kwargs):
        strategies = {
            "human": CLIReportFormat,
            "machine": CLICSVReportFormat
        }

        strategy_class = strategies.get(output_format)
        if not strategy_class:
            raise ValueError(f"Unsupported CLI output format: {output_format}")

        format_strategy = strategy_class()

        for repo_info in self.repo_infos:
            format_strategy.print_report(repo_info, debug_print, level=level)
