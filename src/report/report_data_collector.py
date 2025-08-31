from typing import Any, Dict, List, Union
from .file_info import FileInfo
from .root_info import RootInfo
from .file_helpers import sort_files, average_complexity, average_grade
from src.complexity.metrics import grade


class ReportDataCollector:
    """
    Samlar och strukturerar data för komplexitetsrapporten.
    """
    def __init__(self, repo_info, threshold_low: float = 10.0, threshold_high: float = 20.0):
        self.repo_info = repo_info
        self.results = repo_info.results
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high


    # Use shared helpers instead of duplicate methods

    def build_root_info(self, language: str, root: str, files: List[Union[Dict[str, Any], FileInfo]]) -> RootInfo:
        files = sort_files(files)
        # Filtrera bort dubbletter baserat på path
        unique_files = {}
        for f in files:
            if not f.grade:
                f.grade = grade(f.complexity, self.threshold_low, self.threshold_high)
            unique_files[f.path] = f
        files = list(unique_files.values())
        avg_grade = average_grade(files, self.threshold_low, self.threshold_high)
        complexities = [f.complexity for f in files] if files else []
        min_complexity = min(complexities) if complexities else 0.0
        max_complexity = max(complexities) if complexities else 0.0
        repo_root = getattr(files[0], 'repo_root', '') if files else ''
        return RootInfo(
            path=root,
            average=avg_grade['value'] if isinstance(avg_grade, dict) else avg_grade,
            min_complexity=min_complexity,
            max_complexity=max_complexity,
            files=files,
            repo_root=repo_root
        )

    def prepare_structured_data(self) -> List[Dict[str, Any]]:
        # Group all roots by repo_root
        repo_map = {}
        for language in self.results:
            for root in self.results[language]:
                root_info = self.build_root_info(language, root, self.results[language][root])
                repo_root = root_info.repo_root or '<unknown>'
                if repo_root not in repo_map:
                    repo_map[repo_root] = []
                repo_map[repo_root].append(root_info)
        # Build structured list for template
        structured = []
        for repo_root, roots in repo_map.items():
            structured.append({'repo_root': repo_root, 'roots': roots})
        return structured
