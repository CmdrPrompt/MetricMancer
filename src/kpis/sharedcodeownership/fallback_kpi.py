"""
Fallback KPI for Shared Ownership when calculation fails.
Provides error handling and graceful degradation.
"""
from src.kpis.base_kpi import BaseKPI


class FallbackSharedOwnershipKPI(BaseKPI):
    """
    Fallback KPI used when SharedOwnershipKPI calculation fails.
    Returns error information instead of crashing the analysis.
    """

    def __init__(self, error_message: str):
        super().__init__(
            name="Shared Ownership",
            value={"error": f"Could not calculate: {error_message}"},
            description=("Number of significant authors per file "
                         "(ownership > threshold)")
        )

    def calculate(self, *args, **kwargs):
        """Returns the error value without attempting calculation."""
        return self.value
