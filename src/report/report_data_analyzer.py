from typing import Any, Dict, List, Union
from .file_info import FileInfo
from .root_info import RootInfo
from src.kpis.complexity.metrics import grade
from .report_data_collector import ReportDataCollector



class ReportDataAnalyzer:
    """
    Analyserar och filtrerar data för komplexitetsrapporten.
    """
    def __init__(self, repo_info, threshold: float = 20.0, problem_file_threshold: Union[float, None] = None, threshold_low: float = 10.0, threshold_high: float = 20.0):
        self.repo_info = repo_info
        self.threshold = threshold
        self.problem_file_threshold = problem_file_threshold if problem_file_threshold is not None else threshold
        self.collector = ReportDataCollector(self.repo_info, threshold_low, threshold_high)

    def find_problematic_roots(self) -> List[Dict[str, Any]]:
        from .file_helpers import filter_problem_files, filter_hotspot_risk_files
        summary: List[Dict[str, Any]] = []
        
        # Använd collectorn för att få en strukturerad lista av RootInfo-objekt
        structured_data = self.collector.prepare_structured_data()
        
        for repo_data in structured_data:
            for root_info in repo_data.get('roots', []):
                problem_files = filter_problem_files(root_info.files, self.problem_file_threshold) if self.problem_file_threshold is not None else []
                hotspot_risk_files = filter_hotspot_risk_files(root_info.files)

                if root_info.average > self.threshold or (self.problem_file_threshold is not None and problem_files) or hotspot_risk_files:
                    summary.append({
                        'language': 'code', # Dummy-värde, kan förbättras
                        'root': root_info.path,
                        'repo_root': getattr(root_info, 'repo_root', ''),
                        'average': root_info.average,
                        'grade': grade(root_info.average, self.collector.threshold_low, self.collector.threshold_high)['label'],
                        'problem_files': problem_files,
                        'files': root_info.files,
                        'hotspot_risk_files': hotspot_risk_files
                    })
        return summary
