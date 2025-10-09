from typing import Any, Dict, List, Union

from src.kpis.complexity.metrics import grade
from .file_helpers import filter_hotspot_risk_files, filter_problem_files
from .file_info import FileInfo
from .report_data_collector import ReportDataCollector
from .root_info import RootInfo


class ReportDataAnalyzer:
    """
    Analyzes and filters data for the complexity report.
    Identifies problematic roots (directories) based on thresholds and risk criteria.
    """
    def __init__(self, repo_info, threshold: float = 20.0, problem_file_threshold: Union[float, None] = None, threshold_low: float = 10.0, threshold_high: float = 20.0):
        """
        Initialize the ReportDataAnalyzer.
        Args:
            repo_info: The analyzed repository data model (RepoInfo).
            threshold: Threshold for average complexity to flag a root as problematic.
            problem_file_threshold: Threshold for flagging individual files as problematic.
            threshold_low: Lower threshold for complexity grading.
            threshold_high: Upper threshold for complexity grading.
        """
        self.repo_info = repo_info
        self.threshold = threshold
        self.problem_file_threshold = problem_file_threshold if problem_file_threshold is not None else threshold
        self.collector = ReportDataCollector(self.repo_info, threshold_low, threshold_high)

    def find_problematic_roots(self) -> List[Dict[str, Any]]:
        """
        Find and summarize problematic roots (directories) in the repository.
        Returns a list of dicts with information about roots that exceed thresholds or contain risk files.
        Returns:
            List of dicts with root path, average complexity, grade, problem files, and hotspot risk files.
        """
        summary: List[Dict[str, Any]] = []

        # Use the collector to get a structured list of RootInfo objects
        structured_data = self.collector.prepare_structured_data()

        for repo_data in structured_data:
            for root_info in repo_data.get('roots', []):
                problem_files = filter_problem_files(root_info.files, self.problem_file_threshold) if self.problem_file_threshold is not None else []
                hotspot_risk_files = filter_hotspot_risk_files(root_info.files)

                if root_info.average > self.threshold or (self.problem_file_threshold is not None and problem_files) or hotspot_risk_files:
                    summary.append({
                        'language': 'code',  # Placeholder value, can be improved
                        'root': root_info.path,
                        'repo_root': getattr(root_info, 'repo_root', ''),
                        'average': root_info.average,
                        'grade': grade(root_info.average, self.collector.threshold_low, self.collector.threshold_high)['label'],
                        'problem_files': problem_files,
                        'files': root_info.files,
                        'hotspot_risk_files': hotspot_risk_files
                    })
        return summary
