from ..base_kpi import BaseKPI

class ChurnKPI(BaseKPI):
    def __init__(self, value=None, calculation_values=None):
        super().__init__(
            name="churn",
            value=value,
            unit="commits",
            description="Number of commits affecting the file",
            calculation_values=calculation_values
        )

    def calculate(self, file_path: str, churn_data: dict, **kwargs):
        """
        Looks up a pre-calculated churn value from a dictionary.
        """
        self.value = churn_data.get(file_path, 0)
        return self