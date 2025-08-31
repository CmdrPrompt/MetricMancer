from .file_info import FileInfo
from .root_info import RootInfo
from .file_helpers import sort_files, average_complexity, average_grade
from ..metrics import grade
from typing import Any, Dict, List, Union


class ReportDataBuilder:
	def _build_root_info(self, language: str, root: str, files: List[Union[Dict[str, Any], 'FileInfo']]) -> RootInfo:
		files = self.sort_files(files)
		for f in files:
			if not f.grade:
				f.grade = grade(f.complexity, self.threshold_low, self.threshold_high)
		avg_grade = self.average_grade(files)
		return RootInfo(
			path=root,
			average=avg_grade['value'] if isinstance(avg_grade, dict) else avg_grade,
			files=files
		)

	def __init__(self, repo_info, threshold_low: float = 10.0, threshold_high: float = 20.0, problem_file_threshold: Union[float, None] = None):
		self.repo_info = repo_info
		self.results = repo_info.results
		self.threshold_low = threshold_low
		self.threshold_high = threshold_high
		self.problem_file_threshold = problem_file_threshold


	# Use shared helpers instead of duplicate methods

	def prepare_structured_data(self) -> List[Dict[str, Any]]:
		"""
		Returnerar strukturerad data för rapporten per språk och root.
		"""
		structured: List[Dict[str, Any]] = []
		for language in sorted(self.results):
			language_section = {'name': language, 'roots': []}
			for root in sorted(self.results[language]):
				root_info = self._build_root_info(language, root, self.results[language][root])
				language_section['roots'].append(root_info)
			structured.append(language_section)
		return structured
