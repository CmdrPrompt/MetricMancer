

from src.fileanalyzer import FileAnalyzer
from src.config import LANGUAGES
from src.metrics import grade
from src.code_churn import FileMetrics
from src.metrics_collector import MetricsCollector



class Analyzer:
    def __init__(self, config, threshold_low=10.0, threshold_high=20.0):
        self.config = config.languages
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        # Ingen global metrics_collector, hanteras per repo-root

    def analyze(self, files):
        from src.debug import debug_print
        # Gruppér filer per repo-root
        from src.code_churn import CodeChurnAnalyzer
        from collections import defaultdict
        files_by_root = defaultdict(list)
        scan_dirs_by_root = defaultdict(set)
        # ...fyll files_by_root och scan_dirs_by_root...
        repo_root_cache = {}
        for file in files:
            scan_dir = file['root']
            if scan_dir not in repo_root_cache:
                repo_root_cache[scan_dir] = CodeChurnAnalyzer.find_repo_root([scan_dir])
            repo_root = repo_root_cache[scan_dir]
            file['repo_root'] = repo_root
            files_by_root[repo_root].append(file)
            scan_dirs_by_root[repo_root].add(scan_dir)
        debug_print(f"[DEBUG] Analyzer.analyze: files_by_root:")
        for repo_root in files_by_root:
            debug_print(f"  repo_root: {repo_root}")
            for file in files_by_root[repo_root]:
                debug_print(f"    {file['path']}")
        repo_root_cache = {}
        debug_print(f"[DEBUG] Analyzer.analyze: filepaths:")
        for file in files:
            debug_print(f"  {file['path']}")
        # Only one loop to group files by repo_root
        from src.report.git_repo_info import GitRepoInfo
        summary = {}
        for repo_root in sorted(files_by_root.keys()):
            files_in_repo = files_by_root[repo_root]
            filepaths = [file['path'] for file in files_in_repo]
            scan_dirs = list(scan_dirs_by_root[repo_root])
            debug_print(f"[DEBUG] Analyzer.analyze: skickar till MetricsCollector: repo_root={repo_root}, scan_dirs={scan_dirs}")
            for fp in filepaths:
                debug_print(f"  filepath: {fp}")
            metrics_collector = MetricsCollector(scanner=FileAnalyzer, repo_path=repo_root, scan_dirs=scan_dirs)
            metrics_list = metrics_collector.collect(filepaths)
            results = {}
            churn_data = {m.filename: m.churn for m in metrics_list}
            for file, metrics in zip(files_in_repo, metrics_list):
                ext = file['ext']
                config = self.config[ext]
                analyzer = FileAnalyzer(file['path'], file['root'], config)
                if analyzer.load():
                    result = analyzer.analyze()
                    result['grade'] = grade(result['complexity'], self.threshold_low, self.threshold_high)
                    result['churn'] = metrics.churn
                    result['metrics'] = metrics
                    result['repo_root'] = file.get('repo_root', repo_root)
                    lang = result.get('language')
                    root = result.get('root')
                    if lang and root:
                        if lang not in results:
                            results[lang] = {}
                        if root not in results[lang]:
                            results[lang][root] = []
                        results[lang][root].append(result)
            # Skapa GitRepoInfo för varje repo_root
            import os
            repo_info = GitRepoInfo(
                repo_root=repo_root,
                repo_name=os.path.basename(repo_root),
                scan_dirs=scan_dirs,
                files=filepaths,
                churn_data=churn_data,
                commits=[], # Kan fyllas på vid behov
                results=results
            )
            summary[repo_root] = repo_info
        return summary
