"""
Fallback KPI for Code Ownership when calculation fails.
Provides error handling and graceful degradation.
"""
from src.kpis.base_kpi import BaseKPI


class FallbackCodeOwnershipKPI(BaseKPI):
    """
    Fallback KPI used when CodeOwnershipKPI calculation fails.
    Returns error information instead of crashing the analysis.
    """

    def __init__(self, error_message: str):
        super().__init__(
            name="Code Ownership",
            value={"error": f"Could not calculate: {error_message}"},
            description=("Proportion of code lines owned by each author "
                         "(via git blame)")
        )

    def calculate(self, *args, **kwargs):
        """Returns the error value without attempting calculation."""
        return self.value
