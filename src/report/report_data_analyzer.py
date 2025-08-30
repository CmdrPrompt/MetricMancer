from typing import Any, Dict, List, Union
from .file_info import FileInfo
from .root_info import RootInfo
from ..metrics import grade
from .report_data_collector import ReportDataCollector

class ReportDataAnalyzer:
    """
    Analyserar och filtrerar data för komplexitetsrapporten.
    """
    def __init__(self, results: Dict[str, Dict[str, List[Dict[str, Any]]]], threshold: float = 20.0, problem_file_threshold: Union[float, None] = None, threshold_low: float = 10.0, threshold_high: float = 20.0):
        self.results = results
        self.threshold = threshold
        self.problem_file_threshold = problem_file_threshold if problem_file_threshold is not None else threshold
        self.collector = ReportDataCollector(results, threshold_low, threshold_high)

    def find_problematic_roots(self) -> List[Dict[str, Any]]:
        summary: List[Dict[str, Any]] = []
        for language, roots in self.results.items():
            for root, files in roots.items():
                if not files:
                    continue
                root_info = self.collector.build_root_info(language, root, files)
                if self.problem_file_threshold is not None:
                    problem_files = [f for f in root_info.files if f.complexity > self.problem_file_threshold]
                else:
                    problem_files = []
                if root_info.average > self.threshold or (self.problem_file_threshold is not None and problem_files):
                    summary.append({
                        'language': language,
                        'root': root,
                        'average': root_info.average,
                        'grade': grade(root_info.average, self.collector.threshold_low, self.collector.threshold_high),
                        'problem_files': problem_files
                    })
        return sorted(summary, key=lambda x: (-x['average'], x['language'], x['root']))
