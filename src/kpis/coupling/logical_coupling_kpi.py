"""
Logical Coupling KPI - Measures temporal coupling for a file.

This KPI identifies files that frequently change together with the target file,
revealing hidden architectural dependencies.

Based on Adam Tornhill's methodology from "Your Code as a Crime Scene".
"""

from typing import List, Tuple, Optional
from src.kpis.base_kpi import BaseKPI


class LogicalCouplingKPI(BaseKPI):
    """
    Logical Coupling KPI - measures temporal coupling for a file.

    Reports the number of files with strong coupling (>= 50% co-change rate)
    and provides detailed coupling metrics.

    Attributes:
        value: Count of strongly coupled files (>= 0.5 threshold)
        unit: "coupled_files"
        calculation_values: Dictionary containing:
            - coupled_files: List of (file, coupling_score) tuples
            - max_coupling: Maximum coupling score
            - avg_coupling: Average coupling score

    Example:
        >>> kpi = LogicalCouplingKPI()
        >>> kpi.calculate(
        ...     file_path="src/file.py",
        ...     repo_root="/repo",
        ...     coupling_data=[("src/other.py", 0.75), ("src/another.py", 0.45)]
        ... )
        >>> print(kpi.value)  # 1 (only 0.75 >= 0.5)
        >>> print(kpi.calculation_values["max_coupling"])  # 0.75
    """

    STRONG_COUPLING_THRESHOLD = 0.5  # 50% co-change rate

    def __init__(self, value: Optional[int] = None, calculation_values: Optional[dict] = None):
        """
        Initialize LogicalCouplingKPI.

        Args:
            value: Optional pre-calculated coupling count
            calculation_values: Optional pre-calculated values dictionary
        """
        super().__init__(
            name="logical_coupling",
            value=value,
            unit="coupled_files",
            description="Number of files with strong coupling (>50%)",
            calculation_values=calculation_values
        )

    def calculate(
        self,
        file_path: str,
        repo_root: str,
        coupling_data: Optional[List[Tuple[str, float]]] = None,
        **kwargs
    ) -> 'LogicalCouplingKPI':
        """
        Calculate logical coupling metrics for a file.

        Args:
            file_path: Path to the file being analyzed
            repo_root: Root directory of the git repository
            coupling_data: List of (coupled_file, coupling_score) tuples
                          where coupling_score is between 0.0 and 1.0
            **kwargs: Additional arguments (ignored for extensibility)

        Returns:
            self: Allows method chaining

        Calculation:
            1. Count files with coupling_score >= 0.5
            2. Calculate maximum and average coupling scores
            3. Store all coupling data and metrics
        """
        # Handle None or empty coupling data
        if not coupling_data:
            coupling_data = []

        # Store all coupling data
        self.calculation_values["coupled_files"] = coupling_data

        # Calculate max and average coupling
        if coupling_data:
            scores = [score for _, score in coupling_data]
            self.calculation_values["max_coupling"] = max(scores)
            self.calculation_values["avg_coupling"] = sum(scores) / len(scores)
        else:
            self.calculation_values["max_coupling"] = 0.0
            self.calculation_values["avg_coupling"] = 0.0

        # Count strongly coupled files (>= threshold)
        strong_couplings = sum(
            1 for _, score in coupling_data
            if score >= self.STRONG_COUPLING_THRESHOLD
        )
        self.value = strong_couplings

        return self
