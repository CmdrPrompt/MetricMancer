from src.report.report_format_strategy import ReportFormatStrategy

# Placera MachineCLIReportFormat sist för att undvika importproblem

class MachineCLIReportFormat(ReportFormatStrategy):
    def print_report(self, repo_info, debug_print, level="file"):
        import os
        import sys
        import csv
        results = repo_info.results
        writer = csv.writer(sys.stdout, delimiter=';', lineterminator='\n')
        # Header
        if level == "function":
            writer.writerow(["filename", "function_name", "cyclomatic_complexity", "churn", "hotspot_score", "grade", "lines_of_code", "repo_name"])
        else:
            writer.writerow(["filename", "cyclomatic_complexity", "churn", "hotspot_score", "grade", "repo_name"])
        for language in results:
            for root in results[language]:
                files = results[language][root]
                for f in files:
                    rel_path = os.path.relpath(f.get('path', ''), repo_info.repo_root) if repo_info.repo_root else f.get('path', '')
                    complexity = f.get('complexity', None)
                    churn = f.get('churn', None)
                    grade = f.get('grade', None)
                    repo_name = getattr(repo_info, 'git_folder_name', None) or getattr(repo_info, 'repo_name', None)
                    if complexity is not None and churn is not None:
                        try:
                            hotspot_score = round(float(complexity) * float(churn), 1)
                        except Exception:
                            hotspot_score = None
                    else:
                        hotspot_score = None
                    if level == "function" and 'functions' in f and isinstance(f['functions'], list):
                        for func in f['functions']:
                            writer.writerow([
                                rel_path,
                                func.get("name", ""),
                                func.get("complexity", None),
                                churn,
                                func.get("hotspot_score", hotspot_score),
                                grade,
                                func.get("lines_of_code", None),
                                repo_name
                            ])
                    else:
                        writer.writerow([
                            rel_path,
                            complexity,
                            churn,
                            hotspot_score,
                            grade,
                            repo_name
                        ])

from src.report.report_format_strategy import ReportFormatStrategy
from src.utilities.tree_printer import TreePrinter

class CLIReportFormat(ReportFormatStrategy):
    def print_report(self, repo_info, debug_print, level="file", with_churn=False, with_complexity=False):
        repo_name = self._get_repo_name(repo_info)
        stats = self._get_repo_stats(repo_info, with_churn=True, with_complexity=True)
        timestamp = getattr(repo_info, 'timestamp', None)
        if timestamp:
            print(f"# Timestamp: {timestamp}")
        print(f". {repo_name} {stats}")
        self._print_repo_file_trees(repo_info, debug_print, level=level, with_churn=True, with_complexity=True)

    def _get_repo_name(self, repo_info):
        import os
        repo_root = repo_info.repo_root
        repo_name = os.path.basename(repo_root) if repo_root else ""
        return repo_name

    def _get_repo_stats(self, repo_info, with_churn=False, with_complexity=False):
        stats = repo_info.repo_stats
        grade_icon = '✅' if stats['grade'].lower() == 'low' else ('⚠️' if stats['grade'].lower() == 'medium' else '🔥')
        parts = []
        parts.append(f"C:{stats['avg_complexity']}")
        parts.append(f"Min:{stats['min_complexity']}")
        parts.append(f"Max:{stats['max_complexity']}")
        parts.append(f"Churn:{stats['avg_churn']}")
        parts.append(f"Grade:{stats['grade']} {grade_icon}")
        return "[" + ", ".join(parts) + "]"

    def _print_repo_file_trees(self, repo_info, debug_print, level="file", with_churn=False, with_complexity=False):
        tree_printer = TreePrinter(debug_print=debug_print)
        results = repo_info.results
        for language in results:
            for root in results[language]:
                files = results[language][root]
                print(f"│   Scan-dir: {root} (Language: {language})")
                file_tuples = self._get_file_tuples(files, root, debug_print, level=level, with_churn=True, with_complexity=True)
                tree = tree_printer.build_tree(file_tuples)
                tree_printer.print_tree(tree, prefix="│   ")

    def _get_file_tuples(self, files, root, debug_print, level="file", with_churn=False, with_complexity=False):
        import os
        file_tuples = []
        for f in files:
            abs_path = os.path.abspath(os.path.join(root, f['path']))
            root_abs = os.path.abspath(root)
            debug_print(f"[DEBUG] CLIReportFormat: f['path']={f['path']}, abs_path={abs_path}, root_abs={root_abs}")
            try:
                if os.path.commonpath([abs_path, root_abs]) != root_abs:
                    continue
            except ValueError:
                continue
            rel_path = os.path.relpath(abs_path, root_abs)
            churn_value = f.get('churn', 0)
            if f.get('complexity') is not None and churn_value is not None:
                hotspot_score = round(f['complexity'] * churn_value, 1)
            else:
                hotspot_score = "-"
            if level == "function" and 'functions' in f and isinstance(f['functions'], list):
                for func in f['functions']:
                    func_stats = []
                    func_stats.append(f"Func:{func.get('name','')}")
                    func_stats.append(f"C:{func.get('complexity','?')}")
                    func_stats.append(f"Churn:{churn_value}")
                    func_stats.append(f"Hotspot:{round(func.get('complexity',0)*churn_value,1) if func.get('complexity') is not None else '-'}")
                    func_stats.append(f"Grade:{func.get('grade','?')}")
                    func_stats.append(f"LOC:{func.get('lines_of_code','?')}")
                    file_tuples.append((f"{rel_path}:{func.get('name','')}", "[" + ", ".join(func_stats) + "]"))
            else:
                stats = []
                stats.append(f"C:{f.get('complexity', '?')}")
                stats.append(f"Churn:{churn_value}")
                stats.append(f"Hotspot:{hotspot_score}")
                stats.append(f"Grade:{f.get('grade', '?')}")
                file_tuples.append((rel_path, "[" + ", ".join(stats) + "]"))
        return file_tuples
