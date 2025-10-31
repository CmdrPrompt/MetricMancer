"""
File information data structures for report generation.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class FileInfo:
    """
    Represents information about a file for reporting purposes.
    """
    path: str
    complexity: float = 0.0
    churn: float = 0.0
    functions: int = 0
    grade: Optional[str] = None
    repo_root: str = ""
    kpis: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.kpis is None:
            self.kpis = {}
