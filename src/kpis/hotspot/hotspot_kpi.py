from ..base_kpi import BaseKPI


class HotspotKPI(BaseKPI):
    def __init__(self, value=None, calculation_values=None):
        super().__init__(
            name="hotspot",
            value=value,
            unit="score",
            description="Hotspot score (complexity × churn)",
            calculation_values=calculation_values
        )

    def calculate(self, complexity=None, churn=None, **kwargs):
        # Calculate hotspot score
        if complexity is not None and churn is not None:
            self.value = complexity * churn
            self.calculation_values = {"complexity": complexity, "churn": churn}
        else:
            self.value = None
            self.calculation_values = {}
        return self
