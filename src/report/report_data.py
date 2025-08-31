
from .file_info import FileInfo
from .root_info import RootInfo
from .report_data_collector import ReportDataCollector
from typing import Any, Dict, List, Union


class ReportDataBuilder:
	def __init__(self, repo_info, threshold_low: float = 10.0, threshold_high: float = 20.0, problem_file_threshold: Union[float, None] = None):
		self.repo_info = repo_info
		self.results = repo_info.results
		self.threshold_low = threshold_low
		self.threshold_high = threshold_high
		self.problem_file_threshold = problem_file_threshold

		self.collector = ReportDataCollector(repo_info, threshold_low, threshold_high)

	# Use shared helpers instead of duplicate methods

	def prepare_structured_data(self) -> List[Dict[str, Any]]:
		"""
		Returnerar strukturerad data för rapporten per språk och root.
		"""
		structured: List[Dict[str, Any]] = []
		for language in sorted(self.results):
			language_section = {'name': language, 'roots': []}
			for root in sorted(self.results[language]):
				root_info = self.collector.build_root_info(language, root, self.results[language][root])
				language_section['roots'].append(root_info)
			structured.append(language_section)
		return structured
