from typing import Any, Dict, List, Union
from .file_info import FileInfo
from .root_info import RootInfo
from .file_helpers import sort_files, average_complexity, average_grade
from src.kpis.complexity.metrics import grade


class ReportDataCollector:
    """
    Samlar och strukturerar data för komplexitetsrapporten.
    """
    def __init__(self, repo_info, threshold_low: float = 10.0, threshold_high: float = 20.0):
        self.repo_info = repo_info
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high

    def _traverse_and_collect(self, scan_dir, collected_files):
        """Rekursiv hjälpmetod för att samla in filer från datamodellen."""
        for file_obj in scan_dir.files.values():
            complexity = file_obj.kpis.get('complexity')
            churn = file_obj.kpis.get('churn')
            
            file_info = {
                'path': file_obj.file_path,
                'complexity': complexity.value if complexity else 0,
                'churn': churn.value if churn else 0,
                'functions': complexity.calculation_values.get('function_count', 0) if complexity else 0,
                'repo_root': self.repo_info.repo_root_path
            }
            collected_files.append(file_info)

        for sub_dir in scan_dir.scan_dirs.values():
            self._traverse_and_collect(sub_dir, collected_files)

    # Use shared helpers instead of duplicate methods

    def build_root_info(self, language: str, root: str, files: List[Union[Dict[str, Any], FileInfo]]) -> RootInfo:
        files = sort_files(files)
        # Sätt betyg på filerna
        for file_info in files:
            if not file_info.grade:
                file_info.grade = grade(file_info.complexity, self.threshold_low, self.threshold_high)

        avg_grade = average_grade(files, self.threshold_low, self.threshold_high)
        complexities = [f.complexity for f in files] if files else []
        min_complexity = min(complexities) if complexities else 0.0
        max_complexity = max(complexities) if complexities else 0.0
        repo_root = getattr(files[0], 'repo_root', '') if files else ''
        return RootInfo(
            path=root, # 'root' är här en scannad katalog
            average=avg_grade['value'] if isinstance(avg_grade, dict) else avg_grade,
            min_complexity=min_complexity,
            max_complexity=max_complexity,
            files=files,
            repo_root=repo_root
        )

    def prepare_structured_data(self) -> List[Dict[str, Any]]:
        """Skapar den datastruktur som rapport-templaten förväntar sig."""
        all_files = []
        for scan_dir in self.repo_info.scan_dirs.values():
            self._traverse_and_collect(scan_dir, all_files)

        # För nuvarande rapportstruktur, gruppera per "språk" (här en dummy) och "root" (scan_dir)
        # Detta kan förenklas i framtiden om templaten anpassas.
        root_info = self.build_root_info('code', self.repo_info.repo_root_path, all_files)
        
        return [{'repo_root': self.repo_info.repo_name, 'roots': [root_info]}]
