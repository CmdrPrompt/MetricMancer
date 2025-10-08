
from src.kpis.base_kpi import BaseKPI
import subprocess
from collections import Counter
from typing import Mapping, Union


class CodeOwnershipKPI(BaseKPI):
    def calculate(self, *args, **kwargs):
        # For compatibility with BaseKPI, just return the value
        return self.value
    """
    Calculates code ownership for a file using git blame.
    Value is a dict: {author: ownership_percent}
    """
    def __init__(self, file_path: str, repo_root: str):
        super().__init__(
            name="Code Ownership",
            description="Proportion of code lines owned by each author (via git blame)",
            value=None
        )
        self.file_path = file_path
        self.repo_root = repo_root
        self.value = self.calculate_ownership()
    # Debug print removed

    def calculate_ownership(self) -> Mapping[str, Union[float, str]]:
        import os
        # Skip node_modules and similar directories
        if 'node_modules' in self.file_path or not os.path.exists(self.file_path):
            return {"ownership": "N/A"}
        # Check if file is tracked by git
        try:
            tracked = subprocess.run(
                ['git', '-C', self.repo_root, 'ls-files', '--error-unmatch', self.file_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            if tracked.returncode != 0:
                return {"ownership": "N/A"}
        except Exception:
            return {"ownership": "N/A"}
        try:
            blame_output = subprocess.check_output(
                ['git', '-C', self.repo_root, 'blame', '--line-porcelain', self.file_path],
                text=True
            )
            authors = [line[7:] for line in blame_output.splitlines() if line.startswith('author ')]
            total_lines = len(authors)
            if total_lines == 0:
                return {}
            counts = Counter(authors)
            ownership = {author: round(count / total_lines * 100, 1) for author, count in counts.items()}
            return ownership
        except Exception as e:
            # Could not calculate ownership (e.g., not a git repo, file not tracked)
            return {"ownership": "N/A"}
