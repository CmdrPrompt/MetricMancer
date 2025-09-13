import os
from src.utilities.debug import debug_print
from src.utilities.git_helpers import find_git_repo_root

class FileMetrics:
    def __init__(self, filename, abs_path=None, churn=0, complexity=0):
        self.filename = filename
        self.abs_path = abs_path
        self.churn = churn
        self.complexity = complexity

class CodeChurnAnalyzer:
    def __init__(self, repo_scan_pairs):
        # repo_scan_pairs: List of (repo_root, scan_dir)
        # Fix: If repo_root is a subfolder, walk up to find the actual .git root
        self.repo_scan_pairs = []
        for repo, scan in repo_scan_pairs:
            repo_abs = os.path.abspath(repo)
            git_root = find_git_repo_root(repo_abs)
            self.repo_scan_pairs.append((git_root, os.path.abspath(scan)))
        self.churn_data = {}

    def analyze(self):
        """
        Analyzes code churn for the configured repositories.
        This is a placeholder implementation.
        """
        debug_print("[DEBUG] CodeChurnAnalyzer.analyze() called (placeholder).")
        return self.churn_data
