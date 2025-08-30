from .file_info import FileInfo
from .root_info import RootInfo

from ..metrics import grade

from typing import Any, Dict, List, Union

class ReportDataBuilder:
	def _build_root_info(self, language: str, root: str, files: List[Union[Dict[str, Any], 'FileInfo']]) -> RootInfo:
		"""
		Returnerar RootInfo för en given root och dess filer.
		"""
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
	"""
	Bygger och filtrerar data för komplexitetsrapporten.
	"""
	def __init__(self, results: Dict[str, Dict[str, List[Dict[str, Any]]]], threshold_low: float = 10.0, threshold_high: float = 20.0, problem_file_threshold: Union[float, None] = None):
		"""
		:param results: Resultatstruktur {språk: {root: [fil-dictar]}}
		:param threshold_low: Gräns för låg komplexitet
		:param threshold_high: Gräns för hög komplexitet
		:param problem_file_threshold: Gräns för problemfilers komplexitet
		"""
		self.results = results
		self.threshold_low = threshold_low
		self.threshold_high = threshold_high
		self.problem_file_threshold = problem_file_threshold

	def sort_files(self, files: List[Union[Dict[str, Any], 'FileInfo']]) -> List['FileInfo']:
		"""
		Sorterar och konverterar fil-dictar till FileInfo-objekt.
		"""
		allowed_keys = {'path', 'complexity', 'functions', 'grade'}
		file_objs: List['FileInfo'] = []
		for f in files:
			if isinstance(f, FileInfo):
				file_objs.append(f)
			else:
				filtered = {k: v for k, v in f.items() if k in allowed_keys}
				file_objs.append(FileInfo(**filtered))
		return sorted(file_objs, key=lambda x: x.path)

	def average_complexity(self, files: List[Union[Dict[str, Any], 'FileInfo']]) -> float:
		"""
		Beräknar genomsnittlig komplexitet för en lista av filer.
		"""
		if not files:
			return 0.0
		def get_complexity(f: Union[Dict[str, Any], 'FileInfo']) -> float:
			return f.complexity if hasattr(f, 'complexity') else f['complexity']
		return sum(get_complexity(f) for f in files) / len(files)

	def average_grade(self, files: List[Union[Dict[str, Any], 'FileInfo']]) -> Union[str, Dict[str, Any]]:
		"""
		Returnerar genomsnittlig komplexitet och betyg för en lista av filer.
		"""
		if not files:
			return "No code"
		avg = self.average_complexity(files)
		return {
			'value': avg,
			'label': grade(avg, self.threshold_low, self.threshold_high),
			'formatted': f"{grade(avg, self.threshold_low, self.threshold_high)} ({avg:.1f})"
		}

	def prepare_structured_data(self) -> List[Dict[str, Any]]:
		"""
		Returnerar strukturerad data för rapporten per språk och root.
		"""
		structured: List[Dict[str, Any]] = []
		for language in sorted(self.results):
			language_section = {'name': language, 'roots': []}
			for root in sorted(self.results[language]):
				root_info = self._build_root_info(language, root, self.results[language][root])
				from .report_data_collector import ReportDataCollector
				from .report_data_analyzer import ReportDataAnalyzer
		return structured
