from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class GitRepoInfo:
    @property
    def repo_stats(self):
        """
        Returns a dict with statistics: avg/min/max complexity, avg churn, most common grade.
        """
        from collections import Counter
        all_files = []
        for language in self.results:
            for root in self.results[language]:
                all_files.extend(self.results[language][root])
        complexities = [f.get('complexity', 0) for f in all_files]
        churns = [f.get('churn', 0) for f in all_files]
        grades = [f.get('grade', '') for f in all_files]
        avg_complexity = round(sum(complexities)/len(complexities), 1) if complexities else 0
        min_complexity = round(min(complexities), 1) if complexities else 0
        max_complexity = round(max(complexities), 1) if complexities else 0
        avg_churn = round(sum(churns)/len(churns), 1) if churns else 0
        grade = Counter(grades).most_common(1)[0][0] if grades else ''
        return {
            'avg_complexity': avg_complexity,
            'min_complexity': min_complexity,
            'max_complexity': max_complexity,
            'avg_churn': avg_churn,
            'grade': grade
        }
    repo_root: str
    repo_name: str = ''  # mappnamnet för .git-directory
    scan_dirs: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    churn_data: dict = field(default_factory=dict)
    complexity_data: dict = field(default_factory=dict)
    hotspot_data: dict = field(default_factory=dict)
    commits: List[str] = field(default_factory=list)
    results: dict = field(default_factory=dict)  # analyserade filer och data
