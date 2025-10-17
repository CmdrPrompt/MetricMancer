
from typing import Any, Dict, List, Union
from .file_info import FileInfo
from src.kpis.model import ScanDir
from .root_info import RootInfo
from .file_helpers import sort_files, average_complexity, average_grade
from .report_helpers import grade


class ReportDataCollector:
    """
    Collects and structures data for the complexity report.
    Traverses the repository data model and prepares file-level and root-level summaries.
    """

    def __init__(self, repo_info, threshold_low: float = 10.0, threshold_high: float = 20.0):
        """
        Initialize the ReportDataCollector.
        Args:
            repo_info: The analyzed repository data model (RepoInfo).
            threshold_low: Lower threshold for complexity grading.
            threshold_high: Upper threshold for complexity grading.
        """
        self.repo_info = repo_info
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high

    def _create_file_info_dict(self, file_obj) -> Dict[str, Any]:
        """
        Extract file information from a file object and create a dictionary.
        
        Args:
            file_obj: File object from the data model.
            
        Returns:
            Dictionary with file path, complexity, churn, functions count, and repo root.
        """
        complexity = file_obj.kpis.get('complexity')
        churn = file_obj.kpis.get('churn')
        
        return {
            'path': file_obj.file_path,
            'complexity': complexity.value if complexity else 0,
            'churn': churn.value if churn else 0,
            'functions': complexity.calculation_values.get('function_count', 0) if complexity else 0,
            'repo_root': getattr(self.repo_info, 'repo_root_path', '')
        }

    def _traverse_and_collect_files(self, scan_dir: ScanDir) -> List[Dict[str, Any]]:
        """
        Recursively collect all files from the data model (ScanDir tree).
        Returns a flat list of file info dictionaries.
        """
        collected_files = []
        for file_obj in scan_dir.files.values():
            file_info = self._create_file_info_dict(file_obj)
            collected_files.append(file_info)

        for sub_dir in scan_dir.scan_dirs.values():
            collected_files.extend(self._traverse_and_collect_files(sub_dir))
        return collected_files

    def _assign_grades_to_files(self, files: List[FileInfo]) -> None:
        """
        Assign grade to files if not already set.
        
        Args:
            files: List of FileInfo objects to assign grades to.
        """
        for file_info in files:
            if not file_info.grade:
                file_info.grade = grade(
                    file_info.complexity,
                    self.threshold_low,
                    self.threshold_high
                )

    def _calculate_complexity_stats(self, files: List[FileInfo]) -> Dict[str, float]:
        """
        Calculate min and max complexity statistics from files.
        
        Args:
            files: List of FileInfo objects.
            
        Returns:
            Dictionary with 'min' and 'max' complexity values.
        """
        complexities = [f.complexity for f in files] if files else []
        return {
            'min': min(complexities) if complexities else 0.0,
            'max': max(complexities) if complexities else 0.0
        }

    def build_root_info(self, language: str, root: str, files: List[Union[Dict[str, Any], FileInfo]]) -> RootInfo:
        """
        Build a RootInfo object for a given root directory and its files.
        Args:
            language: The language label (currently a placeholder).
            root: The root directory path.
            files: List of file info dicts or FileInfo objects.
        Returns:
            RootInfo object summarizing the directory.
        """
        files = sort_files(files)
        
        # Assign grades to files if not already set
        self._assign_grades_to_files(files)
        
        # Calculate statistics
        avg_grade = average_grade(files, self.threshold_low, self.threshold_high)
        complexity_stats = self._calculate_complexity_stats(files)
        repo_root = getattr(files[0], 'repo_root', '') if files else ''
        
        return RootInfo(
            path=root,  # 'root' is the scanned directory
            average=avg_grade['value'] if isinstance(avg_grade, dict) else avg_grade,
            min_complexity=complexity_stats['min'],
            max_complexity=complexity_stats['max'],
            files=files,
            repo_root=repo_root
        )

    def prepare_structured_data(self) -> List[Dict[str, Any]]:
        """
        Create the data structure expected by the report templates.
        Flattens the rich RepoInfo model into a legacy structure for reporting.
        Returns:
            List of dicts with repo_root and roots (RootInfo objects).
        """
        all_files = self._traverse_and_collect_files(self.repo_info)

        # For current report structure, group by "language" (dummy) and "root" (scan_dir)
        root_path = getattr(self.repo_info, 'repo_root_path', '')
        root_info = self.build_root_info('code', root_path, all_files)

        return [{'repo_root': getattr(self.repo_info, 'repo_name', ''), 'roots': [root_info]}]
