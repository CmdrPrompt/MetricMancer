from src.languages.config import Config
from src.app.scanner import Scanner
from src.app.analyzer import Analyzer
from src.report.report_generator import ReportGenerator

class MetricMancerApp:
    def __init__(self, directories, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, output_file='complexity_report.html', report_generator_cls=None, level="file", hierarchical=False, output_format="human"):
        self.config = Config()
        self.scanner = Scanner(self.config.languages)
        self.analyzer = Analyzer(self.config.languages, threshold_low=threshold_low, threshold_high=threshold_high)
        self.directories = directories
        # Report settings
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold
        self.output_file = output_file
        self.level = level
        self.hierarchical = hierarchical
        self.output_format = output_format

        # Allow swapping report generator
        from src.report.report_generator import ReportGenerator
        self.report_generator_cls = report_generator_cls or ReportGenerator

    def run(self):
        from src.utilities.debug import debug_print
        debug_print(f"[DEBUG] scan dirs: {self.directories}")
        files = self.scanner.scan(self.directories)
        debug_print(f"[DEBUG] scanned files: {len(files)}")
        summary = self.analyzer.analyze(files)
        debug_print(f"[DEBUG] summary keys: {list(summary.keys())}")
        repo_infos = []
        for repo_root, repo_info in summary.items():
            debug_print(f"[DEBUG] repo_info: root={repo_info.repo_root_path}, name={repo_info.repo_name}")
            repo_infos.append(repo_info)
        import os
        # Prepare report_links for cross-linking if multiple repos
        report_links = []
        if len(repo_infos) > 1:
            for idx, repo_info in enumerate(repo_infos):
                output_file = self.output_file or "complexity_report.html"
                base, ext = os.path.splitext(output_file)
                filename = f"{base}_{idx+1}{ext}"
                report_links.append({
                    'href': filename,
                    'name': getattr(repo_info, 'repo_name', f'Repo {idx+1}'),
                    'selected': False
                })
        # Generate one HTML report per repo_info
        for idx, repo_info in enumerate(repo_infos):
            output_file = self.output_file or "complexity_report.html"
            # If multiple repos, append index to filename
            if len(repo_infos) > 1:
                base, ext = os.path.splitext(output_file)
                output_file = f"{base}_{idx+1}{ext}"
                # Mark the current as selected
                for link in report_links:
                    link['selected'] = (link['href'] == output_file)
                links_for_this = [l for l in report_links if l['href'] != output_file]
            else:
                links_for_this = report_links

            # All generators now accept a single repo_info object, making the call uniform.
            report = self.report_generator_cls(
                repo_info, self.threshold_low, self.threshold_high, self.problem_file_threshold
            )
            report.generate(
                output_file=output_file,
                level=self.level,
                hierarchical=self.hierarchical,
                output_format=self.output_format,
                report_links=links_for_this
            )
