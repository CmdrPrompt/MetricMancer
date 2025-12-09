"""
KPIAggregator - Aggregates KPIs across directory hierarchy.

This class implements the Composite pattern to aggregate KPIs from individual
files up through the directory hierarchy. It supports different aggregation
strategies (sum, max, average, etc.) for different KPI types.

Phase 4 of the Analyzer refactoring.
Follows Single Responsibility Principle and Composite Pattern.
Extracted from analyzer.py (lines 241-310) to reduce complexity.

ARCHITECTURE ALIGNMENT:
- Part of Application Layer (src/app/)
- Flat structure (no subpackages)
- Single Responsibility (only KPI aggregation)
- Uses Composite pattern for recursive aggregation
- Coordinates with existing components (KPICalculator, FileAnalyzer, HierarchyBuilder)
"""

from typing import Dict, Any, Callable, Optional, List
from src.utilities.debug import debug_print


class AggregatedKPI:
    """Lightweight KPI object for aggregated values."""

    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value


class KPIAggregator:
    """
    Aggregates KPIs across directory hierarchy using Composite pattern.

    This class is responsible for:
    1. Aggregating file-level KPIs into directory-level KPIs
    2. Recursively aggregating subdirectory KPIs into parent directory KPIs
    3. Supporting different aggregation strategies per KPI type

    The aggregation follows a bottom-up approach:
    - Leaf nodes (files) provide base KPI values (from FileAnalyzer)
    - Intermediate nodes (directories) aggregate from children
    - Root node contains total aggregated values

    Integrates with Phase 1-3 components:
    - FileAnalyzer: Produces File objects with KPIs
    - HierarchyBuilder: Creates directory structure to aggregate
    - KPICalculator: Calculates individual file KPIs (used by FileAnalyzer)

    Attributes:
        aggregation_functions: Dictionary mapping KPI names to aggregation functions
                              Default is sum for all KPIs (complexity, churn, hotspot)

    Example:
        >>> aggregator = KPIAggregator()
        >>> # After FileAnalyzer and HierarchyBuilder have processed files
        >>> result = aggregator.aggregate_directory(root_scan_dir)
        >>> print(result["complexity"])  # Total complexity across all files
        150

    Test Coverage:
        - test_kpi_aggregator.py provides comprehensive tests
        - TDD approach: tests written before implementation
    """

    def __init__(self, aggregation_functions: Optional[Dict[str, Callable]] = None):
        """
        Initialize KPIAggregator with aggregation strategies.

        Args:
            aggregation_functions: Dictionary mapping KPI names to aggregation functions.
                                  Each function takes a list of values and returns aggregated value.
                                  Example: {"complexity": sum, "hotspot": max}
                                  If None, uses sum for all KPIs.

        Design Note:
            Strategy pattern for aggregation allows flexibility:
            - Sum for additive metrics (complexity, lines of code)
            - Max for severity metrics (hotspot score)
            - Average for normalized metrics (ownership percentage)
        """
        self.aggregation_functions = aggregation_functions if aggregation_functions is not None else {}

    def _get_subdirectories(self, directory_obj: Any) -> List[Any]:
        """
        Extract subdirectories from a directory object.

        Handles both new 'scan_dirs' (dict) and old 'children' (list) formats.

        Args:
            directory_obj: Directory object to extract subdirectories from

        Returns:
            List of subdirectory objects
        """
        # Try new format first (scan_dirs dict)
        scan_dirs = getattr(directory_obj, 'scan_dirs', None)
        if scan_dirs and isinstance(scan_dirs, dict):
            return list(scan_dirs.values())

        # Fall back to old format (children list)
        children = getattr(directory_obj, 'children', None)
        if children:
            return list(children)

        return []

    def _get_files_from_directory(self, directory_obj: Any) -> List[Any]:
        """
        Extract files from a directory object.

        Handles both dict and list formats for files attribute.

        Args:
            directory_obj: Directory object to extract files from

        Returns:
            List of file objects
        """
        files = getattr(directory_obj, 'files', None)
        if files is None:
            return []

        # Handle dict format
        if isinstance(files, dict):
            return list(files.values())

        # Handle list format
        if isinstance(files, list):
            return list(files)

        return []

    def _calculate_aggregated_value(self, kpi_name: str, values: List[Any]) -> Optional[float]:
        """
        Calculate aggregated value for a KPI.

        Uses custom aggregation function if provided, otherwise calculates average.

        Args:
            kpi_name: Name of the KPI to aggregate
            values: List of values to aggregate

        Returns:
            Aggregated value, or None if values is empty
        """
        if not values:
            return None

        try:
            # Use custom aggregation function if provided
            if kpi_name in self.aggregation_functions:
                return self.aggregation_functions[kpi_name](values)

            # Default: calculate average
            avg_value = sum(values) / len(values)
            return round(avg_value, 1)

        except (TypeError, ValueError) as e:
            debug_print(f"[KPIAggregator] Error aggregating {kpi_name}: {e}")
            return None

    def _get_directory_name(self, directory_obj: Any) -> str:
        """
        Extract directory name from directory object.

        Tries 'dir_name' first, then 'name', with 'unknown' as fallback.

        Args:
            directory_obj: Directory object to extract name from

        Returns:
            Directory name string
        """
        return getattr(directory_obj, 'dir_name', getattr(directory_obj, 'name', 'unknown'))

    def _add_kpi_value(self, kpi_values: Dict[str, List[Any]], kpi_name: str, kpi_value: Any) -> None:
        """
        Add a KPI value to the collection dictionary.

        Initializes the list if the KPI name doesn't exist yet.

        Args:
            kpi_values: Dictionary to collect KPI values
            kpi_name: Name of the KPI
            kpi_value: Value to add
        """
        if kpi_name not in kpi_values:
            kpi_values[kpi_name] = []
        kpi_values[kpi_name].append(kpi_value)

    def _update_directory_kpis(self, directory_obj: Any, aggregated_values: Dict[str, Any]) -> None:
        """
        Update directory's kpis dictionary with aggregated values.

        Args:
            directory_obj: Directory object to update
            aggregated_values: Dictionary of KPI names to aggregated values
        """
        if not hasattr(directory_obj, 'kpis'):
            return

        for kpi_name, agg_value in aggregated_values.items():
            directory_obj.kpis[kpi_name] = AggregatedKPI(kpi_name, agg_value)

    def aggregate_file(self, file_obj: Any) -> Dict[str, Any]:
        """
        Aggregate KPIs from a file object.

        This is the base case for aggregation - extracts KPI values from a File object
        produced by FileAnalyzer (Phase 2).

        Args:
            file_obj: File object with kpis dictionary (from FileAnalyzer)

        Returns:
            Dictionary mapping KPI names to their values

        Example:
            >>> # File created by FileAnalyzer
            >>> file = File(name="main.py", kpis={"complexity": ComplexityKPI(value=10)})
            >>> result = aggregator.aggregate_file(file)
            >>> print(result["complexity"])
            10

        Error Handling:
            - Returns empty dict if file_obj is None
            - Returns empty dict if file has no kpis attribute
            - Skips KPIs with no value attribute
        """
        result = {}

        try:
            if file_obj is None:
                return result

            kpis = getattr(file_obj, 'kpis', None)
            if kpis is None:
                return result

            # Extract values from KPI objects
            # KPI objects come from KPICalculator strategies
            for kpi_name, kpi_obj in kpis.items():
                if kpi_obj is None:
                    continue

                value = getattr(kpi_obj, 'value', None)
                if value is not None:
                    result[kpi_name] = value

            debug_print(f"[KPIAggregator] Aggregated file {getattr(file_obj, 'name', 'unknown')}: {result}")
            return result

        except Exception as e:
            debug_print(f"[KPIAggregator] Error aggregating file: {e}")
            return result

    def _count_files_in_tree(self, directory_obj: Any) -> int:
        """
        Count total number of files in directory tree.

        Args:
            directory_obj: ScanDir object to count files from

        Returns:
            Total number of files in tree
        """
        # Count files in this directory
        count = len(self._get_files_from_directory(directory_obj))

        # Recursively count files in subdirectories
        for subdir in self._get_subdirectories(directory_obj):
            count += self._count_files_in_tree(subdir)

        return count

    def aggregate_directory(self, directory_obj: Any) -> Dict[str, Any]:
        """
        Aggregate KPIs for a directory and all its children (Composite pattern).

        This method implements recursive aggregation following the Composite pattern:
        1. Recursively aggregates KPIs from all subdirectories
        2. Aggregates KPIs from all files in this directory
        3. Calculates averages across all files in the tree
        4. Updates the directory's kpis dictionary with aggregated values

        Integrates with HierarchyBuilder (Phase 3):
        - Expects ScanDir objects with scan_dirs (dict) and files (dict) attributes
        - Recursively processes entire tree structure
        - Updates KPIs in-place for each directory node

        Args:
            directory_obj: ScanDir object with files, scan_dirs, and kpis attributes
                          (created by HierarchyBuilder)

        Returns:
            Dictionary mapping KPI names to average values

        Example:
            >>> # Directory structure built by HierarchyBuilder
            >>> root = ScanDir(name="src")
            >>> # After FileAnalyzer has processed all files
            >>> result = aggregator.aggregate_directory(root)
            >>> print(result["complexity"])  # Average complexity across all files
            15.5
            >>> # root.kpis now contains aggregated values

        Algorithm:
            1. Collect KPI values from subdirectories (recursive)
            2. Collect KPI values from files (base case)
            3. Calculate average for each KPI type
            4. Update directory object with aggregated KPIs

        Performance:
            - O(n) where n is total number of files and directories
            - Single pass through tree structure
            - Memory efficient: processes one level at a time
        """
        try:
            # Dictionary to collect all KPI values by name
            kpi_values: Dict[str, List[Any]] = {}

            # 1. Recursively aggregate subdirectories (Composite pattern)
            subdirs = self._get_subdirectories(directory_obj)
            if subdirs:
                debug_print(f"[KPIAggregator] Aggregating {len(subdirs)} subdirectories")
                for subdir in subdirs:
                    # Recursively aggregate subdirectories
                    self.aggregate_directory(subdir)

            # 2. Collect KPI values from all files in tree (recursive)
            self._collect_file_kpis(directory_obj, kpi_values)

            # 3. Calculate aggregated values
            result = {}
            for kpi_name, values in kpi_values.items():
                aggregated_value = self._calculate_aggregated_value(kpi_name, values)
                if aggregated_value is not None:
                    result[kpi_name] = aggregated_value

            # 4. Update directory's kpis dictionary with aggregated values
            self._update_directory_kpis(directory_obj, result)

            dir_name = self._get_directory_name(directory_obj)
            debug_print(f"[KPIAggregator] Aggregated directory {dir_name}: {result}")

            return result

        except Exception as e:
            debug_print(f"[KPIAggregator] Error aggregating directory: {e}")
            return {}

    def _collect_file_kpis(self, directory_obj: Any, kpi_values: Dict[str, List[Any]]) -> None:
        """
        Recursively collect KPI values from all files in directory tree.

        Args:
            directory_obj: ScanDir object to collect from
            kpi_values: Dictionary to accumulate KPI values (modified in place)
        """
        # Collect from files in this directory
        for file_obj in self._get_files_from_directory(directory_obj):
            file_kpis = self.aggregate_file(file_obj)
            for kpi_name, kpi_value in file_kpis.items():
                self._add_kpi_value(kpi_values, kpi_name, kpi_value)

        # Recursively collect from subdirectories
        for subdir in self._get_subdirectories(directory_obj):
            self._collect_file_kpis(subdir, kpi_values)
