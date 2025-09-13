from .base import KPI

class HotspotKPI(KPI):
    def __init__(self, complexity=None, churn=None, value=None, meta=None):
        super().__init__(
            name="hotspot",
            value=value,
            unit=None,
            description="Hotspot score (complexity × churn)",
            meta=meta
        )
        self.complexity = complexity
        self.churn = churn

    def calculate(self, complexity=None, churn=None, **kwargs):
        # Beräkna hotspot-score
        c = complexity if complexity is not None else self.complexity
        h = churn if churn is not None else self.churn
        if c is not None and h is not None:
            self.value = c * h
            self.meta = {"complexity": c, "churn": h}
        else:
            self.value = None
            self.meta = {}
        return self
