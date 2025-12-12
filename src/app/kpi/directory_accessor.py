"""
Directory Object Accessor

Handles extraction of data from directory objects with format compatibility.
Extracted from KPIAggregator to reduce complexity.
"""
from typing import Any, List


class DirectoryObjectAccessor:
    """
    Provides unified access to directory object attributes.

    Handles backward compatibility with different directory object formats:
    - New format: scan_dirs (dict), files (dict)
    - Old format: children (list), files (list)

    Responsibilities:
    - Extract subdirectories from directory objects
    - Extract files from directory objects
    - Extract directory names with fallback logic
    """

    @staticmethod
    def get_subdirectories(directory_obj: Any) -> List[Any]:
        """
        Extract subdirectories from a directory object.

        Handles both new 'scan_dirs' (dict) and old 'children' (list) formats.

        Args:
            directory_obj: Directory object to extract subdirectories from

        Returns:
            List of subdirectory objects
        """
        # Try new format first (scan_dirs dict)
        scan_dirs = getattr(directory_obj, 'scan_dirs', None)
        if scan_dirs and isinstance(scan_dirs, dict):
            return list(scan_dirs.values())

        # Fall back to old format (children list)
        children = getattr(directory_obj, 'children', None)
        if children:
            return list(children)

        return []

    @staticmethod
    def get_files(directory_obj: Any) -> List[Any]:
        """
        Extract files from a directory object.

        Handles both dict and list formats for files attribute.

        Args:
            directory_obj: Directory object to extract files from

        Returns:
            List of file objects
        """
        files = getattr(directory_obj, 'files', None)
        if files is None:
            return []

        # Handle dict format
        if isinstance(files, dict):
            return list(files.values())

        # Handle list format
        if isinstance(files, list):
            return files

        return []

    @staticmethod
    def get_name(directory_obj: Any) -> str:
        """
        Extract directory name from directory object.

        Tries 'dir_name' first, then 'name', with 'unknown' as fallback.

        Args:
            directory_obj: Directory object to extract name from

        Returns:
            Directory name string
        """
        return getattr(directory_obj, 'dir_name', getattr(directory_obj, 'name', 'unknown'))

    @staticmethod
    def count_files_in_tree(directory_obj: Any) -> int:
        """
        Count total number of files in directory tree.

        Args:
            directory_obj: ScanDir object to count files from

        Returns:
            Total number of files in tree
        """
        # Count files in this directory
        count = len(DirectoryObjectAccessor.get_files(directory_obj))

        # Recursively count files in subdirectories
        for subdir in DirectoryObjectAccessor.get_subdirectories(directory_obj):
            count += DirectoryObjectAccessor.count_files_in_tree(subdir)

        return count
