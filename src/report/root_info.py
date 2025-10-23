"""
Root information data structures for report generation.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class RootInfo:
    """
    Represents information about a repository root for reporting purposes.
    """
    name: str
    files: List[Dict[str, Any]]
    summary: Dict[str, Any]

    def __post_init__(self):
        if self.files is None:
            self.files = []
        if self.summary is None:
            self.summary = {}
