from .report_interface import ReportInterface
from collections import Counter
import os



class CLIReportGenerator(ReportInterface):
    def __init__(self, repo_infos, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None):
        # repo_infos ska vara en lista av GitRepoInfo
        self.repo_infos = repo_infos
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold

    def generate(self, output_file=None):
        from src.utilities.debug import debug_print
        # from src.debug import debug_print
        for repo_info in self.repo_infos:
            repo_root = repo_info.repo_root
            repo_name = repo_info.repo_name or os.path.basename(repo_root)
            scan_dirs = repo_info.scan_dirs
            results = repo_info.results
            print(f". {repo_name}")
            for language in results:
                for root in results[language]:
                    files = results[language][root]
                    # Prepare stats for summary
                    complexities = [f.get('complexity', 0) for f in files]
                    churns = [f.get('churn', 0) for f in files]
                    grades = [f.get('grade', '') for f in files]
                    avg_complexity = round(sum(complexities)/len(complexities), 1) if complexities else 0
                    min_complexity = round(min(complexities), 1) if complexities else 0
                    max_complexity = round(max(complexities), 1) if complexities else 0
                    avg_churn = round(sum(churns)/len(churns), 1) if churns else 0
                    grade = Counter(grades).most_common(1)[0][0] if grades else ''
                    grade_icon = '✅' if grade.lower() == 'low' else ('⚠️' if grade.lower() == 'medium' else '🔥')
                    stats = f"[C:{avg_complexity}, Min:{min_complexity}, Max:{max_complexity}, Churn:{avg_churn}, Grade:{grade} {grade_icon}]"
                    print(f"│   Scan-dir: {root} (Language: {language})")
                    print(f"│   | {stats}")
                    # Build tree structure for files in this scan-dir
                    file_tuples = []
                    for f in files:
                        abs_path = os.path.abspath(os.path.join(root, f['path']))
                        root_abs = os.path.abspath(root)
                        debug_print(f"[DEBUG] CLIReportGenerator: f['path']={f['path']}, abs_path={abs_path}, root_abs={root_abs}")
                        # Robust path inclusion: include if abs_path is under root_abs
                        try:
                            if os.path.commonpath([abs_path, root_abs]) != root_abs:
                                continue
                        except ValueError:
                            continue
                        rel_path = os.path.relpath(abs_path, root_abs)
                        if f.get('complexity') is not None and f.get('churn') is not None:
                            hotspot_score = round(f['complexity'] * f['churn'], 1)
                        else:
                            hotspot_score = "-"
                        stats_str = f"[C:{f.get('complexity', '?')}, Churn:{f.get('churn', '?')}, Hotspot:{hotspot_score}, Grade:{f.get('grade', '?')}]"
                        file_tuples.append((rel_path, stats_str))
                    def build_tree(paths):
                        tree = {}
                        for path, stats in paths:
                            parts = path.split(os.sep)
                            node = tree
                            for part in parts[:-1]:
                                node = node.setdefault(part, {})
                            node[parts[-1]] = stats
                        return tree
                    def print_tree(node, prefix="", is_last=True):
                        items = sorted(node.items(), key=lambda x: x[0].lower())
                        for idx, (name, value) in enumerate(items):
                            connector = "└── " if idx == len(items)-1 else "├── "
                            if isinstance(value, dict):
                                print(f"{prefix}{connector}{name}")
                                extension = "    " if idx == len(items)-1 else "│   "
                                print_tree(value, prefix + extension, is_last=(idx == len(items)-1))
                            else:
                                print(f"{prefix}{connector}{name} {value}")
                    tree = build_tree(file_tuples)
                    print_tree(tree, prefix="│   ")
