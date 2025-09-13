from .base import KPI

class ComplexityKPI(KPI):
    def __init__(self, value=None, meta=None):
        super().__init__(
            name="complexity",
            value=value,
            unit=None,
            description="Cyclomatic complexity",
            meta=meta
        )

    def calculate(self, file_content=None, **kwargs):
        # Här kan du implementera faktisk komplexitetsberäkning
        # Placeholder: sätt value till 7 och meta till antal funktioner
        self.value = 7
        self.meta = {"function_count": 3}
        return self
