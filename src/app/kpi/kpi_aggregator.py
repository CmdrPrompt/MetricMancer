"""
KPIAggregator - Aggregates KPIs across directory hierarchy.

This class implements the Composite pattern to aggregate KPIs from individual
files up through the directory hierarchy. It supports different aggregation
strategies (sum, max, average, etc.) for different KPI types.

Follows Single Responsibility Principle and Composite Pattern.

ARCHITECTURE ALIGNMENT:
- Part of Application Layer (src/app/)
- Flat structure (no subpackages)
- Single Responsibility (only KPI aggregation)
- Uses Composite pattern for recursive aggregation
- Coordinates with existing components (KPICalculator, FileAnalyzer, HierarchyBuilder)

REFACTORED:
- Extracted DirectoryObjectAccessor for directory object access
- Extracted KPIValueCollector for value collection
- Extracted AggregationStrategy for aggregation logic
"""

from typing import Dict, Any, Callable, Optional
from src.utilities.debug import debug_print
from src.app.kpi.directory_accessor import DirectoryObjectAccessor
from src.app.kpi.kpi_value_collector import KPIValueCollector
from src.app.kpi.aggregation_strategy import AggregationStrategy


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
        self.directory_accessor = DirectoryObjectAccessor()
        self.value_collector = KPIValueCollector(self.directory_accessor)
        self.aggregation_strategy = AggregationStrategy(aggregation_functions)



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

        Delegates to KPIValueCollector for extraction.

        Args:
            file_obj: File object with kpis dictionary (from FileAnalyzer)

        Returns:
            Dictionary mapping KPI names to their values
        """
        return self.value_collector.extract_file_kpis(file_obj)

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
            kpi_values: Dict[str, Any] = {}

            # 1. Recursively aggregate subdirectories (Composite pattern)
            subdirs = self.directory_accessor.get_subdirectories(directory_obj)
            if subdirs:
                debug_print(f"[KPIAggregator] Aggregating {len(subdirs)} subdirectories")
                for subdir in subdirs:
                    # Recursively aggregate subdirectories
                    self.aggregate_directory(subdir)

            # 2. Collect KPI values from all files in tree (recursive)
            self.value_collector.collect_from_directory_tree(directory_obj, kpi_values)

            # 3. Calculate aggregated values using strategy
            result = self.aggregation_strategy.aggregate_kpi_collections(kpi_values)

            # 4. Update directory's kpis dictionary with aggregated values
            self._update_directory_kpis(directory_obj, result)

            dir_name = self.directory_accessor.get_name(directory_obj)
            debug_print(f"[KPIAggregator] Aggregated directory {dir_name}: {result}")

            return result

        except Exception as e:
            debug_print(f"[KPIAggregator] Error aggregating directory: {e}")
            return {}


