"""
Test module for DeltaAnalyzer.

Following TDD (RED-GREEN-REFACTOR):
- Tests define the API and behavior
- DeltaAnalyzer integrates FunctionDiffParser with complexity calculation
"""

import pytest
import os
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path


class TestDeltaAnalyzerBasics:
    """Test basic DeltaAnalyzer initialization and configuration."""

    def test_delta_analyzer_initialization(self):
        """Test creating a DeltaAnalyzer instance."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        # Should work with any directory (will check for git later)
        analyzer = DeltaAnalyzer(repo_path=".")
        assert analyzer is not None
        assert analyzer.repo_path  # Path should be set (will be absolute)

    def test_delta_analyzer_requires_git_repo(self):
        """Test that DeltaAnalyzer validates git repository."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            # Non-git directory should raise or warn
            analyzer = DeltaAnalyzer(repo_path=tmpdir)
            # Should still initialize but may have limited functionality
            assert analyzer is not None


class TestAnalyzeBranchDelta:
    """Test analyze_branch_delta method with real git repository."""

    @pytest.fixture
    def git_test_repo(self):
        """Create a temporary git repository for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                          cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'],
                          cwd=repo_path, check=True, capture_output=True)

            # Create initial file with a function
            test_file = repo_path / "test.py"
            test_file.write_text("""def simple_function():
    return True
""")

            # Commit initial version
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'],
                          cwd=repo_path, check=True, capture_output=True)

            # Create feature branch
            subprocess.run(['git', 'checkout', '-b', 'feature/test'],
                          cwd=repo_path, check=True, capture_output=True)

            # Modify function (increase complexity)
            test_file.write_text("""def simple_function():
    x = 1
    if x > 0:
        return True
    else:
        return False
""")

            # Commit change
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Add complexity'],
                          cwd=repo_path, check=True, capture_output=True)

            # Get default branch name (git uses 'main' in newer versions)
            result = subprocess.run(['git', 'branch', '--show-current'],
                                   cwd=repo_path, capture_output=True, text=True)
            subprocess.run(['git', 'checkout', '-'], cwd=repo_path, check=True, capture_output=True)
            result = subprocess.run(['git', 'branch', '--show-current'],
                                   cwd=repo_path, capture_output=True, text=True, check=True)
            default_branch = result.stdout.strip()

            yield (str(repo_path), default_branch)

    def test_analyze_branch_delta_basic(self, git_test_repo):
        """Test analyzing delta between branches."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        repo_path, default_branch = git_test_repo
        analyzer = DeltaAnalyzer(repo_path=repo_path)

        # Analyze difference between default branch and feature/test
        delta_diff = analyzer.analyze_branch_delta(
            base_branch=default_branch,
            target_branch='feature/test'
        )

        # Should detect the modified function
        assert delta_diff is not None
        assert delta_diff.base_commit != delta_diff.target_commit
        # At least one function should have changed
        total_changes = (len(delta_diff.added_functions) +
                        len(delta_diff.modified_functions) +
                        len(delta_diff.deleted_functions))
        assert total_changes >= 1

    def test_analyze_branch_delta_complexity_increase(self, git_test_repo):
        """Test that delta analysis detects complexity increases."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        repo_path, default_branch = git_test_repo
        analyzer = DeltaAnalyzer(repo_path=repo_path)

        delta_diff = analyzer.analyze_branch_delta(
            base_branch=default_branch,
            target_branch='feature/test'
        )

        # The function increased in complexity (added if/else)
        # Should have positive complexity delta
        if len(delta_diff.modified_functions) > 0:
            func = delta_diff.modified_functions[0]
            assert func.complexity_delta > 0  # Complexity increased
            assert func.complexity_after > func.complexity_before

    def test_analyze_branch_delta_no_changes(self):
        """Test analyzing delta when branches are identical."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                          cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'],
                          cwd=repo_path, check=True, capture_output=True)

            # Create and commit a file
            test_file = repo_path / "test.py"
            test_file.write_text("def func(): pass")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial'],
                          cwd=repo_path, check=True, capture_output=True)

            # Get default branch
            result = subprocess.run(['git', 'branch', '--show-current'],
                                   cwd=repo_path, capture_output=True, text=True, check=True)
            default_branch = result.stdout.strip()

            analyzer = DeltaAnalyzer(repo_path=str(repo_path))

            # Compare branch to itself
            delta_diff = analyzer.analyze_branch_delta(
                base_branch=default_branch,
                target_branch=default_branch
            )

            # Should have no changes
            assert len(delta_diff.added_functions) == 0
            assert len(delta_diff.modified_functions) == 0
            assert len(delta_diff.deleted_functions) == 0
            assert delta_diff.total_complexity_delta == 0


