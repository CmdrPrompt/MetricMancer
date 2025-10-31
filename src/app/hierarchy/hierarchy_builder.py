"""
HierarchyBuilder - Build directory hierarchy for analyzed files.

This module provides the HierarchyBuilder class which constructs RepoInfo/ScanDir
tree structures by placing analyzed File objects into the correct directory nodes.

Responsibilities:
    - Parse directory paths from file paths
    - Create and navigate ScanDir hierarchy
    - Place File objects in correct directory nodes
    - Maintain parent-child directory relationships

Does NOT:
    - Aggregate KPIs (that's KPIAggregator - Phase 4)
    - Analyze files (that's FileAnalyzer - Phase 2)
    - Calculate KPIs (that's KPICalculator - Phase 1)

Example:
    >>> builder = HierarchyBuilder()
    >>> repo_info = RepoInfo(repo_root_path="/repo", repo_name="myproject")
    >>> files = [file1, file2, file3]  # from FileAnalyzer
    >>>
    >>> repo_info = builder.build_hierarchy(repo_info, files)
    >>> # repo_info now has complete directory hierarchy
"""

from pathlib import Path
from typing import List, Tuple

from src.kpis.model import RepoInfo, ScanDir, File


class HierarchyBuilder:
    """
    Builds directory hierarchy for analyzed files.

    This class is responsible for constructing the RepoInfo/ScanDir tree structure
    by placing analyzed File objects into the correct directory nodes based on their
    file paths.

    Attributes:
        None (stateless component)

    Example:
        >>> builder = HierarchyBuilder()
        >>> repo_info = RepoInfo(repo_root_path="/repo", repo_name="myproject")
        >>> files = [
        ...     File(name="main.py", file_path="src/main.py", ...),
        ...     File(name="utils.py", file_path="src/utils/utils.py", ...)
        ... ]
        >>> repo_info = builder.build_hierarchy(repo_info, files)
        >>> print(repo_info.scan_dirs.keys())  # {'src'}
        >>> print(repo_info.scan_dirs['src'].scan_dirs.keys())  # {'utils'}
    """

    def __init__(self):
        """Initialize HierarchyBuilder (stateless)."""
        pass

    def build_hierarchy(
        self,
        repo_info: RepoInfo,
        files: List[File]
    ) -> RepoInfo:
        """
        Build complete directory hierarchy from list of analyzed files.

        Iterates through all files and places them in the correct directory nodes,
        creating ScanDir objects as needed to represent the directory structure.

        Args:
            repo_info: Root RepoInfo object to populate with hierarchy
            files: List of analyzed File objects to place in hierarchy

        Returns:
            RepoInfo object with complete hierarchy populated

        Example:
            >>> builder = HierarchyBuilder()
            >>> repo_info = RepoInfo(repo_root_path="/repo", repo_name="test")
            >>> files = [
            ...     File(name="README.md", file_path="README.md", ...),
            ...     File(name="main.py", file_path="src/main.py", ...)
            ... ]
            >>> result = builder.build_hierarchy(repo_info, files)
            >>> "README.md" in result.files  # True
            >>> "src" in result.scan_dirs    # True
        """
        for file in files:
            self.add_file_to_hierarchy(repo_info, file)
        return repo_info

    def add_file_to_hierarchy(
        self,
        repo_info: RepoInfo,
        file: File
    ) -> None:
        """
        Add single file to hierarchy (creates directory structure as needed).

        Parses the file's path to determine its directory location, creates any
        necessary ScanDir objects, and places the file in the correct directory node.

        Args:
            repo_info: Root RepoInfo object
            file: File object to add to hierarchy

        Example:
            >>> builder = HierarchyBuilder()
            >>> repo_info = RepoInfo(repo_root_path="/repo", repo_name="test")
            >>> file = File(name="utils.py", file_path="src/utils/utils.py", ...)
            >>> builder.add_file_to_hierarchy(repo_info, file)
            >>> # Creates: repo_info -> ScanDir("src") -> ScanDir("utils") -> File
        """
        # Parse directory path from file.file_path
        path_parts, filename = self._parse_directory_path(
            file.file_path,
            repo_info.repo_root_path
        )

        if not path_parts:
            # Root-level file (no subdirectory)
            repo_info.files[file.name] = file
        else:
            # File is in a subdirectory - navigate/create hierarchy
            container = self._get_or_create_scan_dir(
                repo_info,
                path_parts
            )
            container.files[file.name] = file

    def _parse_directory_path(
        self,
        file_path: str,
        repo_root: str
    ) -> Tuple[List[str], str]:
        """
        Parse file path into directory parts and filename.

        Extracts the directory components from a file path, filtering out
        empty parts and current directory notation ('.').

        Args:
            file_path: Relative file path (e.g., "src/app/main.py")
            repo_root: Repository root path (for reference)

        Returns:
            Tuple of (directory_parts, filename)
            - directory_parts: List of directory names from root to file
            - filename: Name of the file

        Examples:
            >>> builder = HierarchyBuilder()
            >>> builder._parse_directory_path("main.py", "/repo")
            ([], "main.py")
            >>> builder._parse_directory_path("src/main.py", "/repo")
            (["src"], "main.py")
            >>> builder._parse_directory_path("src/app/utils/helpers.py", "/repo")
            (["src", "app", "utils"], "helpers.py")
            >>> builder._parse_directory_path("./src/main.py", "/repo")
            (["src"], "main.py")  # Filters out '.'
        """
        path = Path(file_path)
        filename = path.name

        # Get directory parts, filtering out empty strings and current directory notation
        dir_parts = [
            part for part in path.parent.parts
            if part and part != '.'
        ]

        return dir_parts, filename

    def _get_or_create_scan_dir(
        self,
        repo_info: RepoInfo,
        path_parts: List[str]
    ) -> ScanDir:
        """
        Navigate hierarchy, creating ScanDir nodes as needed.

        Traverses the directory hierarchy according to path_parts, creating
        ScanDir objects for any directories that don't exist yet. Returns
        the final ScanDir node where the file should be placed.

        Args:
            repo_info: Root RepoInfo object
            path_parts: List of directory names representing the path
                       (e.g., ["src", "app", "utils"])

        Returns:
            ScanDir object at the end of the path

        Example:
            >>> builder = HierarchyBuilder()
            >>> repo_info = RepoInfo(repo_root_path="/repo", repo_name="test")
            >>> scan_dir = builder._get_or_create_scan_dir(
            ...     repo_info,
            ...     ["src", "app", "utils"]
            ... )
            >>> # Creates: RepoInfo -> ScanDir("src") -> ScanDir("app") -> ScanDir("utils")
            >>> scan_dir.dir_name  # "utils"
            >>> scan_dir.scan_dir_path  # "src/app/utils"

        Note:
            - Reuses existing ScanDir objects if they already exist
            - Maintains proper parent-child relationships
            - Builds scan_dir_path incrementally
        """
        current_container = repo_info
        current_path = Path()

        for part in path_parts:
            current_path = current_path / part

            if part not in current_container.scan_dirs:
                # Create new ScanDir for this directory level
                current_container.scan_dirs[part] = ScanDir(
                    dir_name=part,
                    scan_dir_path=str(current_path),
                    repo_root_path=repo_info.repo_root_path,
                    repo_name=repo_info.repo_name
                )

            # Navigate to next level
            current_container = current_container.scan_dirs[part]

        return current_container
