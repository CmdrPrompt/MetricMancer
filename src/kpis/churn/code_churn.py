import os
from src.utilities.debug import debug_print

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
            scan_abs = os.path.abspath(scan)
            # Walk up from repo_abs until .git is found
            current = repo_abs
            while not os.path.isdir(os.path.join(current, '.git')):
                parent = os.path.dirname(current)
                if parent == current:
                    break
                current = parent
            self.repo_scan_pairs.append((current, scan_abs))
        self.churn_data = {}

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
        from src.utilities.debug import debug_print
        from pydriller import Repository
        churn_data = {}
        path_aliases = {}
        for repo_root, scan_dir in self.repo_scan_pairs:
            if not os.path.isdir(os.path.join(repo_root, '.git')):
                debug_print(f"[DEBUG] Skipping {repo_root}: no .git directory found")
                continue
            commits = list(Repository(repo_root).traverse_commits())
            debug_print(f"[DEBUG] Found {len(commits)} commits in repo {repo_root}")
            mod_count = 0
            for commit in commits:
                for mod in getattr(commit, "modified_files", []):
                    mod_count += 1
                    added = len(mod.diff_parsed['added']) if hasattr(mod, 'diff_parsed') else 0
                    removed = len(mod.diff_parsed['deleted']) if hasattr(mod, 'diff_parsed') else 0
                    paths = set()
                    if mod.new_path:
                        paths.add(os.path.abspath(os.path.join(repo_root, mod.new_path)))
                    if mod.old_path:
                        paths.add(os.path.abspath(os.path.join(repo_root, mod.old_path)))
                    for abs_path in paths:
                        churn_data.setdefault(abs_path, 0)
                        churn_data[abs_path] += added + removed
                        debug_print(f"[DEBUG] Mod processed: {abs_path}, added={added}, removed={removed}, churn={churn_data[abs_path]}")
                        # Track aliases for aggregation
                        for p in paths:
                            path_aliases.setdefault(p, set()).update(paths)
            debug_print(f"[DEBUG] Total modifications processed in repo {repo_root}: {mod_count}")
        # Aggregate churn for files with aliases (moved/renamed)
        aggregated_churn = {}
        for path, aliases in path_aliases.items():
            total = sum(churn_data.get(alias, 0) for alias in aliases)
            for alias in aliases:
                aggregated_churn[alias] = total
        # Merge aggregated churn into churn_data
        churn_data.update(aggregated_churn)
        debug_print('[DEBUG] Key churn values:')
        key_files = [
            '/Users/thomas/Code/VSCode/ComplexityScanner/src/analyzer.py',
            '/Users/thomas/Code/VSCode/ComplexityScanner/src/churn/code_churn.py',
        ]
        for kf in key_files:
            debug_print(f'  {kf}: churn={churn_data.get(kf, "(not found)")}')
        return churn_data
