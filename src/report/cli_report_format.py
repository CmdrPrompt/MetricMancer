from .report_format_strategy import ReportFormatStrategy
from src.utilities.tree_printer import TreePrinter

class CLIReportFormat(ReportFormatStrategy):
    def print_report(self, repo_info, debug_print):
        repo_name = self._get_repo_name(repo_info)
        stats = self._get_repo_stats(repo_info)
        print(f". {repo_name} {stats}")
        self._print_repo_file_trees(repo_info, debug_print)

    def _get_repo_name(self, repo_info):
        import os
        import subprocess
        repo_root = repo_info.repo_root
        try:
            repo_name = subprocess.check_output([
                'basename',
                subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).strip()
            ]).decode().strip()
        except Exception:
            repo_name = os.path.basename(repo_root)
        return repo_name

    def _get_repo_stats(self, repo_info):
        stats = repo_info.repo_stats
        grade_icon = '✅' if stats['grade'].lower() == 'low' else ('⚠️' if stats['grade'].lower() == 'medium' else '🔥')
        return f"[C:{stats['avg_complexity']}, Min:{stats['min_complexity']}, Max:{stats['max_complexity']}, Churn:{stats['avg_churn']}, Grade:{stats['grade']} {grade_icon}]"

    def _print_repo_file_trees(self, repo_info, debug_print):
        tree_printer = TreePrinter(debug_print=debug_print)
        results = repo_info.results
        for language in results:
            for root in results[language]:
                files = results[language][root]
                print(f"│   Scan-dir: {root} (Language: {language})")
                file_tuples = self._get_file_tuples(files, root, debug_print)
                tree = tree_printer.build_tree(file_tuples)
                tree_printer.print_tree(tree, prefix="│   ")

    def _get_file_tuples(self, files, root, debug_print):
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
            stats_str = f"[C:{f.get('complexity', '?')}, Churn:{churn_value}, Hotspot:{hotspot_score}, Grade:{f.get('grade', '?')}]"
            file_tuples.append((rel_path, stats_str))
        return file_tuples
