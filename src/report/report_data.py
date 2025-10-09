
from typing import Any, Dict, List, Union
from .file_info import FileInfo
from .report_data_collector import ReportDataCollector
from .root_info import RootInfo


class ReportData:
    """
    Holds data for report generation.
    Stores summary and detailed report data.
    """
    def __init__(self, summary, details):
        """
        Initialize the ReportData object.
        Args:
            summary: Summary data for the report.
            details: Detailed data for the report.
        """
        self.summary = summary
        self.details = details


class ReportData:
    """
    Holds data for report generation.
    Stores summary and detailed report data.
    """
    def __init__(self, summary, details):
        """
        Initialize the ReportData object.
        Args:
            summary: Summary data for the report.
            details: Detailed data for the report.
        """
        self.summary = summary

    self.details = details


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
        Prepare structured data for the report, organized by language and root.
        Returns:
            List of dictionaries, each containing language name and root information.
        """
        structured: List[Dict[str, Any]] = []
        for language in sorted(self.results):
            language_section = {'name': language, 'roots': []}
            for root in sorted(self.results[language]):
                root_info = self.collector.build_root_info(language, root, self.results[language][root])
                language_section['roots'].append(root_info)
            structured.append(language_section)
        return structured
