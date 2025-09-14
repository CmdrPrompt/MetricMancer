import os
from src.utilities.debug import debug_print
from src.utilities.git_helpers import find_git_repo_root

class CodeChurnAnalyzer:
    def __init__(self, repo_scan_pairs):
        # repo_scan_pairs: List of (repo_root, scan_dir)
        # Fix: If repo_root is a subfolder, walk up to find the actual .git root
        self.repo_scan_pairs = []
        for repo, scan in repo_scan_pairs:
            repo_abs = os.path.abspath(repo)
            try:
                git_root = find_git_repo_root(repo_abs)
            except Exception as e:
                debug_print(f"[WARN] Could not find git root for {repo_abs}. Error: {e}")
                git_root = None
            self.repo_scan_pairs.append((git_root, os.path.abspath(scan)))
        self.churn_data = {}

    def analyze(self):
        """
        Analyzes code churn for the configured repositories using PyDriller.
        It counts the number of commits that modified each file.
        """
        from pydriller import Repository

        # Group scan directories by git root to avoid traversing the same repo multiple times
        repos_to_scan = {}
        for git_root, scan_dir in self.repo_scan_pairs:
            if git_root not in repos_to_scan:
                repos_to_scan[git_root] = []
            repos_to_scan[git_root].append(scan_dir)

        for repo_path, scan_dirs in repos_to_scan.items():
            debug_print(f"[DEBUG] Analyzing churn for repo: {repo_path}")
            try:
                # Use PyDriller to iterate through commits
                for commit in Repository(repo_path).traverse_commits():
                    for modification in commit.modifications:
                        if modification.new_path:
                            abs_path = os.path.join(repo_path, modification.new_path)
                            # Check if the modified file is within one of the scanned directories
                            if any(abs_path.startswith(scan_dir) for scan_dir in scan_dirs):
                                self.churn_data[abs_path] = self.churn_data.get(abs_path, 0) + 1
            except Exception as e:
                debug_print(f"[WARN] Could not analyze churn for {repo_path}. Is it a valid git repository? Error: {e}")
        
        debug_print(f"[DEBUG] Churn analysis complete. Found churn data for {len(self.churn_data)} files.")
        return self.churn_data
