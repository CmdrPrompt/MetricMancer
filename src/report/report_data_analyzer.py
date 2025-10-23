from typing import Any, Dict, List, Union

from .grading import grade
from .file_helpers import filter_hotspot_risk_files, filter_problem_files
from .report_data_collector import ReportDataCollector


class ReportDataAnalyzer:
    """
    Analyzes and filters data for the complexity report.
    Identifies problematic roots (directories) based on thresholds and risk criteria.
    """

    def __init__(self, repo_info, threshold: float = 20.0,
                 problem_file_threshold: Union[float, None] = None, threshold_low: float = 10.0, threshold_high: float = 20.0):
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

    def _is_root_problematic(self, average_complexity: float, problem_files: List, hotspot_risk_files: List) -> bool:
        """
        Determine if a root directory is problematic based on thresholds and risk criteria.

        Args:
            average_complexity: Average complexity of the root
            problem_files: List of files exceeding problem threshold
            hotspot_risk_files: List of files with hotspot risk

        Returns:
            True if the root is problematic, False otherwise
        """
        # Root is problematic if:
        # 1. Average complexity exceeds threshold, OR
        # 2. Has problem files (if threshold is set), OR
        # 3. Has hotspot risk files
        exceeds_average_threshold = average_complexity > self.threshold
        has_problem_files = bool(self.problem_file_threshold is not None and problem_files)
        has_hotspot_risks = bool(hotspot_risk_files)

        return exceeds_average_threshold or has_problem_files or has_hotspot_risks

    def _calculate_root_metrics(self, root_info) -> Dict[str, Any]:
        """
        Calculate metrics for a single root directory.

        Args:
            root_info: RootInfo object containing root data

        Returns:
            Dict with average_complexity, problem_files, hotspot_risk_files
        """
        problem_files = []
        if self.problem_file_threshold is not None:
            problem_files = filter_problem_files(
                root_info.files, self.problem_file_threshold)

        hotspot_risk_files = filter_hotspot_risk_files(root_info.files)

        return {
            'average_complexity': root_info.average,
            'problem_files': problem_files,
            'hotspot_risk_files': hotspot_risk_files
        }

    def _create_root_summary(self, root_path: str, average_complexity: float, problem_files: List,
                             hotspot_risk_files: List, files: List, repo_root: str = '') -> Dict[str, Any]:
        """
        Create a summary dictionary for a problematic root.

        Args:
            root_path: Path to the root directory
            average_complexity: Average complexity of the root
            problem_files: List of files exceeding problem threshold
            hotspot_risk_files: List of files with hotspot risk
            files: All files in the root
            repo_root: Repository root path

        Returns:
            Dictionary with root summary information
        """
        return {
            'language': 'code',  # Placeholder value, can be improved
            'root': root_path,
            'repo_root': repo_root,
            'average': average_complexity,
            'grade': grade(average_complexity, self.collector.threshold_low, self.collector.threshold_high),
            'problem_files': problem_files,
            'files': files,
            'hotspot_risk_files': hotspot_risk_files
        }

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
                # Calculate metrics for this root
                metrics = self._calculate_root_metrics(root_info)

                # Check if root is problematic using extracted logic
                if self._is_root_problematic(metrics['average_complexity'],
                                             metrics['problem_files'], metrics['hotspot_risk_files']):
                    summary.append(self._create_root_summary(
                        root_info.path, metrics['average_complexity'], metrics['problem_files'], metrics['hotspot_risk_files'],
                        root_info.files, getattr(root_info, 'repo_root', '')
                    ))
        return summary
