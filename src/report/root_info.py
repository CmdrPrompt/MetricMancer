from dataclasses import dataclass, field
from typing import List
from .file_info import FileInfo

@dataclass
class RootInfo:
    path: str
    average: float
    files: List[FileInfo] = field(default_factory=list)
