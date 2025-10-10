import os
import subprocess
from collections import Counter
from typing import Mapping, Union

from src.kpis.base_kpi import BaseKPI
from src.utilities.git_cache import get_git_cache

class CodeOwnershipKPI(BaseKPI):
    """
    Calculates code ownership for a file using git blame.
    Value is a dict: {author: ownership_percent}
    Now uses shared GitDataCache for improved performance.
    """
    
    def calculate(self, *args, **kwargs):
        # For compatibility with BaseKPI, just return the value
        return self.value

    def __init__(self, file_path: str, repo_root: str):
        super().__init__(
            name="Code Ownership",
            description="Proportion of code lines owned by each author (via git blame)",
            value=None
        )
        self.file_path = file_path
        self.repo_root = repo_root
        
        # Use shared git cache instead of class-level cache
        git_cache = get_git_cache()
        self.value = git_cache.get_ownership_data(repo_root, file_path)
