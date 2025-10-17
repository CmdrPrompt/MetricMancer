"""
Test coverage for git_helpers.py module.

This module tests:
- Git repository root detection
- Directory traversal logic
- Edge cases for git operations
- Error handling for invalid paths
"""

import pytest
import os
import tempfile
from unittest.mock import patch

from src.utilities.git_helpers import find_git_repo_root


class TestGitHelpers:
    """Test cases for git helper functions."""

    def test_find_git_repo_root_with_git_directory(self):
        """Test finding git root when .git directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .git directory
            git_dir = os.path.join(temp_dir, '.git')
            os.makedirs(git_dir)

            # Create a subdirectory to test from
            sub_dir = os.path.join(temp_dir, 'src', 'submodule')
            os.makedirs(sub_dir)

            # Test from subdirectory
            result = find_git_repo_root(sub_dir)

            # Should find the temp_dir as the git root
            assert result == temp_dir

    def test_find_git_repo_root_with_git_directory_from_exact_location(self):
        """Test finding git root when starting from the exact git root."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .git directory
            git_dir = os.path.join(temp_dir, '.git')
            os.makedirs(git_dir)

            # Test from the git root directory itself
            result = find_git_repo_root(temp_dir)

            # Should find the temp_dir as the git root
            assert result == temp_dir

    def test_find_git_repo_root_no_git_directory(self):
        """Test behavior when no .git directory is found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory without .git
            sub_dir = os.path.join(temp_dir, 'no_git_here')
            os.makedirs(sub_dir)

            # Test from subdirectory
            result = find_git_repo_root(sub_dir)

            # Should return the original path as absolute path
            assert result == os.path.abspath(sub_dir)

    def test_find_git_repo_root_nested_directories(self):
        """Test finding git root through multiple nested directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .git directory at root
            git_dir = os.path.join(temp_dir, '.git')
            os.makedirs(git_dir)

            # Create deeply nested subdirectory
            deep_dir = os.path.join(temp_dir, 'level1', 'level2', 'level3', 'level4')
            os.makedirs(deep_dir)

            # Test from deep subdirectory
            result = find_git_repo_root(deep_dir)

            # Should find the temp_dir as the git root
            assert result == temp_dir

    def test_find_git_repo_root_with_relative_path(self):
        """Test finding git root with relative path input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .git directory
            git_dir = os.path.join(temp_dir, '.git')
            os.makedirs(git_dir)

            # Create a subdirectory
            sub_dir = os.path.join(temp_dir, 'src')
            os.makedirs(sub_dir)

            # Change to temp directory and use relative path
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = find_git_repo_root('src')

                # Should find the temp_dir as the git root (normalize paths for macOS)
                assert os.path.realpath(result) == os.path.realpath(temp_dir)
            finally:
                os.chdir(old_cwd)

    def test_find_git_repo_root_from_root_filesystem(self):
        """Test behavior when traversing to filesystem root."""
        # Use a path that definitely doesn't have a .git directory
        # and will traverse to filesystem root
        non_git_path = '/tmp' if os.path.exists('/tmp') else os.path.expanduser('~')

        # Ensure there's no .git in the path we're testing
        test_path = non_git_path
        while os.path.dirname(test_path) != test_path:  # Until we reach root
            if os.path.exists(os.path.join(test_path, '.git')):
                # Skip this test if we accidentally hit a git repo
                pytest.skip("Test path contains a git repository")
            test_path = os.path.dirname(test_path)

        result = find_git_repo_root(non_git_path)

        # Should return the original path as absolute
        assert result == os.path.abspath(non_git_path)

    def test_find_git_repo_root_with_nonexistent_path(self):
        """Test behavior with nonexistent path."""
        nonexistent_path = '/this/path/does/not/exist/anywhere'

        # The function should still work with abspath
        result = find_git_repo_root(nonexistent_path)

        # Should return the absolute version of the nonexistent path
        assert result == os.path.abspath(nonexistent_path)

    @patch('src.utilities.git_helpers.os.path.isdir')
    @patch('src.utilities.git_helpers.os.path.abspath')
    @patch('src.utilities.git_helpers.os.path.dirname')
    def test_find_git_repo_root_with_permission_error(self, mock_dirname, mock_abspath, mock_isdir):
        """Test behavior when directory permissions cause issues."""
        # Setup mocks
        mock_abspath.side_effect = lambda x: f'/abs{x}'
        mock_dirname.side_effect = lambda x: '/parent' if x != '/parent' else '/parent'
        mock_isdir.side_effect = PermissionError("Permission denied")

        # This should handle the permission error gracefully
        with pytest.raises(PermissionError):
            find_git_repo_root('/test/path')

    @patch('src.utilities.git_helpers.debug_print')
    def test_find_git_repo_root_debug_output_found(self, mock_debug_print):
        """Test debug output when git directory is found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .git directory
            git_dir = os.path.join(temp_dir, '.git')
            os.makedirs(git_dir)

            # Test and capture debug output
            find_git_repo_root(temp_dir)

            # Verify debug was called and check that the path contains our temp directory
            assert mock_debug_print.called
            call_args = mock_debug_print.call_args[0][0]
            assert "[DEBUG] find_git_repo_root: Found .git at" in call_args
            assert temp_dir.split('/')[-1] in call_args  # Check temp dir name is in path

    @patch('src.utilities.git_helpers.debug_print')
    def test_find_git_repo_root_debug_output_not_found(self, mock_debug_print):
        """Test debug output when no git directory is found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory without .git
            sub_dir = os.path.join(temp_dir, 'no_git')
            os.makedirs(sub_dir)

            # Test and capture debug output
            find_git_repo_root(sub_dir)

            # Verify debug was called and check the message content
            assert mock_debug_print.called
            call_args = mock_debug_print.call_args[0][0]
            assert "[DEBUG] find_git_repo_root: No .git found. Returning original path" in call_args
            assert "no_git" in call_args  # Check our test directory name is in path

    def test_find_git_repo_root_with_git_file_not_directory(self):
        """Test behavior when .git is a file (like in git worktrees) not a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .git file instead of directory (simulates git worktree)
            git_file = os.path.join(temp_dir, '.git')
            with open(git_file, 'w') as f:
                f.write('gitdir: /some/other/path/.git/worktrees/branch')

            # Create a subdirectory to test from
            sub_dir = os.path.join(temp_dir, 'src')
            os.makedirs(sub_dir)

            # Test from subdirectory - should not find git root since .git is file, not dir
            result = find_git_repo_root(sub_dir)

            # Should return original path since os.path.isdir('.git') will be False
            assert result == os.path.abspath(sub_dir)

    def test_find_git_repo_root_multiple_git_directories(self):
        """Test finding git root when there are nested git repositories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create outer .git directory
            outer_git = os.path.join(temp_dir, '.git')
            os.makedirs(outer_git)

            # Create inner directory structure with its own .git
            inner_repo = os.path.join(temp_dir, 'submodule')
            os.makedirs(inner_repo)
            inner_git = os.path.join(inner_repo, '.git')
            os.makedirs(inner_git)

            # Create test directory inside inner repo
            test_dir = os.path.join(inner_repo, 'src')
            os.makedirs(test_dir)

            # Test from inner test directory
            result = find_git_repo_root(test_dir)

            # Should find the closest git root (inner repo)
            assert result == inner_repo


class TestGitHelpersEdgeCases:
    """Test edge cases and error conditions for git helpers."""

    def test_find_git_repo_root_with_empty_string(self):
        """Test behavior with empty string input."""
        result = find_git_repo_root('')

        # Should handle empty string gracefully
        assert result == os.path.abspath('')

    def test_find_git_repo_root_with_current_directory(self):
        """Test behavior with current directory ('.')."""
        current_dir = os.getcwd()
        result = find_git_repo_root('.')

        # Should return absolute path of current directory or its git root
        assert os.path.isabs(result)
        # Result should either be current dir or a parent directory
        assert result == current_dir or current_dir.startswith(result)

    def test_find_git_repo_root_returns_absolute_path(self):
        """Test that function always returns absolute paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with various input formats
            test_paths = [
                temp_dir,
                os.path.join(temp_dir, 'subdir'),
                '.',
                './',
                '../',
            ]

            for test_path in test_paths:
                if os.path.exists(test_path) or test_path in ['.', './', '../']:
                    result = find_git_repo_root(test_path)
                    assert os.path.isabs(result), f"Result should be absolute path for input: {test_path}"
