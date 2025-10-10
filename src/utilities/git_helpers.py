

"""
Helper functions for git operations
"""

import os
from src.utilities.debug import debug_print


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
