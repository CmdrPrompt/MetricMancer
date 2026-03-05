"""
Change-Coupled Hotspot KPI - Combines complexity, churn, and temporal coupling.

This KPI creates a risk score by multiplying complexity, churn, and coupling metrics,
revealing files that are complex, frequently changing, AND coupled to other files.

Formula:
    coupled_hotspot = base_hotspot × max_coupling × coupling_multiplier
    where:
    - base_hotspot = complexity × churn
    - max_coupling = highest coupling score to any file (0.0-1.0)
    - coupling_multiplier = 1 + (num_strong_couplings × 0.1)

This exponential scoring ensures that coupled hotspots have much higher risk than
isolated hotspots, as changes propagate through the coupled files.

Based on Adam Tornhill's methodology from "Your Code as a Crime Scene".
"""

from typing import List, Tuple, Optional
from src.kpis.base_kpi import BaseKPI


class ChangeCoupledHotspotKPI(BaseKPI):
    """
    Change-Coupled Hotspot KPI - combines complexity, churn, and coupling.

    Risk Levels:
        CRITICAL  (>= 1000): Immediate action required
        VERY_HIGH (>= 500):  High priority refactoring
        HIGH      (>= 200):  Significant risk
        MEDIUM    (>= 100):  Monitor closely
        LOW       (< 100):   Acceptable

    Attributes:
        value: Coupled hotspot score
        unit: "score"
        calculation_values: Dictionary containing:
            - base_hotspot: complexity × churn
            - max_coupling: Highest coupling score
            - num_strong_couplings: Count of files with >= 0.5 coupling
            - coupling_multiplier: 1 + (num_strong_couplings × 0.1)

    Example:
        >>> kpi = ChangeCoupledHotspotKPI()
        >>> kpi.calculate(
        ...     file_path="src/file.py",
        ...     repo_root="/repo",
        ...     complexity=20,
        ...     churn=10,
        ...     coupling_data=[("src/a.py", 0.85), ("src/b.py", 0.65)]
        ... )
        >>> print(kpi.value)  # 221.2 (20*10 * 0.85 * 1.2)
        >>> print(kpi.get_risk_level(kpi.value))  # "HIGH"
    """

    STRONG_COUPLING_THRESHOLD = 0.5  # 50% co-change rate

    # Risk level thresholds
    RISK_LEVELS = {
        1000: "CRITICAL",
        500: "VERY_HIGH",
        200: "HIGH",
        100: "MEDIUM",
        0: "LOW"
    }

    def __init__(self, value: Optional[float] = None, calculation_values: Optional[dict] = None):
        """
        Initialize ChangeCoupledHotspotKPI.

        Args:
            value: Optional pre-calculated hotspot score
            calculation_values: Optional pre-calculated values dictionary
        """
        super().__init__(
            name="change_coupled_hotspot",
            value=value,
            unit="score",
            description="Coupled hotspot score (complexity × churn × coupling)",
            calculation_values=calculation_values
        )

    def calculate(
        self,
        file_path: str,
        repo_root: str,
        complexity: Optional[float] = None,
        churn: Optional[float] = None,
        coupling_data: Optional[List[Tuple[str, float]]] = None,
        **kwargs
    ) -> 'ChangeCoupledHotspotKPI':
        """
        Calculate change-coupled hotspot score.

        Args:
            file_path: Path to the file being analyzed
            repo_root: Root directory of the git repository
            complexity: Cyclomatic complexity of the file
            churn: Number of commits that modified the file (or churn metric)
            coupling_data: List of (coupled_file, coupling_score) tuples
                          where coupling_score is between 0.0 and 1.0
            **kwargs: Additional arguments (ignored for extensibility)

        Returns:
            self: Allows method chaining

        Calculation Steps:
            1. base_hotspot = complexity × churn
            2. max_coupling = maximum coupling_score from all files
            3. num_strong_couplings = count of files with coupling_score >= 0.5
            4. coupling_multiplier = 1 + (num_strong_couplings × 0.1)
            5. coupled_hotspot = base_hotspot × max_coupling × coupling_multiplier
        """
        # Handle None values
        complexity = complexity or 0
        churn = churn or 0
        if not coupling_data:
            coupling_data = []

        # Step 1: Calculate base hotspot (complexity × churn)
        base_hotspot = complexity * churn
        self.calculation_values["base_hotspot"] = base_hotspot

        # Step 2: Get maximum coupling score
        if coupling_data:
            coupling_scores = [score for _, score in coupling_data]
            max_coupling = max(coupling_scores)
        else:
            max_coupling = 0.0
        self.calculation_values["max_coupling"] = max_coupling

        # Step 3: Count strongly coupled files
        num_strong_couplings = sum(
            1 for _, score in coupling_data
            if score >= self.STRONG_COUPLING_THRESHOLD
        )
        self.calculation_values["num_strong_couplings"] = num_strong_couplings

        # Step 4: Calculate coupling multiplier
        coupling_multiplier = 1.0 + (num_strong_couplings * 0.1)
        self.calculation_values["coupling_multiplier"] = coupling_multiplier

        # Step 5: Calculate final coupled hotspot score
        # Formula: base_hotspot × max_coupling × coupling_multiplier
        # When there's no coupling (max_coupling = 0), return base_hotspot
        # When coupled, apply full multiplier formula
        if max_coupling > 0:
            self.value = base_hotspot * max_coupling * coupling_multiplier
        else:
            # No coupling detected, return just the base hotspot
            self.value = base_hotspot

        return self

    @staticmethod
    def get_risk_level(score: float) -> str:
        """
        Categorize coupled hotspot risk based on score.

        Args:
            score: Coupled hotspot score

        Returns:
            Risk level: "CRITICAL", "VERY_HIGH", "HIGH", "MEDIUM", or "LOW"

        Risk Thresholds:
            >= 1000: CRITICAL - Immediate action required
            >= 500:  VERY_HIGH - High priority refactoring
            >= 200:  HIGH - Significant risk
            >= 100:  MEDIUM - Monitor closely
            < 100:   LOW - Acceptable
        """
        for threshold in sorted(ChangeCoupledHotspotKPI.RISK_LEVELS.keys(), reverse=True):
            if score >= threshold:
                return ChangeCoupledHotspotKPI.RISK_LEVELS[threshold]
        return "LOW"
