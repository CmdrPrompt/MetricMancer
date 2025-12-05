from src.report.report_format_strategy import ReportFormatStrategy
from src.kpis.model import RepoInfo, ScanDir, File, Function
from typing import List, Tuple


class CLIReportFormat(ReportFormatStrategy):
    def _is_tracked_file(self, file_obj: File, debug: bool = False) -> bool:
        """
        Check if a file is tracked in git based on Code Ownership KPI.

        A file is considered tracked if it has valid ownership data (not None,
        not empty dict, and not the legacy 'N/A' format).

        Args:
            file_obj: File object to check
            debug: If True, print debug information

        Returns:
            True if file is git-tracked, False otherwise
        """
        from src.utilities.debug import debug_print

        co = file_obj.kpis.get('Code Ownership')
        if debug:
            debug_print(f"[DEBUG] Checking file {file_obj.file_path}: co={type(co)}")

        if not co or not hasattr(co, 'value'):
            if debug:
                debug_print(f"[DEBUG] File {file_obj.file_path}: no valid CO, returning False")
            return False

        # Handle new cache structure: value is either None/empty dict for untracked files,
        # or dict with author percentages for tracked files
        if co.value is None or not isinstance(co.value, dict) or len(co.value) == 0:
            if debug:
                debug_print(f"[DEBUG] File {file_obj.file_path}: no ownership data, returning False")
            return False

        # Check if it's the old 'N/A' format or actual ownership data
        if co.value.get('ownership') == 'N/A':
            if debug:
                debug_print(f"[DEBUG] File {file_obj.file_path}: ownership=N/A (old format), returning False")
            return False

        if debug:
            debug_print(f"[DEBUG] File {file_obj.file_path}: ownership={co.value}, returning True")
        return True

    def print_report(self, repo_info: RepoInfo, debug_print, level="file", **kwargs):
        """
        Prints a report for the given RepoInfo object directly to the console.
        This method now works directly with the hierarchical RepoInfo data model.
        """
        repo_name = repo_info.repo_name
        stats, all_files = self._get_repo_stats(repo_info)
        print(f". {repo_name} {stats}")

        # Start the recursive printing from the root of the repo_info object.
        self._print_dir_recursively(repo_info, level, prefix="│   ")

    def _collect_all_files(self, scan_dir: ScanDir) -> List[File]:
        """Recursively collects all git-tracked File objects from a ScanDir tree."""
        from src.utilities.debug import debug_print

        files = [f for f in scan_dir.files.values() if self._is_tracked_file(f, debug=True)]
        debug_print(f"[DEBUG] _collect_all_files: {len(files)} files passed filter from {len(scan_dir.files)} total")
        for sub_dir in scan_dir.scan_dirs.values():
            files.extend(self._collect_all_files(sub_dir))
        return files

    def _get_repo_stats(self, repo_info: RepoInfo) -> Tuple[str, List[File]]:
        """Calculates statistics for the entire repository by traversing the model."""
        all_files = self._collect_all_files(repo_info)
        from src.utilities.debug import debug_print
        debug_print(f"[DEBUG] _get_repo_stats: collected {len(all_files)} files")

        if not all_files:
            return "[No files analyzed]", []

        complexities = [f.kpis['complexity'].value for f in all_files if f.kpis.get('complexity')]
        churns = [f.kpis['churn'].value for f in all_files if f.kpis.get('churn')]

        avg_complexity = round(sum(complexities) / len(complexities), 1) if complexities else 0
        min_complexity = round(min(complexities), 1) if complexities else 0
        max_complexity = round(max(complexities), 1) if complexities else 0
        avg_churn = round(sum(churns) / len(churns), 1) if churns else 0

        stats_str = f"[Avg. C:{avg_complexity}, Min C:{min_complexity}, Max C:{max_complexity}, Avg. Churn:{avg_churn}]"
        return stats_str, all_files

    def _print_dir_recursively(self, scan_dir: ScanDir, level: str, prefix: str = ""):
        """
        Recursively prints the directory structure, its files, and their KPIs.
        Directories containing only untracked files (ownership N/A) are not shown.
        """
        # Filter files: only tracked files
        files = [f for f in scan_dir.files.values() if self._is_tracked_file(f)]
        # Recursively filter subdirs: only show if they or their children have tracked files
        visible_dirs = []
        for d in scan_dir.scan_dirs.values():
            # Check if this subdir or any of its descendants have tracked files
            found = self._has_tracked_files(d)
            if found:
                visible_dirs.append(d)

        items = sorted(visible_dirs, key=lambda d: d.dir_name) + sorted(files, key=lambda f: f.name)

        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = "└── " if is_last else "├── "
            if isinstance(item, ScanDir):
                # Format directory with KPI stats
                dir_stats = self._format_dir_stats(item)
                print(f"{prefix}{connector}{item.dir_name}/ {dir_stats}")
                new_prefix = prefix + ("    " if is_last else "│   ")
                self._print_dir_recursively(item, level, new_prefix)
            elif isinstance(item, File):
                stats_str = self._format_file_stats(item)
                print(f"{prefix}{connector}{item.name} {stats_str}")
                if level == "function" and item.functions:
                    self._print_functions(item.functions, prefix, is_last)

    def _has_tracked_files(self, scan_dir: ScanDir) -> bool:
        """Returns True if this dir or any subdir contains a tracked file."""
        for f in scan_dir.files.values():
            if self._is_tracked_file(f):
                return True
        for d in scan_dir.scan_dirs.values():
            if self._has_tracked_files(d):
                return True
        return False

    def _get_kpi_value(self, kpis: dict, kpi_name: str) -> str:
        """
        Extract KPI value with proper None handling.

        Returns '?' if KPI is missing or value is None.
        This ensures consistent fallback behavior across all KPIs.
        """
        kpi = kpis.get(kpi_name)
        return kpi.value if kpi and kpi.value is not None else '?'

    def _format_dir_stats(self, dir_obj: ScanDir) -> str:
        """
        Format average KPI statistics for a directory.

        Shows average values for all files in the directory tree.
        Returns empty string if no KPIs are available.
        """
        c_val = self._get_kpi_value(dir_obj.kpis, 'complexity')
        cog_val = self._get_kpi_value(dir_obj.kpis, 'cognitive_complexity')
        ch_val = self._get_kpi_value(dir_obj.kpis, 'churn')
        h_val = self._get_kpi_value(dir_obj.kpis, 'hotspot')

        # Only show if at least one KPI is available
        if all(v == '?' for v in [c_val, cog_val, ch_val, h_val]):
            return ""

        return f"[Avg C:{c_val}, Avg Cog:{cog_val}, Avg Churn:{ch_val}, Avg Hotspot:{h_val}]"

    def _format_file_stats(self, file_obj: File) -> str:
        """
        Formats the KPI statistics string for a single file,
        including code ownership, shared ownership, and cognitive complexity if available.
        """
        c_val = self._get_kpi_value(file_obj.kpis, 'complexity')
        cog_val = self._get_kpi_value(file_obj.kpis, 'cognitive_complexity')
        ch_val = self._get_kpi_value(file_obj.kpis, 'churn')
        h_val = self._get_kpi_value(file_obj.kpis, 'hotspot')

        # Code Ownership
        code_ownership = file_obj.kpis.get('Code Ownership')
        ownership_str = ''
        if code_ownership and hasattr(code_ownership, 'value') and isinstance(code_ownership.value, dict):
            if 'error' in code_ownership.value:
                ownership_str = " Ownership: ERROR"
            elif code_ownership.value:
                # Limit to max 3 owners for readability
                sorted_owners = sorted(code_ownership.value.items(), key=lambda x: x[1], reverse=True)
                owners = [f"{author} {percent}%" for author, percent in sorted_owners[:3]]
                if len(sorted_owners) > 3:
                    owners.append(f"+ {len(sorted_owners) - 3} more")
                ownership_str = " Owners: " + ", ".join(owners)

        # Shared Ownership
        shared_ownership = file_obj.kpis.get('Shared Ownership')
        shared_str = ''
        if shared_ownership and hasattr(shared_ownership, 'value') and isinstance(shared_ownership.value, dict):
            if 'error' in shared_ownership.value:
                shared_str = " Shared: ERROR"
            elif 'num_significant_authors' in shared_ownership.value:
                num_authors = shared_ownership.value['num_significant_authors']
                authors = shared_ownership.value.get('authors', [])
                threshold = shared_ownership.value.get('threshold', 20.0)

                if num_authors == 0:
                    shared_str = f" Shared: None (threshold: {threshold}%)"
                elif num_authors == 1:
                    shared_str = f" Shared: Single owner ({authors[0]})"
                else:
                    author_list = ", ".join(authors[:3])  # Show max 3 authors
                    if len(authors) > 3:
                        author_list += "..."
                    shared_str = f" Shared: {num_authors} authors ({author_list})"
            elif shared_ownership.value.get('shared_ownership') == 'N/A':
                shared_str = " Shared: N/A"

        # Always append ownership_str and shared_str directly after Hotspot, trimmed
        return (f"[C:{c_val}, Cog:{cog_val}, Churn:{ch_val}, Hotspot:{h_val}]" +
                (ownership_str if ownership_str else "") +
                (" " if ownership_str and shared_str else "") +
                (shared_str if shared_str else ""))

    def _print_functions(self, functions: List[Function], prefix: str, is_file_last: bool):
        """Prints the functions for a given file, including cognitive complexity if available."""
        func_prefix = prefix + ("    " if is_file_last else "│   ")

        for i, func in enumerate(sorted(functions, key=lambda f: f.name)):
            is_last_func = (i == len(functions) - 1)
            connector = "└── " if is_last_func else "├── "

            c_val = self._get_kpi_value(func.kpis, 'complexity')
            cog_val = self._get_kpi_value(func.kpis, 'cognitive_complexity')
            stats_str = f"[C:{c_val}, Cog:{cog_val}]"
            print(f"{func_prefix}{connector}{func.name}() {stats_str}")
