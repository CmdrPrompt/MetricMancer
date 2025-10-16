"""
KPIAggregator - Aggregates KPIs across directory hierarchy.

This class implements the Composite pattern to aggregate KPIs from individual
files up through the directory hierarchy. It supports different aggregation
strategies (sum, max, average, etc.) for different KPI types.

Part of the Analyzer refactoring (Phase 2).
Follows Single Responsibility Principle and Composite Pattern.
"""

from typing import Dict, Any, Callable, Optional, List
from utilities.debug import debug_print


class KPIAggregator:
    """
    Aggregates KPIs across directory hierarchy using Composite pattern.
    
    This class is responsible for:
    1. Aggregating file-level KPIs into directory-level KPIs
    2. Recursively aggregating subdirectory KPIs into parent directory KPIs
    3. Supporting different aggregation strategies per KPI type
    
    The aggregation follows a bottom-up approach:
    - Leaf nodes (files) provide base KPI values
    - Intermediate nodes (directories) aggregate from children
    - Root node contains total aggregated values
    
    Attributes:
        aggregation_functions: Dictionary mapping KPI names to aggregation functions
                              Default is sum for all KPIs
    
    Example:
        >>> aggregator = KPIAggregator()
        >>> result = aggregator.aggregate_directory(root_dir)
        >>> print(result["complexity"])
        150
    """
    
    def __init__(self, aggregation_functions: Optional[Dict[str, Callable]] = None):
        """
        Initialize KPIAggregator with aggregation strategies.
        
        Args:
            aggregation_functions: Dictionary mapping KPI names to aggregation functions.
                                  Each function takes a list of values and returns aggregated value.
                                  Example: {"complexity": sum, "hotspot": max}
                                  If None, uses sum for all KPIs.
        """
        self.aggregation_functions = aggregation_functions if aggregation_functions is not None else {}
    
    def aggregate_file(self, file_obj: Any) -> Dict[str, Any]:
        """
        Aggregate KPIs from a file object.
        
        This is the base case for aggregation - extracts KPI values from a file.
        
        Args:
            file_obj: File object with kpis dictionary
        
        Returns:
            Dictionary mapping KPI names to their values
            
        Example:
            >>> file = File(name="main.py", kpis={"complexity": KPI(value=10)})
            >>> result = aggregator.aggregate_file(file)
            >>> print(result["complexity"])
            10
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
                if kpi_obj is not None:
                    # Try to get value attribute
                    value = getattr(kpi_obj, 'value', None)
                    if value is not None:
                        result[kpi_name] = value
            
            debug_print(f"[KPIAggregator] Aggregated file {getattr(file_obj, 'name', 'unknown')}: {result}")
            return result
            
        except Exception as e:
            debug_print(f"[KPIAggregator] Error aggregating file: {e}")
            return result
    
    def aggregate_directory(self, directory_obj: Any) -> Dict[str, Any]:
        """
        Aggregate KPIs for a directory and all its children (Composite pattern).
        
        This method:
        1. Recursively aggregates KPIs from all subdirectories
        2. Aggregates KPIs from all files in this directory
        3. Combines all values using aggregation functions
        4. Updates the directory's kpis dictionary with aggregated values
        
        Args:
            directory_obj: Directory object with files, children, and kpis attributes
        
        Returns:
            Dictionary mapping KPI names to aggregated values
            
        Example:
            >>> root = Directory(name="src")
            >>> result = aggregator.aggregate_directory(root)
            >>> print(result["complexity"])
            150
        """
        try:
            # Dictionary to collect all KPI values by name
            kpi_values: Dict[str, List[Any]] = {}
            
            # 1. Recursively aggregate subdirectories (Composite pattern)
            children = getattr(directory_obj, 'children', [])
            if children:
                debug_print(f"[KPIAggregator] Aggregating {len(children)} subdirectories")
                for child in children:
                    child_kpis = self.aggregate_directory(child)
                    
                    # Collect values from child
                    for kpi_name, kpi_value in child_kpis.items():
                        if kpi_name not in kpi_values:
                            kpi_values[kpi_name] = []
                        kpi_values[kpi_name].append(kpi_value)
            
            # 2. Aggregate files in this directory
            files = getattr(directory_obj, 'files', [])
            if files:
                debug_print(f"[KPIAggregator] Aggregating {len(files)} files")
                for file_obj in files:
                    file_kpis = self.aggregate_file(file_obj)
                    
                    # Collect values from file
                    for kpi_name, kpi_value in file_kpis.items():
                        if kpi_name not in kpi_values:
                            kpi_values[kpi_name] = []
                        kpi_values[kpi_name].append(kpi_value)
            
            # 3. Apply aggregation functions
            result = {}
            for kpi_name, values in kpi_values.items():
                if not values:
                    continue
                
                # Get aggregation function for this KPI (default: sum)
                agg_func = self.aggregation_functions.get(kpi_name, sum)
                
                try:
                    aggregated_value = agg_func(values)
                    result[kpi_name] = aggregated_value
                except (TypeError, ValueError) as e:
                    debug_print(f"[KPIAggregator] Error aggregating {kpi_name}: {e}")
                    # Skip this KPI on error
                    continue
            
            # 4. Update directory's kpis dictionary with aggregated values
            if hasattr(directory_obj, 'kpis'):
                for kpi_name, agg_value in result.items():
                    # Create mock KPI object with aggregated value
                    class AggregatedKPI:
                        def __init__(self, name, value):
                            self.name = name
                            self.value = value
                    
                    directory_obj.kpis[kpi_name] = AggregatedKPI(kpi_name, agg_value)
            
            dir_name = getattr(directory_obj, 'name', 'unknown')
            debug_print(f"[KPIAggregator] Aggregated directory {dir_name}: {result}")
            
            return result
            
        except Exception as e:
            debug_print(f"[KPIAggregator] Error aggregating directory: {e}")
            return {}
