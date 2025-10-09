from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from src.kpis.base_kpi import BaseKPI


@dataclass
class Function:
    """Represents a single function or method in a file."""
    name: str
    kpis: Dict[str, BaseKPI] = field(default_factory=dict)


@dataclass
class File:
    """
    Represents a single file that has been analyzed.
    """
    name: str
    file_path: str  # Relative path from ScanDir
    kpis: Dict[str, BaseKPI] = field(default_factory=dict)
    functions: List[Function] = field(default_factory=list)


@dataclass
class BaseDir:
    """
    Base class for directory-like objects.
    """
    dir_name: str
    scan_dir_path: str  # Relative path from repo_root
    repo_root_path: str
    repo_name: str


@dataclass
class ScanDir(BaseDir):
    """
    Represents a scanned directory, which can contain files and subdirectories.
    """
    files: Dict[str, File] = field(default_factory=dict)
    scan_dirs: Dict[str, ScanDir] = field(default_factory=dict)
    kpis: Dict[str, BaseKPI] = field(default_factory=dict)


@dataclass
class RepoInfo(ScanDir):
    """Top-level object representing an entire repository with its structure and KPIs."""
    pass
