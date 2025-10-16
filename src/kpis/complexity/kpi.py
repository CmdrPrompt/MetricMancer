from ..base_kpi import BaseKPI


class ComplexityKPI(BaseKPI):
    def __init__(self, value=None, calculation_values=None):
        super().__init__(
            name="complexity",
            value=value,
            unit="points",
            description="Cyclomatic complexity",
            calculation_values=calculation_values
        )

    def calculate(self, complexity: int, function_count: int, **kwargs):
        """
        Stores a pre-calculated complexity value.

        Args:
            complexity: The calculated complexity value.
            function_count: The calculated number of functions.
        """
        self.value = complexity
        self.calculation_values = {"function_count": function_count}
        return self
