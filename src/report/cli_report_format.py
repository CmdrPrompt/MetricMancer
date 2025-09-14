from .report_format_strategy import ReportFormatStrategy
from src.kpis.model import RepoInfo, ScanDir, File, Function
from typing import List, Tuple
import os

class CLIReportFormat(ReportFormatStrategy):
    def print_report(self, repo_info: RepoInfo, debug_print, level="file"):
        """
        Prints a report for the given RepoInfo object directly to the console.
        This method now works directly with the hierarchical RepoInfo data model.
        """
        repo_name = repo_info.repo_name
        stats, all_files = self._get_repo_stats(repo_info)
        print(f". {repo_name} {stats}")

        # Start the recursive printing from the root of the repo_info object.
        self._print_dir_recursively(repo_info, level, prefix="│   ")
        """
        Format the report for CLI output.
        Args:
            summary: List of summary dictionaries for each root.
            detailed: If True, include detailed file-level information.
        Returns:
            str: Formatted report as a string for CLI display.
        """
        files = list(scan_dir.files.values())
        for sub_dir in scan_dir.scan_dirs.values():
            files.extend(self._collect_all_files(sub_dir))
        return files

    def _get_repo_stats(self, repo_info: RepoInfo) -> Tuple[str, List[File]]:
        """Calculates statistics for the entire repository by traversing the model."""
        from collections import Counter

    all_files = self._collect_all_files(repo_info)
    if not all_files:
        return "[No files analyzed]", []

    complexities = [f.kpis['complexity'].value for f in all_files if 'complexity' in f.kpis]
    churns = [f.kpis['churn'].value for f in all_files if 'churn' in f.kpis]
    # Grades are not stored on the new model, they are calculated on the fly.
    # This part can be added if grading is needed at the repo level.

    avg_complexity = round(sum(complexities) / len(complexities), 1) if complexities else 0
    min_complexity = round(min(complexities), 1) if complexities else 0
    max_complexity = round(max(complexities), 1) if complexities else 0
    avg_churn = round(sum(churns) / len(churns), 1) if churns else 0

    # Dummy grade for now
    grade = "Medium"
    grade_icon = '[WARN]'

    stats_str = f"[C:{avg_complexity}, Min:{min_complexity}, Max:{max_complexity}, Churn:{avg_churn}, Grade:{grade} {grade_icon}]"
    return stats_str, all_files

    def _print_dir_recursively(self, scan_dir: ScanDir, level: str, prefix: str = ""):
        """
        Recursively prints the directory structure, its files, and their KPIs.
        """
        # Combine and sort items: directories first, then files
        dirs = sorted(scan_dir.scan_dirs.values(), key=lambda d: d.dir_name)
        files = sorted(scan_dir.files.values(), key=lambda f: f.name)
        items = dirs + files

        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = "└── " if is_last else "├── "
            
            if isinstance(item, ScanDir):
                print(f"{prefix}{connector}{item.dir_name}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
                self._print_dir_recursively(item, level, new_prefix)
            
            elif isinstance(item, File):
                stats_str = self._format_file_stats(item)
                print(f"{prefix}{connector}{item.name} {stats_str}")
                if level == "function" and item.functions:
                    self._print_functions(item.functions, item.kpis.get('churn', type('obj', (object,), {'value':0})()).value, prefix, is_last)

    def _format_file_stats(self, file_obj: File) -> str:
        """Formats the KPI statistics string for a single file."""
        complexity = file_obj.kpis.get('complexity')
        churn = file_obj.kpis.get('churn')
        hotspot = file_obj.kpis.get('hotspot')

        c_val = complexity.value if complexity else '?'
        ch_val = churn.value if churn else '?'
        h_val = hotspot.value if hotspot else '?'
        # Grade can be calculated here if needed
        # from src.report.grading import grade
        # grade_val = grade(c_val) if c_val != '?' else '?'

        return f"[C:{c_val}, Churn:{ch_val}, Hotspot:{h_val}]"

    def _print_functions(self, functions: List[Function], file_churn: int, prefix: str, is_file_last: bool):
        """Prints the functions for a given file."""
        func_prefix = prefix + ("    " if is_file_last else "│   ")
        
        for i, func in enumerate(functions):
            is_last_func = (i == len(functions) - 1)
            connector = "└── " if is_last_func else "├── "
            
            complexity = func.kpis.get('complexity')
            c_val = complexity.value if complexity else 0
            h_val = c_val * file_churn
            
            stats_str = f"[C:{c_val}, Hotspot:{h_val}]"
            print(f"{func_prefix}{connector}{func.name}() {stats_str}")
