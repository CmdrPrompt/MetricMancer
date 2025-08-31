import os
from src.debug import debug_print

class FileMetrics:
    def __init__(self, filename, churn=0, complexity=0):
        self.filename = filename
        self.churn = churn
        self.complexity = complexity


class CodeChurnAnalyzer:
    def __init__(self, repo_scan_pairs):
        # repo_scan_pairs: List of (repo_root, scan_dir)
        self.repo_scan_pairs = [(os.path.abspath(repo), os.path.abspath(scan)) for repo, scan in repo_scan_pairs]
    # ...existing code...

    @staticmethod
    def find_repo_root(scan_dirs):
        import os
        # Start from first scan dir, walk up until .git is found
        start_dir = os.path.abspath(scan_dirs[0]) if scan_dirs else os.getcwd()
        debug_print(f"[DEBUG] find_repo_root: start_dir={start_dir}")
        current = start_dir
        while True:
            if os.path.isdir(os.path.join(current, '.git')):
                debug_print(f"[DEBUG] find_repo_root: found .git at {current}")
                return current
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        debug_print(f"[DEBUG] find_repo_root: fallback to {os.getcwd()}")
        return os.getcwd()  # fallback


    def analyze(self):
        from pydriller import Repository
        import os
        churn_data = {}
        for repo_root, scan_dir in self.repo_scan_pairs:
            if not os.path.isdir(os.path.join(repo_root, '.git')):
                continue
            commits = list(Repository(repo_root).traverse_commits())
            for commit in commits:
                for mod in getattr(commit, "modified_files", []):
                    added = len(mod.diff_parsed['added']) if hasattr(mod, 'diff_parsed') else 0
                    removed = len(mod.diff_parsed['deleted']) if hasattr(mod, 'diff_parsed') else 0
                    path = mod.new_path or mod.old_path
                    if path:
                        norm_path = os.path.relpath(os.path.join(repo_root, path), repo_root)
                        churn_data.setdefault(norm_path, 0)
                        churn_data[norm_path] += added + removed
        return churn_data
