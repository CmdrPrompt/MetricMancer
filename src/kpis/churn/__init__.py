from ..base import KPI

class ChurnKPI(KPI):
	def __init__(self, value=None, meta=None):
		super().__init__(
			name="churn",
			value=value,
			unit=None,
			description="Code churn (antal commits/ändringar)",
			meta=meta
		)

	def calculate(self, commit_history=None, **kwargs):
		# Placeholder: sätt value till 5 och meta till antal commits
		self.value = 5
		self.meta = {"commit_count": 5}
		return self
