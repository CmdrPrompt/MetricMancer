
import json
from src.report.report_interface import ReportInterface

class JSONReportGenerator(ReportInterface):
    def __init__(self, repo_infos, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None):
        self.repo_infos = repo_infos
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold

    def generate(self, output_file=None):
        from src.utilities.debug import debug_print
        from src.report.json.json_report_format import JSONReportFormat
        import sys
        # Hämta level från CLI-argument om det finns
        level = "file"
        for i, arg in enumerate(sys.argv):
            if arg == "--level" and i + 1 < len(sys.argv):
                level = sys.argv[i + 1]
        format_strategy = JSONReportFormat()
        all_repos = []
        for repo_info in self.repo_infos:
            repo_json = format_strategy.get_repo_json(repo_info, debug_print, level=level)
            all_repos.append(repo_json)
        json_str = json.dumps(all_repos, indent=2, ensure_ascii=False)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"\u2705 JSON report written to: {output_file}")
        else:
            print(json_str)
