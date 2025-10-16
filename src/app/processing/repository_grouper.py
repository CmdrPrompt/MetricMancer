"""
RepositoryGrouper - Groups files by repository root.

This class follows the Single Responsibility Principle (SRP) by focusing
solely on organizing files into repository groups. It's a pure utility class
with no side effects, making it highly testable.

Part of the Analyzer refactoring to reduce complexity from 121 to manageable levels.
"""
from collections import defaultdict
from typing import List, Dict, Set, Tuple


class RepositoryGrouper:
    """
    Groups files by their repository root directory.
    
    Responsibilities:
    - Group files by repository root
    - Track scan directories per repository
    - Maintain file order within repositories
    
    This class is stateless and provides pure functions for grouping,
    making it easy to test and reason about.
    
    Example:
        >>> grouper = RepositoryGrouper()
        >>> files = [
        ...     {'path': '/repo1/src/a.py', 'root': '/repo1'},
        ...     {'path': '/repo1/src/b.py', 'root': '/repo1'},
        ...     {'path': '/repo2/src/c.py', 'root': '/repo2'}
        ... ]
        >>> files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        >>> len(files_by_root)  # 2 repositories
        2
        >>> len(files_by_root['/repo1'])  # 2 files in repo1
        2
    """
    
    def group_by_repository(self, files: List[dict]) -> Tuple[Dict[str, List[dict]], Dict[str, Set[str]]]:
        """
        Groups files by their repository root directory.
        
        Takes a list of file dictionaries and organizes them by their
        'root' field. Also tracks the scan directories (currently just
        the root itself) for each repository.
        
        Args:
            files: List of file dictionaries. Each file should have:
                   - 'path': Full path to the file
                   - 'root': Repository root path (optional, defaults to '')
                   - Any other metadata is preserved
        
        Returns:
            Tuple containing:
            - files_by_root: Dictionary mapping repository root to list of files
            - scan_dirs_by_root: Dictionary mapping repository root to set of scan directories
        
        Example:
            >>> grouper = RepositoryGrouper()
            >>> files = [
            ...     {'path': '/repo/src/file1.py', 'root': '/repo'},
            ...     {'path': '/repo/src/file2.py', 'root': '/repo'}
            ... ]
            >>> files_by_root, scan_dirs = grouper.group_by_repository(files)
            >>> files_by_root['/repo']
            [{'path': '/repo/src/file1.py', 'root': '/repo'}, ...]
        """
        files_by_root = defaultdict(list)
        scan_dirs_by_root = defaultdict(set)
        
        for file in files:
            # Get repository root, default to empty string if not present
            repo_root = file.get('root', '')
            
            # Add file to the appropriate repository group
            files_by_root[repo_root].append(file)
            
            # Track this repository root as a scan directory
            scan_dirs_by_root[repo_root].add(repo_root)
        
        # Convert defaultdicts to regular dicts for cleaner API
        return dict(files_by_root), dict(scan_dirs_by_root)