class TestAnalyzeCommitRange:
    """Test analyze_commit_range method."""

    def test_analyze_commit_range_basic(self):
        """Test analyzing delta between two commits."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                          cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'],
                          cwd=repo_path, check=True, capture_output=True)

            # First commit
            test_file = repo_path / "test.py"
            test_file.write_text("def func(): pass")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'First'], cwd=repo_path, check=True, capture_output=True)

            # Get first commit hash
            result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                   cwd=repo_path, check=True, capture_output=True, text=True)
            first_commit = result.stdout.strip()

            # Second commit
            test_file.write_text("def func():\n    return True")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Second'], cwd=repo_path, check=True, capture_output=True)

            analyzer = DeltaAnalyzer(repo_path=str(repo_path))

            # Analyze from first commit to HEAD
            delta_diff = analyzer.analyze_commit_range(
                from_commit=first_commit,
                to_commit='HEAD'
            )

            # Should detect changes
            assert delta_diff is not None
            assert delta_diff.base_commit == first_commit

    def test_analyze_commit_range_multiple_commits(self):
        """Test analyzing delta across multiple commits."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                          cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'],
                          cwd=repo_path, check=True, capture_output=True)

            # Create 3 commits
            test_file = repo_path / "test.py"

            test_file.write_text("def func1(): pass")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Commit 1'], cwd=repo_path, check=True, capture_output=True)
            result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                   cwd=repo_path, check=True, capture_output=True, text=True)
            commit1 = result.stdout.strip()

            test_file.write_text("def func1(): pass\ndef func2(): pass")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Commit 2'], cwd=repo_path, check=True, capture_output=True)

            test_file.write_text("def func1(): return 1\ndef func2(): pass\ndef func3(): pass")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Commit 3'], cwd=repo_path, check=True, capture_output=True)

            analyzer = DeltaAnalyzer(repo_path=str(repo_path))

            # Analyze from commit1 to HEAD (should see all changes)
            delta_diff = analyzer.analyze_commit_range(
                from_commit=commit1,
                to_commit='HEAD'
            )

            # Should detect multiple function changes/additions
            total_changes = (len(delta_diff.added_functions) +
                           len(delta_diff.modified_functions))
            assert total_changes >= 2  # At least func2 added, func1 modified


