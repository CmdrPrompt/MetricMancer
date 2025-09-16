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
        Adds deep debug logging for repo_path, scan_dirs, .git presence, PyDriller commits/files, and exceptions.
        """
        try:
            from pydriller import Repository
        except ImportError:
            debug_print("[DEBUG] PyDriller not installed, skipping churn analysis.")
            return self.churn_data

        # Group scan directories by git root to avoid traversing the same repo multiple times
        repos_to_scan = {}
        for git_root, scan_dir in self.repo_scan_pairs:
            if git_root not in repos_to_scan:
                repos_to_scan[git_root] = []
            repos_to_scan[git_root].append(scan_dir)

        for repo_path, scan_dirs in repos_to_scan.items():
            debug_print(f"[DEBUG] Analyzing churn for repo: {repo_path}")
            debug_print(f"[DEBUG] scan_dirs for repo: {scan_dirs}")
            git_dir = os.path.join(repo_path, '.git')
            if not os.path.isdir(git_dir):
                debug_print(f"[DEBUG] No .git directory found at {git_dir}, skipping churn analysis for this repo.")
                continue
            debug_print(f"[DEBUG] .git directory found at {git_dir}")
            if not scan_dirs:
                debug_print(f"[DEBUG] scan_dirs is empty, skipping churn analysis for this repo.")
                continue
            for scan_dir in scan_dirs:
                debug_print(f"[DEBUG] Scanning churn for dir: {scan_dir}")
                if not os.path.isdir(scan_dir):
                    debug_print(f"[DEBUG] scan_dir {scan_dir} does not exist or is not a directory.")
            try:
                commit_count = 0
                file_mod_count = 0
                files_seen = set()
                for commit in Repository(repo_path).traverse_commits():
                    commit_count += 1
                    debug_print(f"[DEBUG] PyDriller commit: {getattr(commit, 'hash', '?')} ({getattr(getattr(commit, 'author', None), 'name', '?')} {getattr(commit, 'author_date', '?')})")
                    # PyDriller API compatibility: try both 'modifications' and 'modified_files' (newer)
                    mods = None
                    if hasattr(commit, 'modifications'):
                        mods = commit.modifications
                    elif hasattr(commit, 'modified_files'):
                        mods = commit.modified_files
                    else:
                        debug_print(f"[WARN] Commit object has neither 'modifications' nor 'modified_files': {dir(commit)}")
                        continue
                    for modification in mods:
                        file_mod_count += 1
                        # Try both new_path and filename attributes
                        new_path = getattr(modification, 'new_path', None)
                        if not new_path:
                            new_path = getattr(modification, 'filename', None)
                        if new_path:
                            abs_path = os.path.join(repo_path, new_path)
                            if any(abs_path.startswith(scan_dir) for scan_dir in scan_dirs):
                                self.churn_data[abs_path] = self.churn_data.get(abs_path, 0) + 1
                                files_seen.add(abs_path)
                debug_print(f"[DEBUG] PyDriller found {commit_count} commits, {file_mod_count} file modifications in {repo_path}")
                debug_print(f"[DEBUG] PyDriller files seen in {repo_path}: {list(files_seen)}")
            except Exception as e:
                debug_print(f"[WARN] Could not analyze churn for {repo_path}. Is it a valid git repository? Error: {e}")
        debug_print(f"[DEBUG] Churn analysis complete. Found churn data for {len(self.churn_data)} files.")
        debug_print(f"[DEBUG] Churn data keys: {list(self.churn_data.keys())}")
        return self.churn_data
