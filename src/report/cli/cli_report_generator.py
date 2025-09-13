from src.report.report_interface import ReportInterface
from collections import Counter
import os


class CLIReportGenerator(ReportInterface):
    def __init__(self, repo_infos, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None):
        # repo_infos ska vara en lista av GitRepoInfo
        self.repo_infos = repo_infos
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold

    def generate(self, output_file=None):
        from src.utilities.debug import debug_print
        import sys
        level = "file"
        output_format = "human"
        for i, arg in enumerate(sys.argv):
            if arg == "--level" and i + 1 < len(sys.argv):
                level = sys.argv[i + 1]
            if arg == "--output-format" and i + 1 < len(sys.argv):
                output_format = sys.argv[i + 1]
        if output_format == "machine":
            from src.report.cli.cli_csv_report_format import CLICSVReportFormat
            format_strategy = CLICSVReportFormat()
        else:
            from src.report.cli.cli_report_format import CLIReportFormat
            format_strategy = CLIReportFormat()
        if not self.repo_infos or all(not getattr(r, 'results', None) for r in self.repo_infos):
            print("[INFO] Inga kodfiler hittades att analysera i angiven katalog.")
            return
        for repo_info in self.repo_infos:
            format_strategy.print_report(repo_info, debug_print, level=level)
    # All rapportlogik hanteras nu av strategi-klassen

    # Tree building and printing now handled by TreePrinter
