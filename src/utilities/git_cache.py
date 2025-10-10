"""
Git Data Cache
--------------
Shared cache for git data to minimize redundant git calls across KPIs.
Implements the cache design from Issue #38.
"""
from typing import Dict, Optional, Any, Set
import os
import subprocess
from collections import Counter
from src.utilities.debug import debug_print


class GitDataCache:
    """
    Centralized cache for git data used by multiple KPIs.
    
    Cache structure:
    - ownership_cache = {repo_root: {file_path: {author: ownership_percent}}}
    - churn_cache = {repo_root: {file_path: churn_value}}
    - blame_cache = {repo_root: {file_path: blame_data}}
    - tracked_files_cache = {repo_root: set(tracked_files)}
    """
    
    def __init__(self):
        # Cache for different types of git data
        self.ownership_cache: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.churn_cache: Dict[str, Dict[str, int]] = {}
        self.blame_cache: Dict[str, Dict[str, str]] = {}  # Raw git blame output
        self.tracked_files_cache: Dict[str, Set[str]] = {}
        
        # Cache for git commands used by multiple KPIs
        self._ls_files_cache: Dict[str, Set[str]] = {}
        
    def clear_cache(self, repo_root: Optional[str] = None):
        """Clear cache for a specific repo or the entire cache."""
        if repo_root:
            self.ownership_cache.pop(repo_root, None)
            self.churn_cache.pop(repo_root, None)
            self.blame_cache.pop(repo_root, None)
            self.tracked_files_cache.pop(repo_root, None)
            self._ls_files_cache.pop(repo_root, None)
            debug_print(f"[CACHE] Cleared cache for repo: {repo_root}")
        else:
            self.ownership_cache.clear()
            self.churn_cache.clear()
            self.blame_cache.clear()
            self.tracked_files_cache.clear()
            self._ls_files_cache.clear()
            debug_print("[CACHE] Cleared all caches")
    
    def is_file_tracked(self, repo_root: str, file_path: str) -> bool:
        """
        Check if a file is tracked by git.
        Uses cache to avoid repeated git ls-files calls.
        """
        # Normalize paths
        repo_root = os.path.abspath(repo_root)
        
        # Check cache first
        if repo_root in self.tracked_files_cache:
            return file_path in self.tracked_files_cache[repo_root]
        
        # If not cached, fetch all tracked files for repo
        try:
            debug_print(f"[CACHE] Fetching tracked files for repo: {repo_root}")
            result = subprocess.run(
                ['git', '-C', repo_root, 'ls-files'],
                capture_output=True,
                text=True,
                check=True
            )
            tracked_files = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            self.tracked_files_cache[repo_root] = tracked_files
            debug_print(f"[CACHE] Cached {len(tracked_files)} tracked files for repo: {repo_root}")
            return file_path in tracked_files
        except Exception as e:
            debug_print(f"[CACHE] Error fetching tracked files for {repo_root}: {e}")
            return False
    
    def get_git_blame(self, repo_root: str, file_path: str) -> Optional[str]:
        """
        Get git blame output for a file.
        Uses cache to avoid repeated git blame calls.
        """
        repo_root = os.path.abspath(repo_root)
        
        # Check cache first
        repo_blame_cache = self.blame_cache.setdefault(repo_root, {})
        if file_path in repo_blame_cache:
            debug_print(f"[CACHE] Hit: git blame for {file_path}")
            return repo_blame_cache[file_path]
        
        # Check if file exists and is tracked
        full_file_path = os.path.join(repo_root, file_path)
        if not os.path.exists(full_file_path) or not self.is_file_tracked(repo_root, file_path):
            repo_blame_cache[file_path] = None
            return None
        
        try:
            debug_print(f"[CACHE] Miss: fetching git blame for {file_path}")
            blame_output = subprocess.check_output(
                ['git', '-C', repo_root, 'blame', '--line-porcelain', file_path],
                text=True
            )
            repo_blame_cache[file_path] = blame_output
            debug_print(f"[CACHE] Cached git blame for {file_path}")
            return blame_output
        except Exception as e:
            debug_print(f"[CACHE] Error getting git blame for {file_path}: {e}")
            repo_blame_cache[file_path] = None
            return None
    
    def clear_cache(self):
        """Clear all cache data"""
        self.blame_cache.clear()
        self.ownership_cache.clear()
        self.churn_cache.clear()
        self.tracked_files_cache.clear()
        debug_print("[CACHE] All caches cleared")

    def get_ownership_data(self, repo_root: str, file_path: str) -> Dict[str, Any]:
        """
        Get ownership data for a file.
        Returns: {author: ownership_percent} or {"ownership": "N/A"}
        """
        repo_root = os.path.abspath(repo_root)
        
        # Check cache first
        repo_ownership_cache = self.ownership_cache.setdefault(repo_root, {})
        if file_path in repo_ownership_cache:
            debug_print(f"[CACHE] Hit: ownership data for {file_path}")
            return repo_ownership_cache[file_path]
        
        # Skip node_modules and similar
        if 'node_modules' in file_path:
            result = {}  # Use empty dict instead of {"ownership": "N/A"}
            repo_ownership_cache[file_path] = result
            return result
        
        # Get git blame data
        blame_output = self.get_git_blame(repo_root, file_path)
        if blame_output is None:
            result = {}  # Use empty dict instead of {"ownership": "N/A"}
            repo_ownership_cache[file_path] = result
            return result
        
        try:
            # Parse blame output to get authors
            authors = [line[7:] for line in blame_output.splitlines() if line.startswith('author ')]
            total_lines = len(authors)
            
            if total_lines == 0:
                result = {}
            else:
                counts = Counter(authors)
                result = {author: round(count / total_lines * 100, 1) for author, count in counts.items()}
            
            debug_print(f"[CACHE] Calculated ownership for {file_path}: {len(result)} authors")
            repo_ownership_cache[file_path] = result
            return result
            
        except Exception as e:
            debug_print(f"[CACHE] Error calculating ownership for {file_path}: {e}")
            result = {}  # Use empty dict instead of {"ownership": "N/A"}
            repo_ownership_cache[file_path] = result
            return result
    
    def get_churn_data(self, repo_root: str, file_path: str) -> int:
        """
        Get churn data for a file.
        Returns number of commits that affected the file.
        """
        repo_root = os.path.abspath(repo_root)
        
        # Check cache first
        repo_churn_cache = self.churn_cache.setdefault(repo_root, {})
        if file_path in repo_churn_cache:
            debug_print(f"[CACHE] Hit: churn data for {file_path}")
            return repo_churn_cache[file_path]
        
        # Check if file exists and is tracked
        full_file_path = os.path.join(repo_root, file_path)
        if not os.path.exists(full_file_path) or not self.is_file_tracked(repo_root, file_path):
            repo_churn_cache[file_path] = 0
            return 0
        
        try:
            # Use git log to count commits that affected the file
            debug_print(f"[CACHE] Miss: calculating churn for {file_path}")
            result = subprocess.run(
                ['git', '-C', repo_root, 'log', '--oneline', '--', file_path],
                capture_output=True,
                text=True,
                check=True
            )
            churn_count = len([line for line in result.stdout.strip().split('\n') if line.strip()])
            debug_print(f"[CACHE] Calculated churn for {file_path}: {churn_count} commits")
            repo_churn_cache[file_path] = churn_count
            return churn_count
        except Exception as e:
            debug_print(f"[CACHE] Error calculating churn for {file_path}: {e}")
            repo_churn_cache[file_path] = 0
            return 0
    
    def prefetch_ownership_data(self, repo_root: str, file_paths: list[str]):
        """
        Prefetch ownership data for multiple files in batch.
        This is optimization to reduce the number of git calls.
        """
        repo_root = os.path.abspath(repo_root)
        debug_print(f"[CACHE] Prefetching ownership data for {len(file_paths)} files")
        
        # Filter out already cached files
        repo_ownership_cache = self.ownership_cache.setdefault(repo_root, {})
        uncached_files = [fp for fp in file_paths if fp not in repo_ownership_cache]
        
        if not uncached_files:
            debug_print("[CACHE] All files already cached")
            return
        
        debug_print(f"[CACHE] Need to fetch {len(uncached_files)} uncached files")
        
        # Fetch data for all uncached files
        for file_path in uncached_files:
            self.get_ownership_data(repo_root, file_path)
    
    def prefetch_churn_data(self, repo_root: str, file_paths: list[str]):
        """
        Prefetch churn data for multiple files in batch.
        This is optimization to reduce the number of git calls.
        """
        repo_root = os.path.abspath(repo_root)
        debug_print(f"[CACHE] Prefetching churn data for {len(file_paths)} files")
        
        # Filter out already cached files
        repo_churn_cache = self.churn_cache.setdefault(repo_root, {})
        uncached_files = [fp for fp in file_paths if fp not in repo_churn_cache]
        
        if not uncached_files:
            debug_print("[CACHE] All churn files already cached")
            return
        
        debug_print(f"[CACHE] Need to fetch churn for {len(uncached_files)} uncached files")
        
        # Fetch data for all uncached files
        for file_path in uncached_files:
            self.get_churn_data(repo_root, file_path)
    
    def prebuild_cache_for_files(self, repo_root: str, file_paths: list[str]):
        """
        Pre-build cache for all files efficiently using bulk git operations (Issue #40).
        This method builds the cache before KPI calculations start, reducing individual git calls.
        """
        repo_root = os.path.abspath(repo_root)
        debug_print(f"[CACHE] Pre-building cache for {len(file_paths)} files")
        
        # Step 1: Pre-populate tracked files cache efficiently
        try:
            debug_print(f"[CACHE] Pre-building tracked files cache for repo: {repo_root}")
            result = subprocess.run(
                ['git', '-C', repo_root, 'ls-files'],
                capture_output=True,
                text=True,
                check=True
            )
            tracked_files = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            self.tracked_files_cache[repo_root] = tracked_files
            debug_print(f"[CACHE] Pre-built tracked files cache with {len(tracked_files)} files")
        except Exception as e:
            debug_print(f"[CACHE] Error pre-building tracked files: {e}")
            return
        
        # Step 2: Filter to only tracked files from our file list
        valid_files = [fp for fp in file_paths if fp in tracked_files]
        debug_print(f"[CACHE] {len(valid_files)} of {len(file_paths)} files are tracked by git")
        
        # Step 3: Pre-build ownership data efficiently
        repo_ownership_cache = self.ownership_cache.setdefault(repo_root, {})
        repo_blame_cache = self.blame_cache.setdefault(repo_root, {})
        
        uncached_ownership_files = [fp for fp in valid_files if fp not in repo_ownership_cache]
        debug_print(f"[CACHE] Pre-building ownership for {len(uncached_ownership_files)} uncached files")
        
        for file_path in uncached_ownership_files:
            try:
                # Get blame data
                blame_output = subprocess.check_output(
                    ['git', '-C', repo_root, 'blame', '--line-porcelain', file_path],
                    text=True
                )
                repo_blame_cache[file_path] = blame_output
                
                # Calculate ownership from blame
                authors = [line[7:] for line in blame_output.splitlines() if line.startswith('author ')]
                total_lines = len(authors)
                
                if total_lines == 0:
                    ownership_result = {}
                else:
                    from collections import Counter
                    counts = Counter(authors)
                    ownership_result = {author: round(count / total_lines * 100, 1) for author, count in counts.items()}
                
                repo_ownership_cache[file_path] = ownership_result
                debug_print(f"[CACHE] Pre-built ownership for {file_path}: {len(ownership_result)} authors")
                
            except Exception as e:
                debug_print(f"[CACHE] Error pre-building ownership for {file_path}: {e}")
                repo_ownership_cache[file_path] = {}
                repo_blame_cache[file_path] = None
        
        # Step 4: Pre-build churn data efficiently
        repo_churn_cache = self.churn_cache.setdefault(repo_root, {})
        uncached_churn_files = [fp for fp in valid_files if fp not in repo_churn_cache]
        debug_print(f"[CACHE] Pre-building churn for {len(uncached_churn_files)} uncached files")
        
        for file_path in uncached_churn_files:
            try:
                result = subprocess.run(
                    ['git', '-C', repo_root, 'log', '--oneline', '--', file_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                churn_count = len([line for line in result.stdout.strip().split('\n') if line.strip()])
                repo_churn_cache[file_path] = churn_count
                debug_print(f"[CACHE] Pre-built churn for {file_path}: {churn_count} commits")
                
            except Exception as e:
                debug_print(f"[CACHE] Error pre-building churn for {file_path}: {e}")
                repo_churn_cache[file_path] = 0
        
        debug_print(f"[CACHE] Pre-building completed for {len(valid_files)} files")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Return statistics about cache usage."""
        stats = {
            "repos_cached": len(self.ownership_cache),
            "total_ownership_entries": sum(len(repo_cache) for repo_cache in self.ownership_cache.values()),
            "total_churn_entries": sum(len(repo_cache) for repo_cache in self.churn_cache.values()),
            "total_blame_entries": sum(len(repo_cache) for repo_cache in self.blame_cache.values()),
            "total_tracked_files": sum(len(files) for files in self.tracked_files_cache.values())
        }
        return stats


# Singleton instance to share between KPIs
_git_cache_instance = None


def get_git_cache() -> GitDataCache:
    """Return singleton instance of GitDataCache."""
    global _git_cache_instance
    if _git_cache_instance is None:
        _git_cache_instance = GitDataCache()
        debug_print("[CACHE] Created new GitDataCache instance")
    return _git_cache_instance