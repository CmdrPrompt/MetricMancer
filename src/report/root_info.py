
from dataclasses import dataclass, field
from typing import List
from .file_info import FileInfo

@dataclass
class RootInfo:
    path: str
    average: float
    min_complexity: float
    max_complexity: float
    files: List[FileInfo] = field(default_factory=list)
