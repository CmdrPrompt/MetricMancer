import os
from collections import Counter

from src.report.cli.cli_csv_report_format import CLICSVReportFormat
from src.report.cli.cli_report_format import CLIReportFormat
from src.report.cli.cli_summary_format import CLISummaryFormat
from src.report.cli.cli_quick_wins_format import CLIQuickWinsFormat
from src.report.report_interface import ReportInterface
from src.utilities.debug import debug_print


class CLIReportGenerator(ReportInterface):
    def __init__(self, repo_info, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None):
        self.repo_infos = [repo_info]  # Internally, we still work with a list
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold

    def generate(self, output_file=None, level="file", output_format="human", save_cli_to_file=False, **kwargs):
        strategies = {
            "summary": CLISummaryFormat,
            "quick-wins": CLIQuickWinsFormat,
            "human": CLIReportFormat,
            "human-tree": CLIReportFormat,  # Alias for backward compatibility
            "tree": CLIReportFormat,  # Alias for backward compatibility
            "machine": CLICSVReportFormat
        }

        strategy_class = strategies.get(output_format)
        if not strategy_class:
            raise ValueError(f"Unsupported CLI output format: {output_format}")

        format_strategy = strategy_class()

        # If save_cli_to_file is True (multi-format mode), capture output to file
        if save_cli_to_file and output_file and output_format != "machine" and (
                output_file.endswith('.md') or output_file.endswith('.html')):
            import sys
            from io import StringIO

            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            try:
                for repo_info in self.repo_infos:
                    format_strategy.print_report(repo_info, debug_print, level=level, output_file=output_file, **kwargs)

                # Write captured output to file
                content = captured_output.getvalue()
                os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)

                # Wrap in markdown code fence if .md extension for proper monospace rendering
                if output_file.endswith('.md'):
                    content = f"```\n{content}\n```\n"

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[OK] Report generated: {output_file}", file=old_stdout)
                # Also print the content to stdout for CLI visibility
                print(content, end='', file=old_stdout)
            finally:
                sys.stdout = old_stdout
        else:
            # Normal stdout printing (backward compatible)
            for repo_info in self.repo_infos:
                format_strategy.print_report(repo_info, debug_print, level=level, output_file=output_file, **kwargs)
