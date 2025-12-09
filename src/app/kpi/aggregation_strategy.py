"""
Aggregation Strategy

Handles calculation of aggregated values from collections of KPI values.
Extracted from KPIAggregator to reduce complexity.
"""
from typing import Dict, Callable, Optional, List, Any
from src.utilities.debug import debug_print


class AggregationStrategy:
    """
    Calculates aggregated values using configurable strategies.
    
    Supports different aggregation methods:
    - Sum (default for additive metrics)
    - Max (for severity metrics)
    - Min (for threshold metrics)
    - Average (explicit calculation)
    - Custom functions
    
    Responsibilities:
    - Apply aggregation functions to value collections
    - Provide default aggregation behavior (average)
    - Handle edge cases and errors gracefully
    """
    
    def __init__(self, aggregation_functions: Optional[Dict[str, Callable]] = None):
        """
        Initialize AggregationStrategy.
        
        Args:
            aggregation_functions: Dictionary mapping KPI names to aggregation functions.
                                  Each function takes a list of values and returns aggregated value.
                                  Example: {"complexity": sum, "hotspot": max}
                                  If None or empty, uses average for all KPIs.
        """
        self.aggregation_functions = aggregation_functions if aggregation_functions is not None else {}
    
    def calculate_aggregated_value(self, kpi_name: str, values: List[Any]) -> Optional[float]:
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
                agg_value = self.aggregation_functions[kpi_name](values)
            else:
                # Default: calculate average
                agg_value = sum(values) / len(values)
            
            # Only round if agg_value is int or float
            if isinstance(agg_value, (int, float)):
                return round(agg_value, 1)
            else:
                return agg_value
        
        except (TypeError, ValueError) as e:
            debug_print(f"[AggregationStrategy] Error aggregating {kpi_name}: {e}")
            return None
    
    def aggregate_kpi_collections(self, kpi_values: Dict[str, List[Any]]) -> Dict[str, Any]:
        """
        Aggregate multiple KPI value collections.
        
        Args:
            kpi_values: Dictionary mapping KPI names to lists of values
            
        Returns:
            Dictionary mapping KPI names to aggregated values
        """
        result = {}
        
        for kpi_name, values in kpi_values.items():
            aggregated_value = self.calculate_aggregated_value(kpi_name, values)
            if aggregated_value is not None:
                result[kpi_name] = aggregated_value
        
        return result
