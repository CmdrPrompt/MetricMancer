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
        # Cache för olika typer av git-data
        self.ownership_cache: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.churn_cache: Dict[str, Dict[str, int]] = {}
        self.blame_cache: Dict[str, Dict[str, str]] = {}  # Rå git blame output
        self.tracked_files_cache: Dict[str, Set[str]] = {}
        
        # Cache för git-kommandon som används av flera KPIs
        self._ls_files_cache: Dict[str, Set[str]] = {}
        
    def clear_cache(self, repo_root: Optional[str] = None):
        """Rensa cache för en specifik repo eller hela cachen."""
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
        Kontrollera om en fil är tracked av git.
        Använder cache för att undvika upprepade git ls-files anrop.
        """
        # Normalisera paths
        repo_root = os.path.abspath(repo_root)
        
        # Kontrollera cache först
        if repo_root in self.tracked_files_cache:
            return file_path in self.tracked_files_cache[repo_root]
        
        # Om inte cached, hämta alla tracked files för repo
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
        Hämta git blame output för en fil.
        Använder cache för att undvika upprepade git blame anrop.
        """
        repo_root = os.path.abspath(repo_root)
        
        # Kontrollera cache först
        repo_blame_cache = self.blame_cache.setdefault(repo_root, {})
        if file_path in repo_blame_cache:
            debug_print(f"[CACHE] Hit: git blame for {file_path}")
            return repo_blame_cache[file_path]
        
        # Kontrollera om filen finns och är tracked
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
        """Rensa all cache-data"""
        self.blame_cache.clear()
        self.ownership_cache.clear()
        self.churn_cache.clear()
        self.tracked_files_cache.clear()
        debug_print("[CACHE] All caches cleared")

    def get_ownership_data(self, repo_root: str, file_path: str) -> Dict[str, Any]:
        """
        Hämta ownership data för en fil.
        Returnerar: {author: ownership_percent} eller {"ownership": "N/A"}
        """
        repo_root = os.path.abspath(repo_root)
        
        # Kontrollera cache först
        repo_ownership_cache = self.ownership_cache.setdefault(repo_root, {})
        if file_path in repo_ownership_cache:
            debug_print(f"[CACHE] Hit: ownership data for {file_path}")
            return repo_ownership_cache[file_path]
        
        # Skip node_modules och liknande
        if 'node_modules' in file_path:
            result = {}  # Använd tom dict istället för {"ownership": "N/A"}
            repo_ownership_cache[file_path] = result
            return result
        
        # Hämta git blame data
        blame_output = self.get_git_blame(repo_root, file_path)
        if blame_output is None:
            result = {}  # Använd tom dict istället för {"ownership": "N/A"}
            repo_ownership_cache[file_path] = result
            return result
        
        try:
            # Parsea blame output för att få författare
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
            result = {}  # Använd tom dict istället för {"ownership": "N/A"}
            repo_ownership_cache[file_path] = result
            return result
    
    def get_churn_data(self, repo_root: str, file_path: str) -> int:
        """
        Hämta churn data för en fil.
        Returnerar antal commits som påverkade filen.
        """
        repo_root = os.path.abspath(repo_root)
        
        # Kontrollera cache först
        repo_churn_cache = self.churn_cache.setdefault(repo_root, {})
        if file_path in repo_churn_cache:
            debug_print(f"[CACHE] Hit: churn data for {file_path}")
            return repo_churn_cache[file_path]
        
        # Implementera churn-beräkning här eller delegera till befintlig kod
        # För nu returnerar vi 0 som placeholder
        debug_print(f"[CACHE] Miss: churn data for {file_path} (placeholder)")
        result = 0
        repo_churn_cache[file_path] = result
        return result
    
    def prefetch_ownership_data(self, repo_root: str, file_paths: list[str]):
        """
        Förhämta ownership data för flera filer i batch.
        Detta är optimering för att minska antalet git-anrop.
        """
        repo_root = os.path.abspath(repo_root)
        debug_print(f"[CACHE] Prefetching ownership data for {len(file_paths)} files")
        
        # Filtrera bort redan cachade filer
        repo_ownership_cache = self.ownership_cache.setdefault(repo_root, {})
        uncached_files = [fp for fp in file_paths if fp not in repo_ownership_cache]
        
        if not uncached_files:
            debug_print("[CACHE] All files already cached")
            return
        
        debug_print(f"[CACHE] Need to fetch {len(uncached_files)} uncached files")
        
        # Hämta data för alla uncached filer
        for file_path in uncached_files:
            self.get_ownership_data(repo_root, file_path)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Returnera statistik om cache-användning."""
        stats = {
            "repos_cached": len(self.ownership_cache),
            "total_ownership_entries": sum(len(repo_cache) for repo_cache in self.ownership_cache.values()),
            "total_churn_entries": sum(len(repo_cache) for repo_cache in self.churn_cache.values()),
            "total_blame_entries": sum(len(repo_cache) for repo_cache in self.blame_cache.values()),
            "total_tracked_files": sum(len(files) for files in self.tracked_files_cache.values())
        }
        return stats


# Singleton instance för att dela mellan KPIs
_git_cache_instance = None


def get_git_cache() -> GitDataCache:
    """Returnera singleton-instansen av GitDataCache."""
    global _git_cache_instance
    if _git_cache_instance is None:
        _git_cache_instance = GitDataCache()
        debug_print("[CACHE] Created new GitDataCache instance")
    return _git_cache_instance