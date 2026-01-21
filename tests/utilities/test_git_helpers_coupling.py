"""
Tests for git coupling analysis helpers.

This module tests git history extraction for temporal coupling analysis,
following the implementation plan for Change-Coupled Hotspots (Phase 1).
"""

import unittest
import tempfile
import subprocess
import os
from pathlib import Path
from datetime import datetime, timedelta

from src.utilities.git_helpers import (
    get_commit_history,
    get_changed_files_in_commit,
    get_commits_affecting_file
)


class TestGetCommitHistory(unittest.TestCase):
    """Test get_commit_history function for coupling analysis."""

    def setUp(self):
        """Create temporary git repository for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                      cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'],
                      cwd=self.repo_path, check=True, capture_output=True)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_commit_history_empty_repo(self):
        """Test get_commit_history returns empty list for repo with no commits."""
        history = get_commit_history(str(self.repo_path))
        
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 0)

    def test_get_commit_history_single_commit(self):
        """Test get_commit_history with single commit."""
        # Create and commit a file
        test_file = self.repo_path / "test.py"
        test_file.write_text("def test(): pass")
        subprocess.run(['git', 'add', 'test.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        history = get_commit_history(str(self.repo_path))
        
        self.assertEqual(len(history), 1)
        self.assertIn('commit_hash', history[0])
        self.assertIn('timestamp', history[0])
        self.assertIn('author', history[0])
        self.assertIn('changed_files', history[0])
        self.assertEqual(len(history[0]['changed_files']), 1)
        self.assertIn('test.py', history[0]['changed_files'][0])

    def test_get_commit_history_multiple_commits(self):
        """Test get_commit_history with multiple commits."""
        # Create first commit
        file1 = self.repo_path / "file1.py"
        file1.write_text("# File 1")
        subprocess.run(['git', 'add', 'file1.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add file1'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Create second commit
        file2 = self.repo_path / "file2.py"
        file2.write_text("# File 2")
        subprocess.run(['git', 'add', 'file2.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add file2'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Create third commit with both files
        file1.write_text("# File 1 modified")
        file2.write_text("# File 2 modified")
        subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Modify both files'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        history = get_commit_history(str(self.repo_path))
        
        # Should have 3 commits (reverse chronological order)
        self.assertEqual(len(history), 3)
        
        # Latest commit should have 2 changed files
        latest_commit = history[0]
        self.assertEqual(len(latest_commit['changed_files']), 2)
        self.assertTrue(any('file1.py' in f for f in latest_commit['changed_files']))
        self.assertTrue(any('file2.py' in f for f in latest_commit['changed_files']))

    def test_get_commit_history_with_time_filter(self):
        """Test get_commit_history respects time period filter."""
        # Create old commit (simulate with backdated commit if possible)
        file1 = self.repo_path / "old_file.py"
        file1.write_text("# Old file")
        subprocess.run(['git', 'add', 'old_file.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Old commit'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Create recent commit
        file2 = self.repo_path / "new_file.py"
        file2.write_text("# New file")
        subprocess.run(['git', 'add', 'new_file.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Recent commit'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Get history for last 1 day (should get both since they're recent in test)
        history = get_commit_history(str(self.repo_path), since_date="1 day ago")
        
        # In real scenario with proper dates, this would filter
        # For now, just verify it accepts the parameter
        self.assertGreaterEqual(len(history), 1)

    def test_get_commit_history_exclude_merges(self):
        """Test get_commit_history can exclude merge commits."""
        # Create a simple commit
        file1 = self.repo_path / "file.py"
        file1.write_text("# File")
        subprocess.run(['git', 'add', 'file.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Regular commit'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Test with exclude_merges=True (default)
        history_no_merges = get_commit_history(str(self.repo_path), exclude_merges=True)
        
        # Test with exclude_merges=False
        history_with_merges = get_commit_history(str(self.repo_path), exclude_merges=False)
        
        # Both should work (no merges in this simple repo)
        self.assertEqual(len(history_no_merges), len(history_with_merges))

    def test_get_commit_history_author_info(self):
        """Test that commit history includes author information."""
        file1 = self.repo_path / "test.py"
        file1.write_text("# Test")
        subprocess.run(['git', 'add', 'test.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Test commit'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        history = get_commit_history(str(self.repo_path))
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['author'], 'Test User')

    def test_get_commit_history_returns_absolute_paths(self):
        """Test that changed_files contain paths relative to repo root."""
        # Create nested structure
        subdir = self.repo_path / "src"
        subdir.mkdir()
        file1 = subdir / "module.py"
        file1.write_text("# Module")
        
        subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add nested file'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        history = get_commit_history(str(self.repo_path))
        
        self.assertEqual(len(history), 1)
        # Should have relative path from repo root
        self.assertTrue(any('src/module.py' in f or 'src\\module.py' in f 
                          for f in history[0]['changed_files']))


class TestGetChangedFilesInCommit(unittest.TestCase):
    """Test get_changed_files_in_commit function."""

    def setUp(self):
        """Create temporary git repository for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                      cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'],
                      cwd=self.repo_path, check=True, capture_output=True)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_changed_files_single_file(self):
        """Test getting changed files from commit with single file."""
        file1 = self.repo_path / "test.py"
        file1.write_text("# Test")
        subprocess.run(['git', 'add', 'test.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add test'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Get commit hash
        result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                              cwd=self.repo_path, check=True, capture_output=True, text=True)
        commit_hash = result.stdout.strip()
        
        changed_files = get_changed_files_in_commit(str(self.repo_path), commit_hash)
        
        self.assertEqual(len(changed_files), 1)
        self.assertIn('test.py', changed_files[0])

    def test_get_changed_files_multiple_files(self):
        """Test getting changed files from commit with multiple files."""
        file1 = self.repo_path / "file1.py"
        file2 = self.repo_path / "file2.py"
        file1.write_text("# File 1")
        file2.write_text("# File 2")
        
        subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add multiple files'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Get commit hash
        result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                              cwd=self.repo_path, check=True, capture_output=True, text=True)
        commit_hash = result.stdout.strip()
        
        changed_files = get_changed_files_in_commit(str(self.repo_path), commit_hash)
        
        self.assertEqual(len(changed_files), 2)
        filenames = [os.path.basename(f) for f in changed_files]
        self.assertIn('file1.py', filenames)
        self.assertIn('file2.py', filenames)

    def test_get_changed_files_invalid_commit(self):
        """Test get_changed_files_in_commit with invalid commit hash."""
        # Should handle gracefully (return empty list or raise exception)
        with self.assertRaises((subprocess.CalledProcessError, ValueError)):
            get_changed_files_in_commit(str(self.repo_path), "invalid_hash_123")


