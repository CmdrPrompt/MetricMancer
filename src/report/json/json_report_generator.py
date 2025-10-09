
import json
from src.report.report_interface import ReportInterface

class JSONReportGenerator(ReportInterface):
    def __init__(self, repo_info, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None):
        self.repo_infos = [repo_info] # Internally, we still work with a list
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold

    def generate(self, output_file=None, level="file", hierarchical=False, **kwargs):
        from src.utilities.debug import debug_print
        from src.report.json.json_report_format import JSONReportFormat
        from src.kpis.model import RepoInfo

        format_strategy = JSONReportFormat()
        all_repos = []
        for repo_info in self.repo_infos:
            repo_json = format_strategy.get_report_data(repo_info, level=level, hierarchical=hierarchical)
            all_repos.append(repo_json)

        # Om bara ett repo, skriv inte ut det i en lista
        output_data = all_repos[0] if len(all_repos) == 1 else all_repos
        json_str = json.dumps(output_data, indent=2, ensure_ascii=False)

        if not output_file:
            output_file = 'complexity_report.json'
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"[OK] JSON report written to: {output_file}")
        else:
            print(json_str)
