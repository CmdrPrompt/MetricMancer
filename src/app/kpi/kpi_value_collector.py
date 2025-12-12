"""
KPI Value Collector

Collects KPI values from files and aggregates them.
Extracted from KPIAggregator to reduce complexity.
"""
from typing import Dict, Any, List
from src.utilities.debug import debug_print


class KPIValueCollector:
    """
    Collects KPI values from file and directory objects.

    Responsibilities:
    - Extract KPI values from file objects
    - Accumulate KPI values into collections
    - Recursively traverse directory trees to collect all KPI values
    """

    def __init__(self, directory_accessor):
        """
        Initialize KPIValueCollector.

        Args:
            directory_accessor: Accessor for extracting data from directory objects
        """
        self.directory_accessor = directory_accessor

    def extract_file_kpis(self, file_obj: Any) -> Dict[str, Any]:
        """
        Extract KPI values from a file object.

        This is the base case for aggregation - extracts KPI values from a File object
        produced by FileAnalyzer.

        Args:
            file_obj: File object with kpis dictionary (from FileAnalyzer)

        Returns:
            Dictionary mapping KPI names to their values

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
            for kpi_name, kpi_obj in kpis.items():
                if kpi_obj is None:
                    continue

                value = getattr(kpi_obj, 'value', None)
                if value is not None:
                    result[kpi_name] = value

            debug_print(f"[KPIValueCollector] Extracted from file {getattr(file_obj, 'name', 'unknown')}: {result}")
            return result

        except Exception as e:
            debug_print(f"[KPIValueCollector] Error extracting file KPIs: {e}")
            return result

    def collect_from_directory_tree(self, directory_obj: Any, kpi_values: Dict[str, List[Any]]) -> None:
        """
        Recursively collect KPI values from all files in directory tree.

        Args:
            directory_obj: ScanDir object to collect from
            kpi_values: Dictionary to accumulate KPI values (modified in place)
        """
        # Collect from files in this directory
        for file_obj in self.directory_accessor.get_files(directory_obj):
            file_kpis = self.extract_file_kpis(file_obj)
            for kpi_name, kpi_value in file_kpis.items():
                self._add_kpi_value(kpi_values, kpi_name, kpi_value)

        # Recursively collect from subdirectories
        for subdir in self.directory_accessor.get_subdirectories(directory_obj):
            self.collect_from_directory_tree(subdir, kpi_values)

    @staticmethod
    def _add_kpi_value(kpi_values: Dict[str, List[Any]], kpi_name: str, kpi_value: Any) -> None:
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
