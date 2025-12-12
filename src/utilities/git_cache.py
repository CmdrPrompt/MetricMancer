"""
Git Data Cache
--------------
Shared cache for git data to minimize redundant git calls across KPIs.
Implements the cache design from Issue #38.
"""
from typing import Dict, Optional, Any, Set
import os
from collections import Counter
from src.utilities.debug import debug_print
from src.utilities.git_helpers import run_git_command


class GitDataCache:
    """
    Centralized cache for git data used by multiple KPIs.

    Cache structure:
    - ownership_cache = {repo_root: {file_path: {author: ownership_percent}}}
    - churn_cache = {repo_root: {file_path: churn_value}}
    - blame_cache = {repo_root: {file_path: blame_data}}
    - tracked_files_cache = {repo_root: set(tracked_files)}

    Helper Methods (organized by function):

    Path and Cache Management:
        - _normalize_repo_path(): Centralized path normalization (eliminates 8x duplication)
        - _get_repo_cache(): Centralized cache dictionary access (eliminates 8x duplication)

    Logging and Debugging:
        - _log_cache_access(): Standardized cache hit/miss logging (eliminates 5x duplication)

    Git Command Execution:
        - _run_git_command(): Centralized git command execution with error handling

    Data Calculation:
        - _calculate_ownership_from_blame(): Extract ownership percentages from blame output
        - _calculate_churn(): Calculate churn count for a file within time period
    """

    def __init__(self, churn_period_days: int = 30):
        # Cache for different types of git data
        self.ownership_cache: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.churn_cache: Dict[str, Dict[str, int]] = {}
        self.blame_cache: Dict[str, Dict[str, str]] = {}  # Raw git blame output
        self.tracked_files_cache: Dict[str, Set[str]] = {}

        # Cache for git commands used by multiple KPIs
        self._ls_files_cache: Dict[str, Set[str]] = {}

        # Churn calculation settings
        self.churn_period_days = churn_period_days

    # ============================================================================
    # Path and Cache Management Helpers
    # ============================================================================

    def _normalize_repo_path(self, repo_root: str) -> str:
        """
        Normalize repository path to absolute path.

        This helper eliminates duplicated path normalization across 8 methods.
        Ensures consistent path handling for cache dictionary keys.

        Args:
            repo_root: Repository path (relative or absolute)

        Returns:
            Absolute path to repository

        Example:
            >>> cache._normalize_repo_path("./my_repo")
            "/workspaces/MetricMancer/my_repo"
            >>> cache._normalize_repo_path("/absolute/path")
            "/absolute/path"
        """
        return os.path.abspath(repo_root)

    def _get_repo_cache(self, cache_dict: Dict, repo_root: str) -> Dict:
        """
        Get or create a repo-specific cache dictionary.

        This helper eliminates duplicated cache.setdefault() calls across 8 methods.
        Automatically normalizes the repo_root path before accessing the cache.

        Args:
            cache_dict: The cache dictionary (e.g., self.ownership_cache, self.churn_cache)
            repo_root: Repository path (will be normalized to absolute path)

        Returns:
            The repo-specific cache dictionary (creates empty dict if not exists)

        Example:
            >>> repo_cache = cache._get_repo_cache(cache.ownership_cache, "/my/repo")
            >>> repo_cache["file.py"] = {"Alice": 100.0}
            >>> # Later access returns same dictionary
            >>> same_cache = cache._get_repo_cache(cache.ownership_cache, "/my/repo")
            >>> same_cache["file.py"]
            {"Alice": 100.0}

        Note:
            Uses setdefault() to atomically get-or-create the repo dictionary.
        """
        normalized_root = self._normalize_repo_path(repo_root)
        return cache_dict.setdefault(normalized_root, {})

    # ============================================================================
    # Logging and Debugging Helpers
    # ============================================================================

    def _log_cache_access(self, file_path: str, hit: bool, cache_type: str):
        """
        Log cache access (hit or miss) with consistent formatting.

        This helper standardizes cache logging across 5 access points,
        eliminating duplicated debug_print() calls.

        Args:
            file_path: Path to the file being accessed (relative to repo root)
            hit: True for cache hit, False for cache miss
            cache_type: Type of cache - one of:
                - "ownership" - Code ownership cache
                - "churn" - Code churn cache
                - "git blame" - Raw git blame output cache

        Example:
            >>> cache._log_cache_access("src/main.py", hit=True, cache_type="ownership")
            # Logs: "[CACHE] Hit: ownership data for src/main.py"
            >>> cache._log_cache_access("src/test.py", hit=False, cache_type="churn")
            # Logs: "[CACHE] Miss: churn data for src/test.py"

        Note:
            Git blame uses special formatting without "data" suffix to match
            existing log format conventions.
        """
        status = "Hit" if hit else "Miss"
        # For git blame, don't add "data" suffix to match existing format
        if cache_type == "git blame":
            debug_print(f"[CACHE] {status}: {cache_type} for {file_path}")
        else:
            debug_print(f"[CACHE] {status}: {cache_type} data for {file_path}")

    # ============================================================================
    # Git Command Execution Helpers
    # ============================================================================

    def _run_git_command(self, repo_root: str, args: list[str], check_file: Optional[str] = None) -> Optional[str]:
        """
        Run a git command with consistent error handling.

        Delegates to the centralized run_git_command helper from git_helpers,
        adding optional file tracking check.

        Args:
            repo_root: Root directory of the git repository
            args: List of git command arguments (e.g., ['ls-files'], ['blame', 'file.py'])
            check_file: Optional file path to check if tracked before running command

        Returns:
            Command stdout output as string, or None on error or untracked file
        """
        repo_root = self._normalize_repo_path(repo_root)

        # Check if file is tracked (if check_file provided)
        if check_file and not self.is_file_tracked(repo_root, check_file):
            return None

        return run_git_command(repo_root, args)

    # ============================================================================
    # Data Calculation Helpers
    # ============================================================================

    def _calculate_ownership_from_blame(self, blame_output: str) -> Dict[str, float]:
        """
        Calculate ownership percentages from git blame output.

        This helper extracts author information from git blame's --line-porcelain
        format and calculates each author's percentage of total lines.

        Args:
            blame_output: Raw git blame output in --line-porcelain format
                         (contains 'author <name>' lines for each code line)

        Returns:
            Dictionary mapping author names to ownership percentages (rounded to 1 decimal)
            Empty dict if no author information found

        Example:
            >>> blame_output = "author Alice\nauthor Bob\nauthor Alice\n"
            >>> cache._calculate_ownership_from_blame(blame_output)
            {"Alice": 66.7, "Bob": 33.3}

        Note:
            Uses Counter for efficient author line counting. Percentages are
            rounded to 1 decimal place for consistency with ownership reports.
        """
        authors = [line[7:] for line in blame_output.splitlines() if line.startswith('author ')]
        total_lines = len(authors)

        if total_lines == 0:
            return {}

        counts = Counter(authors)
        return {author: round(count / total_lines * 100, 1) for author, count in counts.items()}

    def _calculate_churn(self, repo_root: str, file_path: str) -> int:
        """
        Calculate churn count for a file within the configured time period.

        This helper uses 'git log --since' to count commits that modified the file
        within the time window specified by self.churn_period_days.

        Args:
            repo_root: Root directory of the git repository (will be normalized)
            file_path: Relative path to the file from repo root

        Returns:
            Number of commits affecting the file in the time period
            Returns 0 if git command fails or file has no history

        Example:
            >>> cache = GitDataCache(churn_period_days=30)
            >>> cache._calculate_churn("/my/repo", "src/main.py")
            15  # File was modified in 15 commits in last 30 days

        Note:
            Time period controlled by self.churn_period_days (default: 30 days).
            Uses --oneline for efficient commit counting without full metadata.
        """
        since_date = f"{self.churn_period_days} days ago"
        output = self._run_git_command(
            repo_root,
            ['log', '--oneline', '--since', since_date, '--', file_path]
        )

        if not output:
            return 0

        return len([line for line in output.strip().split('\n') if line.strip()])

    # ============================================================================
    # Public Cache Operations
    # ============================================================================

    def clear_cache(self, repo_root: Optional[str] = None):
        """Clear cache for a specific repo or the entire cache."""
        if repo_root:
            self._clear_repo_cache(repo_root)
        else:
            self._clear_all_caches()

    def _clear_repo_cache(self, repo_root: str):
        """Clear all caches for a specific repository."""
        self.ownership_cache.pop(repo_root, None)
        self.churn_cache.pop(repo_root, None)
        self.blame_cache.pop(repo_root, None)
        self.tracked_files_cache.pop(repo_root, None)
        self._ls_files_cache.pop(repo_root, None)
        debug_print(f"[CACHE] Cleared cache for repo: {repo_root}")

    def _clear_all_caches(self):
        """Clear all cached data."""
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
        repo_root = self._normalize_repo_path(repo_root)

        # Check cache first
        if repo_root in self.tracked_files_cache:
            return file_path in self.tracked_files_cache[repo_root]

        # If not cached, fetch all tracked files for repo
        debug_print(f"[CACHE] Fetching tracked files for repo: {repo_root}")
        output = self._run_git_command(repo_root, ['ls-files'])

        if output is None:
            debug_print(f"[CACHE] Error fetching tracked files for {repo_root}")
            return False

        tracked_files = set(output.strip().split('\n')) if output.strip() else set()
        self.tracked_files_cache[repo_root] = tracked_files
        debug_print(f"[CACHE] Cached {len(tracked_files)} tracked files for repo: {repo_root}")
        return file_path in tracked_files

    def get_git_blame(self, repo_root: str, file_path: str) -> Optional[str]:
        """
        Get git blame output for a file.
        Uses cache to avoid repeated git blame calls.
        """
        repo_root = self._normalize_repo_path(repo_root)

        # Check cache first
        repo_blame_cache = self._get_repo_cache(self.blame_cache, repo_root)
        if file_path in repo_blame_cache:
            self._log_cache_access(file_path, hit=True, cache_type="git blame")
            return repo_blame_cache[file_path]

        # Check if file exists
        full_file_path = os.path.join(repo_root, file_path)
        if not os.path.exists(full_file_path):
            repo_blame_cache[file_path] = None
            return None

        # Use helper method with tracking check
        self._log_cache_access(file_path, hit=False, cache_type="git blame")
        blame_output = self._run_git_command(
            repo_root,
            ['blame', '--line-porcelain', file_path],
            check_file=file_path
        )

        repo_blame_cache[file_path] = blame_output
        if blame_output:
            debug_print(f"[CACHE] Cached git blame for {file_path}")
        else:
            debug_print(f"[CACHE] Error getting git blame for {file_path}")

        return blame_output

    def get_ownership_data(self, repo_root: str, file_path: str) -> Dict[str, Any]:
        """
        Get ownership data for a file.
        Returns: {author: ownership_percent} or {"ownership": "N/A"}
        """
        repo_root = self._normalize_repo_path(repo_root)

        # Check cache first
        repo_ownership_cache = self._get_repo_cache(self.ownership_cache, repo_root)
        if file_path in repo_ownership_cache:
            self._log_cache_access(file_path, hit=True, cache_type="ownership")
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

        # Calculate ownership using helper method
        result = self._calculate_ownership_from_blame(blame_output)
        debug_print(f"[CACHE] Calculated ownership for {file_path}: {len(result)} authors")
        repo_ownership_cache[file_path] = result
        return result

    def get_churn_data(self, repo_root: str, file_path: str) -> int:
        """
        Get churn data for a file.
        Returns number of commits that affected the file.
        """
        repo_root = self._normalize_repo_path(repo_root)

        # Check cache first
        repo_churn_cache = self._get_repo_cache(self.churn_cache, repo_root)
        if file_path in repo_churn_cache:
            self._log_cache_access(file_path, hit=True, cache_type="churn")
            return repo_churn_cache[file_path]

        # Check if file exists and is tracked
        full_file_path = os.path.join(repo_root, file_path)
        if not os.path.exists(full_file_path) or not self.is_file_tracked(repo_root, file_path):
            repo_churn_cache[file_path] = 0
            return 0

        # Calculate churn using helper method
        self._log_cache_access(file_path, hit=False, cache_type="churn")
        churn_count = self._calculate_churn(repo_root, file_path)
        debug_print(f"[CACHE] Calculated churn for {file_path}: {churn_count} commits")
        repo_churn_cache[file_path] = churn_count
        return churn_count

    def prefetch_ownership_data(self, repo_root: str, file_paths: list[str]):
        """
        Prefetch ownership data for multiple files in batch.
        This is optimization to reduce the number of git calls.
        """
        repo_root = self._normalize_repo_path(repo_root)
        debug_print(f"[CACHE] Prefetching ownership data for {len(file_paths)} files")

        # Filter out already cached files
        repo_ownership_cache = self._get_repo_cache(self.ownership_cache, repo_root)
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
        repo_root = self._normalize_repo_path(repo_root)
        debug_print(f"[CACHE] Prefetching churn data for {len(file_paths)} files")

        # Filter out already cached files
        repo_churn_cache = self._get_repo_cache(self.churn_cache, repo_root)
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
        repo_root = self._normalize_repo_path(repo_root)
        debug_print(f"[CACHE] Pre-building cache for {len(file_paths)} files")

        # Step 1: Pre-populate tracked files cache
        valid_files = self._prebuild_tracked_files_cache(repo_root, file_paths)
        if not valid_files:
            return

        # Step 2: Pre-build ownership and blame data
        self._prebuild_ownership_cache(repo_root, valid_files)

        # Step 3: Pre-build churn data
        self._prebuild_churn_cache(repo_root, valid_files)

        debug_print(f"[CACHE] Pre-building completed for {len(valid_files)} files")

    def _prebuild_tracked_files_cache(self, repo_root: str, file_paths: list[str]) -> list[str]:
        """Pre-build tracked files cache and return list of valid tracked files."""
        debug_print(f"[CACHE] Pre-building tracked files cache for repo: {repo_root}")
        output = self._run_git_command(repo_root, ['ls-files'])

        if output is None:
            debug_print("[CACHE] Error pre-building tracked files")
            return []

        tracked_files = set(output.strip().split('\n')) if output.strip() else set()
        self.tracked_files_cache[repo_root] = tracked_files
        debug_print(f"[CACHE] Pre-built tracked files cache with {len(tracked_files)} files")

        valid_files = [fp for fp in file_paths if fp in tracked_files]
        debug_print(f"[CACHE] {len(valid_files)} of {len(file_paths)} files are tracked by git")
        return valid_files

    def _prebuild_ownership_cache(self, repo_root: str, valid_files: list[str]):
        """Pre-build ownership and blame data for uncached files."""
        repo_ownership_cache = self._get_repo_cache(self.ownership_cache, repo_root)
        repo_blame_cache = self._get_repo_cache(self.blame_cache, repo_root)

        uncached_files = [fp for fp in valid_files if fp not in repo_ownership_cache]
        debug_print(f"[CACHE] Pre-building ownership for {len(uncached_files)} uncached files")

        for file_path in uncached_files:
            self._prebuild_single_file_ownership(repo_root, file_path, repo_ownership_cache, repo_blame_cache)

    def _prebuild_single_file_ownership(self, repo_root: str, file_path: str,
                                        repo_ownership_cache: dict, repo_blame_cache: dict):
        """Pre-build ownership data for a single file."""
        blame_output = self._run_git_command(repo_root, ['blame', '--line-porcelain', file_path])

        if blame_output is None:
            debug_print(f"[CACHE] Error pre-building ownership for {file_path}")
            repo_ownership_cache[file_path] = {}
            repo_blame_cache[file_path] = None
            return

        repo_blame_cache[file_path] = blame_output
        ownership_result = self._calculate_ownership_from_blame(blame_output)
        repo_ownership_cache[file_path] = ownership_result
        debug_print(f"[CACHE] Pre-built ownership for {file_path}: {len(ownership_result)} authors")

    def _prebuild_churn_cache(self, repo_root: str, valid_files: list[str]):
        """Pre-build churn data for uncached files."""
        repo_churn_cache = self._get_repo_cache(self.churn_cache, repo_root)
        uncached_files = [fp for fp in valid_files if fp not in repo_churn_cache]
        debug_print(f"[CACHE] Pre-building churn for {len(uncached_files)} uncached files")

        for file_path in uncached_files:
            churn_count = self._calculate_churn(repo_root, file_path)
            repo_churn_cache[file_path] = churn_count
            debug_print(
                f"[CACHE] Pre-built churn for {file_path}: {churn_count} commits "
                f"(last {self.churn_period_days} days)"
            )

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


def get_git_cache(churn_period_days: int = None) -> GitDataCache:
    """
    Return singleton instance of GitDataCache.

    Args:
        churn_period_days: Number of days for churn calculation (only used when creating new instance)
    """
    global _git_cache_instance
    if _git_cache_instance is None:
        _git_cache_instance = GitDataCache(churn_period_days or 30)
        debug_print(
            f"[CACHE] Created new GitDataCache instance with churn_period={_git_cache_instance.churn_period_days} days"
        )
    elif churn_period_days is not None and _git_cache_instance.churn_period_days != churn_period_days:
        # Update churn period if different and clear churn cache
        debug_print(
            f"[CACHE] Updating churn period from {_git_cache_instance.churn_period_days} to {churn_period_days} days"
        )
        _git_cache_instance.churn_period_days = churn_period_days
        _git_cache_instance.churn_cache.clear()
    return _git_cache_instance
