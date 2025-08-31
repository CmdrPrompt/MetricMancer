from typing import Any, Dict, List, Union
from .file_info import FileInfo
from .root_info import RootInfo
from ..metrics import grade
from .report_data_collector import ReportDataCollector



class ReportDataAnalyzer:
    """
    Analyserar och filtrerar data för komplexitetsrapporten.
    """
    def __init__(self, repo_info, threshold: float = 20.0, problem_file_threshold: Union[float, None] = None, threshold_low: float = 10.0, threshold_high: float = 20.0):
        self.repo_info = repo_info
        self.results = repo_info.results
        self.threshold = threshold
        self.problem_file_threshold = problem_file_threshold if problem_file_threshold is not None else threshold
        self.collector = ReportDataCollector(self.repo_info, threshold_low, threshold_high)

    def find_problematic_roots(self) -> List[Dict[str, Any]]:
        summary: List[Dict[str, Any]] = []
        for language, roots in self.results.items():
            for root, files in roots.items():
                if not files:
                    continue
                root_info = self.collector.build_root_info(language, root, files)
                if self.problem_file_threshold is not None:
                    problem_files = [f for f in root_info.files if f.complexity >= self.problem_file_threshold]
                else:
                    problem_files = []

                # Hotspot-risk: medium (>=100) och hög (>300)
                hotspot_risk_files = []
                for f in root_info.files:
                    if f.complexity is not None and f.churn is not None:
                        hs_score = f.complexity * f.churn
                        if hs_score > 300 or (f.complexity > 15 and f.churn > 15):
                            hotspot_risk_files.append(f)
                        elif hs_score >= 100:
                            hotspot_risk_files.append(f)

                if root_info.average > self.threshold or (self.problem_file_threshold is not None and problem_files) or hotspot_risk_files:
                    summary.append({
                        'language': language,
                        'root': root,
                        'repo_root': getattr(root_info, 'repo_root', ''),
                        'average': root_info.average,
                        'grade': grade(root_info.average, self.collector.threshold_low, self.collector.threshold_high),
                        'problem_files': problem_files,
                        'files': root_info.files,
                        'hotspot_risk_files': hotspot_risk_files
                    })
        return sorted(summary, key=lambda x: (-x['average'], x['language'], x['root']))
