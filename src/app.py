from src.config import Config
from src.scanner import Scanner
from src.analyzer import Analyzer
from src.report.report_generator import ReportGenerator

class ComplexityScannerApp:
    def __init__(self, directories, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, output_file='complexity_report.html', report_generator_cls=None):
        self.config = Config()
        self.scanner = Scanner(self.config)
        self.analyzer = Analyzer(self.config, threshold_low, threshold_high)
        self.directories = directories
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold
        self.output_file = output_file
        # Allow swapping report generator
        from src.report.report_generator import ReportGenerator
        self.report_generator_cls = report_generator_cls or ReportGenerator

    def run(self):
        from src.debug import debug_print
        debug_print(f"[DEBUG] scan dirs: {self.directories}")
        files = self.scanner.scan(self.directories)
        debug_print(f"[DEBUG] scanned files: {len(files)}")
        summary = self.analyzer.analyze(files)
        debug_print(f"[DEBUG] summary keys: {list(summary.keys())}")
        repo_infos = []
        for repo_root, repo_info in summary.items():
            debug_print(f"[DEBUG] repo_info: root={repo_info.repo_root}, name={repo_info.repo_name}, files={len(repo_info.files)}, results-languages={list(repo_info.results.keys())}")
            repo_infos.append(repo_info)
        import os
        # Generate one HTML report per repo_info
        for idx, repo_info in enumerate(repo_infos):
            output_file = self.output_file or "complexity_report.html"
            # If multiple repos, append index to filename
            if len(repo_infos) > 1:
                base, ext = os.path.splitext(output_file)
                output_file = f"{base}_{idx+1}{ext}"
            # Use correct input type for each generator
            if self.report_generator_cls.__name__ == "CLIReportGenerator":
                report = self.report_generator_cls(
                    [repo_info],
                    self.threshold_low,
                    self.threshold_high,
                    self.problem_file_threshold
                )
            else:
                report = self.report_generator_cls(
                    repo_info,
                    self.threshold_low,
                    self.threshold_high,
                    self.problem_file_threshold
                )
            report.generate(output_file)
