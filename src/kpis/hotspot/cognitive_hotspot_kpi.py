from ..base_kpi import BaseKPI


class CognitiveHotspotKPI(BaseKPI):
    def __init__(self, value=None, calculation_values=None):
        super().__init__(
            name="cognitive_hotspot",
            value=value,
            unit="score",
            description="Cognitive Hotspot score (cognitive complexity × churn)",
            calculation_values=calculation_values
        )

    def calculate(self, cognitive_complexity=None, churn=None, **kwargs):
        # Calculate cognitive hotspot score
        if cognitive_complexity is not None and churn is not None:
            self.value = cognitive_complexity * churn
            self.calculation_values = {"cognitive_complexity": cognitive_complexity, "churn": churn}
        else:
            self.value = None
            self.calculation_values = {}
        return self
