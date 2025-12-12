

"""
Helper functions for git operations
"""

import os
import subprocess
from typing import List, Optional
from src.utilities.debug import debug_print


def run_git_command(repo_root: str, args: list[str]) -> Optional[str]:
    """
    Run a git command with consistent error handling.

    This is a centralized helper for executing git commands across the codebase.
    It normalizes the repo path and provides consistent error handling.

    Args:
        repo_root: Root directory of the git repository
        args: List of git command arguments (e.g., ['ls-files'], ['blame', 'file.py'])

    Returns:
        Command stdout output as string, or None on error

    Example:
        >>> run_git_command("/my/repo", ["ls-files"])
        "file1.py\nfile2.py\n..."
        >>> run_git_command("/my/repo", ["blame", "--line-porcelain", "main.py"])
        "<blame output>"
    """
    repo_root = os.path.abspath(repo_root)

    try:
        result = subprocess.run(
            ['git', '-C', repo_root] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        debug_print(f"[GIT] Command failed: git {' '.join(args)} - {e}")
        return None
    except PermissionError as e:
        debug_print(f"[GIT] Permission denied: {e}")
        return None
    except Exception as e:
        debug_print(f"[GIT] Unexpected error running git command: {e}")
        return None


def find_git_repo_root(start_path: str) -> str:
    """
    Find the root of a git repository by traversing up the filesystem
    from a given starting point and looking for a .git directory.

    Args:
        start_path: The path to start searching from.

    Returns:
        The absolute path to the git repository root, or the original
        start_path if no .git repository is found.
    """
    current = os.path.abspath(start_path)
    while True:
        if os.path.isdir(os.path.join(current, '.git')):
            debug_print(f"[DEBUG] find_git_repo_root: Found .git at {current}")
            return current
        parent = os.path.dirname(current)
        if parent == current:
            # Reached filesystem root
            debug_print(f"[DEBUG] find_git_repo_root: No .git found. Returning original path {start_path}")
            return os.path.abspath(start_path)  # Fallback
        current = parent


def _get_current_branch_name(repo_root: str) -> str:
    """
    Get the name of the current git branch.

    Args:
        repo_root: Path to the git repository root

    Returns:
        Current branch name

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    result = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def _get_changed_files_on_base_branch(repo_root: str) -> List[str]:
    """
    Get files changed in recent commits when on base branch.

    Args:
        repo_root: Path to the git repository root

    Returns:
        List of changed file paths
    """
    # Get files changed in last 10 commits
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD~10..HEAD'],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True
    )
    return _process_git_output_to_files(result.stdout, repo_root)


def _get_changed_files_vs_base_branch(repo_root: str, base_branch: str) -> List[str]:
    """
    Get files changed compared to base branch.

    Args:
        repo_root: Path to the git repository root
        base_branch: Base branch to compare against

    Returns:
        List of changed file paths
    """
    result = subprocess.run(
        ['git', 'diff', '--name-only', f'{base_branch}...HEAD'],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True
    )
    return _process_git_output_to_files(result.stdout, repo_root)


def _process_git_output_to_files(git_output: str, repo_root: str) -> List[str]:
    """
    Process git command output into absolute file paths.

    Args:
        git_output: Raw output from git command
        repo_root: Path to the git repository root

    Returns:
        List of absolute file paths
    """
    files = [f.strip() for f in git_output.strip().split('\n') if f.strip()]
    return [os.path.join(repo_root, f) for f in files]


def get_changed_files_in_branch(repo_path: str, base_branch: str = "main") -> List[str]:
    """
    Get list of files changed in the current branch compared to base branch.

    Args:
        repo_path: Path to the git repository
        base_branch: Base branch to compare against (default: "main")

    Returns:
        List of file paths that have been changed
    """
    try:
        repo_root = find_git_repo_root(repo_path)
        debug_print(f"[DEBUG] get_changed_files_in_branch: repo_root={repo_root}")

        # Get current branch name
        current_branch = _get_current_branch_name(repo_root)
        debug_print(f"[DEBUG] get_changed_files_in_branch: current_branch={current_branch}")

        # Get changed files based on branch context
        if current_branch == base_branch:
            debug_print("[DEBUG] get_changed_files_in_branch: On base branch, getting recent commits")
            absolute_files = _get_changed_files_on_base_branch(repo_root)
        else:
            debug_print(f"[DEBUG] get_changed_files_in_branch: Comparing to {base_branch}")
            absolute_files = _get_changed_files_vs_base_branch(repo_root, base_branch)

        debug_print(f"[DEBUG] get_changed_files_in_branch: Found {len(absolute_files)} changed files")
        return absolute_files

    except subprocess.CalledProcessError as e:
        debug_print(f"[DEBUG] get_changed_files_in_branch: Git command failed: {e}")
        return []
    except Exception as e:
        debug_print(f"[DEBUG] get_changed_files_in_branch: Error: {e}")
        return []


def get_current_branch(repo_path: str) -> Optional[str]:
    """
    Get the name of the current git branch.

    Args:
        repo_path: Path to the git repository

    Returns:
        Current branch name or None if not in a git repo
    """
    try:
        repo_root = find_git_repo_root(repo_path)
        return _get_current_branch_name(repo_root)
    except Exception as e:
        debug_print(f"[DEBUG] get_current_branch: Error: {e}")
        return None
