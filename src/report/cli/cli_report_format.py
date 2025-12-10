from src.report.report_format_strategy import ReportFormatStrategy
from src.kpis.model import RepoInfo, ScanDir, File, Function
from src.utilities.debug import debug_print
from typing import List, Tuple, Dict


class CLIReportFormat(ReportFormatStrategy):
    """
    CLI report formatter with tree-based visualization.

    Provides human-readable command-line output with hierarchical
    directory structure and KPI metrics.
    """

    # Constants for tree formatting
    CONNECTOR_LAST = "└── "
    CONNECTOR_CONTINUE = "├── "
    PREFIX_LAST = "    "
    PREFIX_CONTINUE = "│   "

    # Constants for ownership formatting
    MAX_AUTHORS_DISPLAY = 3

    def _is_tracked_file(self, file_obj: File, debug: bool = False) -> bool:
        """
        Check if a file is tracked in git based on Code Ownership KPI.

        Args:
            file_obj: File object to check
            debug: If True, print debug information (unused, kept for API compatibility)

        Returns:
            True if file is git-tracked, False otherwise
        """
        return self._has_valid_ownership_data(file_obj.kpis.get('Code Ownership'))

    def print_report(self, repo_info: RepoInfo, debug_print, level="file", **kwargs):
        """
        Prints a report for the given RepoInfo object directly to the console.
        This method now works directly with the hierarchical RepoInfo data model.
        """
        repo_name = repo_info.repo_name
        stats, all_files = self._get_repo_stats(repo_info)
        print(f". {repo_name} {stats}")

        # Start the recursive printing from the root of the repo_info object.
        self._print_dir_recursively(repo_info, level, prefix=self.PREFIX_CONTINUE)

    def _collect_all_files(self, scan_dir: ScanDir, debug: bool = True) -> List[File]:
        """
        Recursively collects all git-tracked File objects from a ScanDir tree.

        Args:
            scan_dir: Directory to scan
            debug: Enable debug output (default: True)

        Returns:
            List of tracked File objects
        """
        files = [f for f in scan_dir.files.values() if self._is_tracked_file(f, debug=debug)]
        debug_print(f"[DEBUG] _collect_all_files: {len(files)} files passed filter from {len(scan_dir.files)} total")

        for sub_dir in scan_dir.scan_dirs.values():
            files.extend(self._collect_all_files(sub_dir, debug=debug))

        return files

    def _calc_stats(self, values: List[float]) -> Tuple[float, float, float]:
        """Calculate avg, min, max for a list of values. Returns (0,0,0) if empty."""
        if not values:
            return 0, 0, 0
        return (
            round(sum(values) / len(values), 1),
            round(min(values), 1),
            round(max(values), 1)
        )

    def _get_repo_stats(self, repo_info: RepoInfo) -> Tuple[str, List[File]]:
        """Calculates statistics for the entire repository by traversing the model."""
        all_files = self._collect_all_files(repo_info)
        debug_print(f"[DEBUG] _get_repo_stats: collected {len(all_files)} files")

        if not all_files:
            return "[No files analyzed]", []

        complexities = [f.kpis['complexity'].value for f in all_files if f.kpis.get('complexity')]
        churns = [f.kpis['churn'].value for f in all_files if f.kpis.get('churn')]

        avg_c, min_c, max_c = self._calc_stats(complexities)
        avg_churn = self._calc_stats(churns)[0]  # Only need avg for churn

        stats_str = f"[Avg. C:{avg_c}, Min C:{min_c}, Max C:{max_c}, Avg. Churn:{avg_churn}]"
        return stats_str, all_files

    def _get_visible_directories(self, scan_dir: ScanDir) -> List[ScanDir]:
        """
        Get list of subdirectories that contain tracked files.

        Returns only directories that have at least one tracked file
        in themselves or their descendants.
        """
        visible_dirs = []
        for d in scan_dir.scan_dirs.values():
            if self._has_tracked_files(d):
                visible_dirs.append(d)
        return visible_dirs

    def _print_directory_item(self, item: ScanDir, connector: str, prefix: str, level: str):
        """Print a single directory item with stats and recurse into it."""
        dir_stats = self._format_dir_stats(item)
        print(f"{prefix}{connector}{item.dir_name}/ {dir_stats}")
        # Calculate new prefix based on connector type
        is_last = connector == self.CONNECTOR_LAST
        new_prefix = prefix + self._get_prefix_extension(is_last)
        self._print_dir_recursively(item, level, new_prefix)

    def _print_file_item(self, item: File, connector: str, prefix: str, level: str, is_last: bool):
        """Print a single file item with stats and optionally its functions."""
        stats_str = self._format_file_stats(item)
        print(f"{prefix}{connector}{item.name} {stats_str}")

        if level == "function" and item.functions:
            self._print_functions(item.functions, prefix, is_last)

    def _print_dir_recursively(self, scan_dir: ScanDir, level: str, prefix: str = ""):
        """
        Recursively prints the directory structure, its files, and their KPIs.
        Directories containing only untracked files (ownership N/A) are not shown.
        """
        # Filter tracked files and visible directories
        files = [f for f in scan_dir.files.values() if self._is_tracked_file(f)]
        visible_dirs = self._get_visible_directories(scan_dir)

        # Sort and combine items
        items = sorted(visible_dirs, key=lambda d: d.dir_name) + sorted(files, key=lambda f: f.name)

        # Print each item with appropriate formatting
        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = self._get_connector(is_last)

            if isinstance(item, ScanDir):
                self._print_directory_item(item, connector, prefix, level)
            elif isinstance(item, File):
                self._print_file_item(item, connector, prefix, level, is_last)

    def _has_tracked_files(self, scan_dir: ScanDir) -> bool:
        """Returns True if this dir or any subdir contains a tracked file."""
        has_direct = any(self._is_tracked_file(f) for f in scan_dir.files.values())
        has_nested = any(self._has_tracked_files(d) for d in scan_dir.scan_dirs.values())
        return has_direct or has_nested

    def _get_connector(self, is_last: bool) -> str:
        """Get tree connector string based on position."""
        return self.CONNECTOR_LAST if is_last else self.CONNECTOR_CONTINUE

    def _get_prefix_extension(self, is_last: bool) -> str:
        """Get prefix extension based on position."""
        return self.PREFIX_LAST if is_last else self.PREFIX_CONTINUE

    def _get_kpi_value(self, kpis: dict, kpi_name: str) -> str:
        """
        Extract KPI value with proper None handling.

        Returns '?' if KPI is missing or value is None.
        This ensures consistent fallback behavior across all KPIs.
        """
        kpi = kpis.get(kpi_name)
        return kpi.value if kpi and kpi.value is not None else '?'

    def _extract_kpis(self, kpis: dict, include_cognitive: bool = True) -> Dict[str, str]:
        """
        Extract standard KPI values into a dictionary.

        Args:
            kpis: KPI dictionary to extract from
            include_cognitive: Include cognitive complexity (default: True)

        Returns:
            Dictionary with extracted KPI values
        """
        result = {
            'complexity': self._get_kpi_value(kpis, 'complexity'),
            'churn': self._get_kpi_value(kpis, 'churn'),
            'hotspot': self._get_kpi_value(kpis, 'hotspot')
        }

        if include_cognitive:
            result['cognitive'] = self._get_kpi_value(kpis, 'cognitive_complexity')

        return result

    def _has_valid_ownership_data(self, ownership_kpi) -> bool:
        """
        Check if ownership KPI contains valid data.

        Returns False for None, empty dict, or N/A format.
        Returns True for valid ownership dictionaries with author data.
        """
        # Check KPI exists and has value attribute
        if not ownership_kpi or not hasattr(ownership_kpi, 'value'):
            return False

        value = ownership_kpi.value

        # Check value is valid dict with content
        if not isinstance(value, dict) or not value:
            return False

        # Check for legacy N/A format
        return value.get('ownership') != 'N/A'

    def _format_author_list(self, authors_dict: dict, max_display: int = None) -> str:
        """
        Format author dictionary into readable list.

        Args:
            authors_dict: Dictionary of {author: percentage}
            max_display: Maximum authors to display (default: MAX_AUTHORS_DISPLAY)

        Returns:
            Formatted author list with percentages
        """
        if max_display is None:
            max_display = self.MAX_AUTHORS_DISPLAY

        sorted_authors = sorted(authors_dict.items(), key=lambda x: x[1], reverse=True)
        author_list = [f"{author} {percent}%" for author, percent in sorted_authors[:max_display]]

        remaining = len(sorted_authors) - max_display
        if remaining > 0:
            author_list.append(f"+ {remaining} more")

        return ", ".join(author_list)

    def _format_code_ownership(self, code_ownership_kpi) -> str:
        """
        Format code ownership KPI into readable string.

        Limits display to max 3 authors sorted by contribution percentage.
        Returns empty string if no valid ownership data.
        """
        if not self._has_valid_ownership_data(code_ownership_kpi):
            return ''

        value = code_ownership_kpi.value

        # Handle error cases
        if 'error' in value:
            return " Ownership: ERROR"

        # Format ownership with top contributors
        author_list = self._format_author_list(value)
        return f" Owners: {author_list}"

    def _format_shared_ownership(self, shared_ownership_kpi) -> str:
        """
        Format shared ownership KPI into readable string.

        Shows number of significant authors and their names.
        Returns empty string if no valid data.
        """
        # Validate KPI structure
        if not shared_ownership_kpi or not hasattr(shared_ownership_kpi, 'value'):
            return ''

        value = shared_ownership_kpi.value
        if not isinstance(value, dict):
            return ''

        # Check for special cases
        if 'error' in value:
            return " Shared: ERROR"
        if value.get('shared_ownership') == 'N/A':
            return " Shared: N/A"
        if 'num_significant_authors' not in value:
            return ''

        return self._format_shared_ownership_authors(value)

    def _format_shared_ownership_authors(self, value: dict) -> str:
        """Format author information from shared ownership value."""
        num_authors = value['num_significant_authors']
        authors = value.get('authors', [])
        threshold = value.get('threshold', 20.0)

        # Handle zero or single author cases
        if num_authors == 0:
            return f" Shared: None (threshold: {threshold}%)"
        if num_authors == 1:
            return f" Shared: Single owner ({authors[0]})"

        # Multiple authors - format with limit
        author_list = ", ".join(authors[:self.MAX_AUTHORS_DISPLAY])
        if len(authors) > self.MAX_AUTHORS_DISPLAY:
            author_list += "..."
        return f" Shared: {num_authors} authors ({author_list})"

    def _format_dir_stats(self, dir_obj: ScanDir) -> str:
        """
        Format average KPI statistics for a directory.

        Shows average values for all files in the directory tree.
        Returns empty string if no KPIs are available.
        """
        kpis = self._extract_kpis(dir_obj.kpis, include_cognitive=True)

        # Only show if at least one KPI is available
        if all(v == '?' for v in kpis.values()):
            return ""

        return (f"[Avg C:{kpis['complexity']}, Avg Cog:{kpis['cognitive']}, "
                f"Avg Churn:{kpis['churn']}, Avg Hotspot:{kpis['hotspot']}]")

    def _format_file_stats(self, file_obj: File) -> str:
        """Formats the KPI statistics string for a single file."""
        kpis = self._extract_kpis(file_obj.kpis, include_cognitive=True)
        base_stats = (f"[C:{kpis['complexity']}, Cog:{kpis['cognitive']}, "
                      f"Churn:{kpis['churn']}, Hotspot:{kpis['hotspot']}]")

        # Append ownership strings (they include leading space if non-empty)
        ownership_str = self._format_code_ownership(file_obj.kpis.get('Code Ownership'))
        shared_str = self._format_shared_ownership(file_obj.kpis.get('Shared Ownership'))

        return base_stats + ownership_str + shared_str

    def _print_functions(self, functions: List[Function], prefix: str, is_file_last: bool):
        """Prints the functions for a given file, including cognitive complexity if available."""
        func_prefix = prefix + self._get_prefix_extension(is_file_last)

        for i, func in enumerate(sorted(functions, key=lambda f: f.name)):
            is_last_func = (i == len(functions) - 1)
            connector = self._get_connector(is_last_func)

            kpis = self._extract_kpis(func.kpis, include_cognitive=True)
            stats_str = f"[C:{kpis['complexity']}, Cog:{kpis['cognitive']}]"
            print(f"{func_prefix}{connector}{func.name}() {stats_str}")
