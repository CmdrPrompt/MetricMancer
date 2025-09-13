import os
from collections import defaultdict
from src.languages.config import LANGUAGES
from src.report.git_repo_info import GitRepoInfo
from src.kpis.churn.code_churn import FileMetrics
from src.kpis.complexity.fileanalyzer import FileAnalyzer
from src.kpis.complexity.metrics import grade
from src.kpis.complexity.metrics_collector import MetricsCollector

class Analyzer:
    def __init__(self, config, threshold_low=10.0, threshold_high=20.0):
        self.config = config.languages
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high

    def _group_files_by_repo(self, files):
        """Groups files by their repository root directory."""
        files_by_root = defaultdict(list)
        scan_dirs_by_root = defaultdict(set)
        for file in files:
            repo_root = file.get('root', '')
            files_by_root[repo_root].append(file)
            scan_dirs_by_root[repo_root].add(repo_root)
        return files_by_root, scan_dirs_by_root

    def _analyze_repo(self, repo_root, files_in_repo, scan_dirs):
        """Analyzes a single repository's files for complexity, churn, and other metrics."""
        from src.utilities.debug import debug_print

        filepaths = [file['path'] for file in files_in_repo]
        debug_print(f"[DEBUG] Analyzing repo: {repo_root} with {len(filepaths)} files.")

        # 1. Collect metrics (complexity and churn)
        metrics_collector = MetricsCollector(scanner=FileAnalyzer, repo_path=repo_root, scan_dirs=scan_dirs)
        metrics_list = metrics_collector.collect(filepaths)

        # 2. Prepare data structures for GitRepoInfo
        churn_data = {os.path.abspath(m.filename): m.churn for m in metrics_list}
        complexity_data = {os.path.abspath(m.filename): m.complexity for m in metrics_list}
        hotspot_data = {os.path.abspath(m.filename): m.complexity * m.churn for m in metrics_list}

        # 3. Perform detailed analysis on each file
        results = defaultdict(lambda: defaultdict(list))
        for file, metrics in zip(files_in_repo, metrics_list):
            ext = file.get('ext')
            if ext not in self.config:
                debug_print(f"_analyze_repo: Skipping file with unknown extension: {file['path']}")
                continue

            config = self.config[ext]
            analyzer = FileAnalyzer(file['path'], file['root'], config)
            if not analyzer.load():
                continue

            result = analyzer.analyze()
            result['grade'] = grade(result['complexity'], self.threshold_low, self.threshold_high)
            result['churn'] = metrics.churn
            result['abs_path'] = metrics.abs_path
            result['metrics'] = metrics
            result['repo_root'] = file.get('repo_root', repo_root)

            lang = result.get('language')
            root = result.get('root')
            if lang and root:
                results[lang][root].append(result)

        # 4. Create GitRepoInfo object for the repository
        repo_info = GitRepoInfo(
            repo_root=repo_root,
            repo_name=os.path.basename(repo_root),
            scan_dirs=scan_dirs,
            files=filepaths,
            churn_data=churn_data,
            complexity_data=complexity_data,
            hotspot_data=hotspot_data,
            commits=[],  # Can be populated if needed
            results=dict(results)
        )
        return repo_info

    def analyze(self, files):
        """Analyzes a list of files, groups them by repository, and returns a summary."""
        from src.utilities.debug import debug_print

        if not files:
            return {}

        files_by_root, scan_dirs_by_root = self._group_files_by_repo(files)
        debug_print(f"[DEBUG] Analyzer: Found {len(files_by_root)} repositories to analyze.")

        summary = {}
        for repo_root in sorted(files_by_root.keys()):
            summary[repo_root] = self._analyze_repo(
                repo_root, files_by_root[repo_root], list(scan_dirs_by_root[repo_root])
            )

        return summary
