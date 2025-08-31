from .code_churn import FileMetrics, CodeChurnAnalyzer


class MetricsCollector:
    def __init__(self, scanner, repo_path='.', scan_dirs=None):
        self.scanner = scanner
        self.repo_path = repo_path
        self.scan_dirs = scan_dirs if scan_dirs else [repo_path]
        # Skapa lista av (repo_root, scan_dir)-par
        self.repo_scan_pairs = [(self.repo_path, scan_dir) for scan_dir in self.scan_dirs]
        self.churn_analyzer = CodeChurnAnalyzer(self.repo_scan_pairs)

    def collect(self, filepaths, root_dir=''):
        import os
        from src.fileanalyzer import FileAnalyzer
        from src.config import LANGUAGES
        churn = self.churn_analyzer.analyze()
        metrics = []
        for filepath in filepaths:
            ext = os.path.splitext(filepath)[1]
            config = LANGUAGES.get(ext, {})
            analyzer = FileAnalyzer(filepath, root_dir, config)
            if analyzer.load():
                result = analyzer.analyze()
                complexity = result.get('complexity', 0)
            else:
                complexity = 0
            abs_path = os.path.abspath(filepath)
            relpath = os.path.relpath(abs_path, self.repo_path)
            churn_value = churn.get(relpath, 0)
            metrics.append(FileMetrics(
                filename=filepath,
                churn=churn_value,
                complexity=complexity
            ))
        return metrics
