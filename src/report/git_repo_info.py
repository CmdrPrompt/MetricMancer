from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class GitRepoInfo:
    repo_root: str
    repo_name: str = ''  # mappnamnet för .git-directory
    scan_dirs: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    churn_data: dict = field(default_factory=dict)
    commits: List[str] = field(default_factory=list)
    results: dict = field(default_factory=dict)  # analyserade filer och data
