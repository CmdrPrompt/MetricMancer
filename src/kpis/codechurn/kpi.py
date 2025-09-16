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
        Looks up a pre-calculated churn value from a dictionary, robust to absolute/relative path mismatches and filename-only matches.
        """
        import os
        abs_path = os.path.normcase(os.path.normpath(os.path.abspath(file_path)))
        # Try absolute path match
        for key in churn_data:
            norm_key = os.path.normcase(os.path.normpath(key))
            if abs_path == norm_key:
                self.value = churn_data[key]
                break
        else:
            # Try filename match if absolute path fails
            file_name = os.path.basename(file_path)
            for key in churn_data:
                if os.path.basename(key) == file_name:
                    self.value = churn_data[key]
                    break
            else:
                self.value = 0
        return self