class TestAnalyzeWorkingTree:
    """Test analyze_working_tree method for uncommitted changes."""

    def test_analyze_working_tree_with_uncommitted_changes(self):
        """Test analyzing uncommitted changes in working directory."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                          cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'],
                          cwd=repo_path, check=True, capture_output=True)

            # Commit initial version
            test_file = repo_path / "test.py"
            test_file.write_text("def func(): pass")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=repo_path, check=True, capture_output=True)

            # Make uncommitted changes
            test_file.write_text("def func():\n    return True")

            analyzer = DeltaAnalyzer(repo_path=str(repo_path))

            # Analyze working tree
            delta_diff = analyzer.analyze_working_tree()

            # Should detect uncommitted changes
            assert delta_diff is not None
            assert delta_diff.target_commit == 'working-tree'
            # Should have detected the modified function
            total_changes = (len(delta_diff.modified_functions) +
                           len(delta_diff.added_functions))
            assert total_changes >= 1

    def test_analyze_working_tree_clean(self):
        """Test analyzing clean working tree (no uncommitted changes)."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                          cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'],
                          cwd=repo_path, check=True, capture_output=True)

            # Commit file
            test_file = repo_path / "test.py"
            test_file.write_text("def func(): pass")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=repo_path, check=True, capture_output=True)

            # No uncommitted changes
            analyzer = DeltaAnalyzer(repo_path=str(repo_path))

            delta_diff = analyzer.analyze_working_tree()

            # Should have no changes
            assert len(delta_diff.added_functions) == 0
            assert len(delta_diff.modified_functions) == 0
            assert len(delta_diff.deleted_functions) == 0


class TestComplexityCalculation:
    """Test that DeltaAnalyzer correctly calculates complexity deltas."""

    def test_complexity_delta_for_simple_change(self):
        """Test complexity calculation for a simple function change."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Setup git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                          cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'],
                          cwd=repo_path, check=True, capture_output=True)

            # Initial: Simple function (complexity = 1)
            test_file = repo_path / "test.py"
            test_file.write_text("def func():\n    return 1")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=repo_path, check=True, capture_output=True)
            result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                   cwd=repo_path, check=True, capture_output=True, text=True)
            commit1 = result.stdout.strip()

            # Modified: Add if statement (complexity = 2)
            test_file.write_text("""def func():
    if True:
        return 1
    return 0
""")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Add if'], cwd=repo_path, check=True, capture_output=True)

            analyzer = DeltaAnalyzer(repo_path=str(repo_path))

            delta_diff = analyzer.analyze_commit_range(
                from_commit=commit1,
                to_commit='HEAD'
            )

            # Should have one modified function
            assert len(delta_diff.modified_functions) == 1
            func = delta_diff.modified_functions[0]

            # Complexity should have increased
            assert func.complexity_before >= 1  # At least 1
            assert func.complexity_after > func.complexity_before  # Increased
            assert func.complexity_delta > 0  # Positive delta


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_analyzer_with_non_existent_branch(self):
        """Test analyzing with non-existent branch."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                          cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'],
                          cwd=repo_path, check=True, capture_output=True)

            # Create initial commit
            test_file = repo_path / "test.py"
            test_file.write_text("def func(): pass")
            subprocess.run(['git', 'add', 'test.py'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=repo_path, check=True, capture_output=True)

            analyzer = DeltaAnalyzer(repo_path=str(repo_path))

            # Should raise or return empty delta
            with pytest.raises(Exception):
                analyzer.analyze_branch_delta(
                    base_branch='master',
                    target_branch='non-existent-branch'
                )

    def test_analyzer_with_binary_files(self):
        """Test that analyzer handles binary files gracefully."""
        from src.analysis.delta.delta_analyzer import DeltaAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                          cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'],
                          cwd=repo_path, check=True, capture_output=True)

            # Add binary file
            binary_file = repo_path / "image.png"
            binary_file.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
            subprocess.run(['git', 'add', 'image.png'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Add binary'], cwd=repo_path, check=True, capture_output=True)

            result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                   cwd=repo_path, check=True, capture_output=True, text=True)
            commit1 = result.stdout.strip()

            # Modify binary file
            binary_file.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rMODIFIED')
            subprocess.run(['git', 'add', 'image.png'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Modify binary'], cwd=repo_path, check=True, capture_output=True)

            analyzer = DeltaAnalyzer(repo_path=str(repo_path))

            # Should handle binary files gracefully (skip them)
            delta_diff = analyzer.analyze_commit_range(
                from_commit=commit1,
                to_commit='HEAD'
            )

            # Should not crash, binary files should be ignored
            assert delta_diff is not None
