from ..base_kpi import BaseKPI
import os

class ChurnKPI(BaseKPI):
	def __init__(self, value=None, calculation_values=None):
		super().__init__(
			name="churn",
			value=value,
			unit="lines changed",
			description="Code churn (number of commits/changes)",
			calculation_values=calculation_values
		)

	def calculate(self, file_path: str, churn_data: dict, **kwargs):
		"""
		Retrieves code churn for a single file from a precomputed data set.

		Args:
			file_path (str): Absolute path to the file whose churn value should be retrieved.
			churn_data (dict): A dictionary where the key is an absolute file path
							   and the value is its churn value.
		"""
		self.value = churn_data.get(os.path.abspath(file_path), 0)
		# calculation_values can be extended with e.g. number of commits if needed
		self.calculation_values = {}
		return self