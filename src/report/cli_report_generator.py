from .report_interface import ReportInterface
from collections import Counter
import os



class CLIReportGenerator(ReportInterface):
    def __init__(self, repo_infos, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None):
        """
        Initialize the CLIReportGenerator.
        Args:
            repo_infos: A list of repository information (GitRepoInfo).
            threshold_low: The lower threshold for reporting.
            threshold_high: The upper threshold for reporting.
            problem_file_threshold: Optional threshold for problematic files.
        """
        self.repo_infos = repo_infos
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold

    def generate(self, output_file=None):
        """
        Generate and print the report for the repositories.
        Args:
            output_file: Optional file to write the report to.
        """
        from src.utilities.debug import debug_print
        from .cli_report_format import CLIReportFormat
        format_strategy = CLIReportFormat()
        for repo_info in self.repo_infos:
            format_strategy.print_report(repo_info, debug_print)
    # All rapportlogik hanteras nu av strategi-klassen

    # Tree building and printing now handled by TreePrinter