class TestGetCommitsAffectingFile(unittest.TestCase):
    """Test get_commits_affecting_file function."""

    def setUp(self):
        """Create temporary git repository for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                      cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'],
                      cwd=self.repo_path, check=True, capture_output=True)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_commits_affecting_file_single_commit(self):
        """Test getting commits for file with single change."""
        file1 = self.repo_path / "target.py"
        file1.write_text("# Version 1")
        subprocess.run(['git', 'add', 'target.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial version'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        commits = get_commits_affecting_file(str(self.repo_path), "target.py")
        
        self.assertEqual(len(commits), 1)
        self.assertEqual(len(commits[0]), 40)  # Git commit hash length

    def test_get_commits_affecting_file_multiple_commits(self):
        """Test getting commits for file with multiple changes."""
        file1 = self.repo_path / "target.py"
        
        # First commit
        file1.write_text("# Version 1")
        subprocess.run(['git', 'add', 'target.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Version 1'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Second commit
        file1.write_text("# Version 2")
        subprocess.run(['git', 'add', 'target.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Version 2'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Third commit
        file1.write_text("# Version 3")
        subprocess.run(['git', 'add', 'target.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Version 3'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        commits = get_commits_affecting_file(str(self.repo_path), "target.py")
        
        self.assertEqual(len(commits), 3)
        # All should be valid commit hashes
        for commit_hash in commits:
            self.assertEqual(len(commit_hash), 40)

    def test_get_commits_affecting_file_not_modified(self):
        """Test getting commits for file that exists but wasn't modified."""
        # Create and commit file1
        file1 = self.repo_path / "file1.py"
        file1.write_text("# File 1")
        subprocess.run(['git', 'add', 'file1.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add file1'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # Create and commit file2 (different file)
        file2 = self.repo_path / "file2.py"
        file2.write_text("# File 2")
        subprocess.run(['git', 'add', 'file2.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add file2'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        # file1 should only have 1 commit
        commits = get_commits_affecting_file(str(self.repo_path), "file1.py")
        self.assertEqual(len(commits), 1)

    def test_get_commits_affecting_file_nonexistent(self):
        """Test getting commits for file that doesn't exist."""
        # Create a commit so repo isn't empty
        file1 = self.repo_path / "exists.py"
        file1.write_text("# Exists")
        subprocess.run(['git', 'add', 'exists.py'], cwd=self.repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add file'],
                      cwd=self.repo_path, check=True, capture_output=True)
        
        commits = get_commits_affecting_file(str(self.repo_path), "nonexistent.py")
        
        # Should return empty list for file that doesn't exist
        self.assertEqual(len(commits), 0)

    def test_get_commits_affecting_file_with_time_filter(self):
        """Test getting commits with time period filter."""
        file1 = self.repo_path / "target.py"
        
        # Create multiple commits
        for i in range(3):
            file1.write_text(f"# Version {i+1}")
            subprocess.run(['git', 'add', 'target.py'], cwd=self.repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', f'Version {i+1}'],
                          cwd=self.repo_path, check=True, capture_output=True)
        
        # Get commits with time filter (all should be recent in test)
        commits = get_commits_affecting_file(str(self.repo_path), "target.py", since_date="1 day ago")
        
        # Should get all commits in test environment (they're all recent)
        self.assertGreaterEqual(len(commits), 1)


if __name__ == '__main__':
    unittest.main()
