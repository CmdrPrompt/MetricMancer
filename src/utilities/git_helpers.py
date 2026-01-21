

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


# ============================================================================
# Coupling Analysis Functions (Phase 1: Change-Coupled Hotspots)
# ============================================================================

def get_commit_history(
    repo_root: str,
    since_date: str = "90 days ago",
    exclude_merges: bool = True
) -> List[dict]:
    """
    Extract commit history with changed files for coupling analysis.
    
    This function retrieves git commit history including the files changed
    in each commit, which is used to detect temporal coupling (files that
    change together).
    
    Args:
        repo_root: Root directory of the git repository
        since_date: Time period for history (e.g., "90 days ago", "6 months ago")
        exclude_merges: Whether to exclude merge commits (default: True)
    
    Returns:
        List of commit dictionaries with structure:
        [{
            'commit_hash': str,
            'timestamp': int,
            'author': str,
            'changed_files': List[str]
        }]
        
        Returns empty list if no commits found or git command fails.
    
    Example:
        >>> history = get_commit_history("/my/repo", since_date="30 days ago")
        >>> len(history)
        45
        >>> history[0]['author']
        'John Doe'
        >>> len(history[0]['changed_files'])
        3
    """
    repo_root = os.path.abspath(repo_root)
    
    try:
        # Build git log command
        cmd = [
            'log',
            f'--since={since_date}',
            '--pretty=format:%H|%at|%an',
            '--name-only'
        ]
        
        if exclude_merges:
            cmd.append('--no-merges')
        
        output = run_git_command(repo_root, cmd)
        
        if not output:
            return []
        
        # Parse output
        commits = []
        lines = output.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check if this is a commit header line (contains |)
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    commit_hash = parts[0]
                    timestamp = int(parts[1])
                    author = '|'.join(parts[2:])  # Handle names with |
                    
                    # Collect changed files (lines after commit header until next commit or blank)
                    changed_files = []
                    i += 1
                    
                    while i < len(lines):
                        file_line = lines[i].strip()
                        if not file_line:
                            break
                        if '|' in file_line and len(file_line.split('|')) >= 3:
                            # This is the next commit header
                            break
                        changed_files.append(file_line)
                        i += 1
                    
                    if changed_files:  # Only add commits that have changed files
                        commits.append({
                            'commit_hash': commit_hash,
                            'timestamp': timestamp,
                            'author': author,
                            'changed_files': changed_files
                        })
                    continue
            
            i += 1
        
        return commits
        
    except Exception as e:
        debug_print(f"[GIT] Error getting commit history: {e}")
        return []


def get_changed_files_in_commit(
    repo_root: str,
    commit_hash: str
) -> List[str]:
    """
    Get list of files changed in a specific commit.
    
    Args:
        repo_root: Root directory of the git repository
        commit_hash: Git commit hash
    
    Returns:
        List of file paths (relative to repo root) that were changed in the commit.
        Returns empty list if commit not found or error occurs.
    
    Raises:
        subprocess.CalledProcessError: If commit hash is invalid
    
    Example:
        >>> files = get_changed_files_in_commit("/my/repo", "abc123def")
        >>> files
        ['src/main.py', 'tests/test_main.py']
    """
    repo_root = os.path.abspath(repo_root)
    
    try:
        # Use git show with --name-only to get just filenames
        output = run_git_command(
            repo_root,
            ['show', '--name-only', '--pretty=format:', commit_hash]
        )
        
        if not output:
            raise subprocess.CalledProcessError(1, 'git show')
        
        # Filter out empty lines and return
        files = [line.strip() for line in output.strip().split('\n') if line.strip()]
        return files
        
    except Exception as e:
        debug_print(f"[GIT] Error getting changed files for commit {commit_hash}: {e}")
        raise


def get_commits_affecting_file(
    repo_root: str,
    file_path: str,
    since_date: str = "90 days ago"
) -> List[str]:
    """
    Get all commits that modified a specific file within a time period.
    
    This is used to calculate how frequently a file changes, which is
    needed for coupling analysis.
    
    Args:
        repo_root: Root directory of the git repository
        file_path: Path to file (relative to repo root)
        since_date: Time period for history (e.g., "90 days ago")
    
    Returns:
        List of commit hashes (full 40-char hashes) that modified the file.
        Returns empty list if file has no commits or doesn't exist.
    
    Example:
        >>> commits = get_commits_affecting_file("/my/repo", "src/main.py", "30 days ago")
        >>> len(commits)
        15
        >>> len(commits[0])
        40  # Full commit hash
    """
    repo_root = os.path.abspath(repo_root)
    
    try:
        output = run_git_command(
            repo_root,
            ['log', f'--since={since_date}', '--pretty=format:%H', '--', file_path]
        )
        
        if not output:
            return []
        
        # Split by newline and filter empty lines
        commits = [line.strip() for line in output.strip().split('\n') if line.strip()]
        return commits
        
    except Exception as e:
        debug_print(f"[GIT] Error getting commits for file {file_path}: {e}")
        return []
