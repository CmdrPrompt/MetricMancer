"""
Service for detecting changed files in git repositories.

This service encapsulates git change detection logic, improving separation
of concerns and testability.
"""

from typing import Optional, Tuple, List
from src.utilities.git_helpers import get_current_branch, get_changed_files_in_branch
from src.app.infrastructure.exception_handler import ExceptionHandler


class FileChangeDetector:
    """
    Service for detecting changed files in git branches.

    This class encapsulates the logic for:
    - Detecting the current git branch
    - Finding files changed compared to a base branch
    - Handling git operation failures gracefully
    """

    def __init__(self, repo_path: str):
        """
        Initialize FileChangeDetector.

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = repo_path

    def get_changed_files(self, base_branch: str = 'main') -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Get list of changed files compared to base branch.

        Args:
            base_branch: Base branch to compare against (default: 'main')

        Returns:
            Tuple of (current_branch, changed_files_list)
            Returns (None, None) if git operations fail

        Example:
            detector = FileChangeDetector('/path/to/repo')
            current_branch, changed_files = detector.get_changed_files(base_branch='main')
            if current_branch:
                print(f"Branch: {current_branch}")
                print(f"Changed files: {changed_files}")
        """
        result = ExceptionHandler.handle_git_operation(
            "determine changed files",
            self._get_changed_files_impl,
            base_branch
        )
        return result if result else (None, None)

    def _get_changed_files_impl(self, base_branch: str) -> Tuple[str, List[str]]:
        """
        Implementation of changed file detection.

        Args:
            base_branch: Base branch to compare against

        Returns:
            Tuple of (current_branch, changed_files_list)

        Raises:
            Exception: If git operations fail
        """
        current_branch = get_current_branch(self.repo_path)
        changed_files = get_changed_files_in_branch(
            repo_path=self.repo_path,
            base_branch=base_branch
        )
        return current_branch, changed_files
