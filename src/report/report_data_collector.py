from typing import Any, Dict, List, Union
from .file_info import FileInfo
from .root_info import RootInfo
from .file_helpers import sort_files, average_complexity, average_grade
from ..metrics import grade

class ReportDataCollector:
    """
    Samlar och strukturerar data för komplexitetsrapporten.
    """
    def __init__(self, results: Dict[str, Dict[str, List[Dict[str, Any]]]], threshold_low: float = 10.0, threshold_high: float = 20.0):
        self.results = results
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high


    # Use shared helpers instead of duplicate methods

    def build_root_info(self, language: str, root: str, files: List[Union[Dict[str, Any], FileInfo]]) -> RootInfo:
        files = sort_files(files)
        for f in files:
            if not f.grade:
                f.grade = grade(f.complexity, self.threshold_low, self.threshold_high)
        avg_grade = average_grade(files, self.threshold_low, self.threshold_high)
        return RootInfo(
            path=root,
            average=avg_grade['value'] if isinstance(avg_grade, dict) else avg_grade,
            files=files
        )

    def prepare_structured_data(self) -> List[Dict[str, Any]]:
        structured: List[Dict[str, Any]] = []
        for language in sorted(self.results):
            language_section = {'name': language, 'roots': []}
            for root in sorted(self.results[language]):
                root_info = self.build_root_info(language, root, self.results[language][root])
                language_section['roots'].append(root_info)
            structured.append(language_section)
        return structured
