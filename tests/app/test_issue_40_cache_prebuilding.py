import unittest
import tempfile
import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

from src.app import Analyzer
from src.utilities.git_cache import get_git_cache


class TestIssue40CachePreBuilding(unittest.TestCase):
    """
    TDD tests for Issue #40: Build cache before KPI calculation

    These tests verify that the cache is pre-populated with all file data
    before individual KPI calculations begin, rather than lazy loading during processing.
    """

    def setUp(self):
        """Set up test environment with a mock git repository."""
        # Create temporary directory structure
        self.test_dir = tempfile.mkdtemp()
        self.repo_dir = os.path.join(self.test_dir, "test_repo")
        os.makedirs(self.repo_dir)

        # Create test files
        self.test_files = [
            "src/main.py",
            "src/utils.py",
            "tests/test_main.py"
        ]

        for file_path in self.test_files:
            full_path = os.path.join(self.repo_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(f"# Test file {file_path}\ndef test_function():\n    return True\n")

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.repo_dir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=self.repo_dir, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=self.repo_dir, check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.repo_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.repo_dir, check=True)

        # Set up analyzer
        self.analyzer = Analyzer({'.py': {'name': 'python'}})

        # Clear cache before each test
        cache = get_git_cache()
        cache.clear_cache()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        # Clear cache after test
        cache = get_git_cache()
        cache.clear_cache()

    def test_cache_pre_building_before_kpi_calculation(self):
        """
        Test that cache is pre-built with all file data before KPI calculations start.

        This is the main TDD test for Issue #40. It should FAIL initially and PASS
        after implementation.
        """
        cache = get_git_cache()

        # Mock scanner to return our test files
        mock_files = []
        for file_path in self.test_files:
            full_path = Path(self.repo_dir) / file_path
            mock_files.append({
                'path': str(full_path),
                'ext': '.py'
            })

        with patch('subprocess.run') as mock_subprocess, \
                patch('subprocess.check_output') as mock_check_output:
            # Mock git commands to simulate cache operations
            mock_subprocess.return_value.stdout = '\n'.join(self.test_files)
            mock_subprocess.return_value.returncode = 0
            mock_check_output.side_effect = [
                'Mock blame output\n'.encode(),       # git blame
                'Mock log output\n'.encode()          # git log
            ]

            # Track when cache methods are called
            original_get_ownership = cache.get_ownership_data
            original_get_churn = cache.get_churn_data

            ownership_calls = []
            churn_calls = []

            def track_ownership_calls(repo_root, file_path):
                ownership_calls.append((repo_root, file_path))
                return original_get_ownership(repo_root, file_path)

            def track_churn_calls(repo_root, file_path):
                churn_calls.append((repo_root, file_path))
                return original_get_churn(repo_root, file_path)

            with patch.object(cache, 'get_ownership_data', side_effect=track_ownership_calls), \
                    patch.object(cache, 'get_churn_data', side_effect=track_churn_calls):

                # Run analysis
                result = self.analyzer._analyze_repo(self.repo_dir, mock_files, [self.repo_dir])

                # Verify cache was pre-built for ALL files before individual processing
                self.assertIsNotNone(result, "Analysis should complete successfully")

                # With pre-building, calls should be primarily from cache hits during KPI calculation
                # The key is that ownership_calls should be <= len(self.test_files) * 2
                # (once during pre-build, once during KPI calculation for each file)
                max_expected_calls = len(self.test_files) * 2
                self.assertLessEqual(len(ownership_calls), max_expected_calls,
                                     f"Pre-building should limit ownership calls to "
                                     f"{max_expected_calls} or fewer, got {len(ownership_calls)}")

                self.assertLessEqual(len(churn_calls), max_expected_calls,
                                     f"Pre-building should limit churn calls to "
                                     f"{max_expected_calls} or fewer, got {len(churn_calls)}")

                # Verify cache contains data for all files
                for file_path in self.test_files:
                    rel_path = file_path

                    # Check ownership cache
                    ownership_data = cache.get_ownership_data(self.repo_dir, rel_path)
                    self.assertIsNotNone(ownership_data,
                                         f"Ownership data should be cached for {rel_path}")

                    # Check churn cache
                    churn_data = cache.get_churn_data(self.repo_dir, rel_path)
                    self.assertIsNotNone(churn_data,
                                         f"Churn data should be cached for {rel_path}")

    def test_cache_pre_building_reduces_individual_calls(self):
        """
        Test that pre-building cache reduces the number of git calls during KPI calculation.

        This test verifies the performance benefit of Issue #40 implementation.
        """
        # Mock scanner files
        mock_files = []
        for file_path in self.test_files:
            full_path = Path(self.repo_dir) / file_path
            mock_files.append({
                'path': str(full_path),
                'ext': '.py'
            })

        with patch('subprocess.run') as mock_subprocess, \
                patch('subprocess.check_output') as mock_check_output:
            # Mock git commands for cache operations
            mock_subprocess.return_value.stdout = '\n'.join(self.test_files)
            mock_subprocess.return_value.returncode = 0
            mock_check_output.side_effect = [
                'Mock blame output\n'.encode() * 5,
                'Mock log output\n'.encode() * 5
            ]

            # Mock git subprocess operations
            mock_subprocess.return_value.stdout = '\n'.join(self.test_files)
            mock_subprocess.return_value.returncode = 0

            # Run analysis
            result = self.analyzer._analyze_repo(self.repo_dir, mock_files, [self.repo_dir])

            # After pre-building, subsequent calls should use cache
            # The exact number depends on implementation, but should be efficient
            git_call_count = mock_subprocess.call_count + mock_check_output.call_count

            # With pre-building, we expect:
            # - 1 ls-files call for tracked files
            # - 1 blame call per file for ownership (3 files = 3 calls)
            # - 1 log call per file for churn (3 files = 3 calls)
            # Total expected: ~7 calls (1 + 3 + 3)
            # This is much better than naive implementation which would be files × calls per KPI
            expected_max_calls = 1 + (len(self.test_files) * 2)  # ls-files + (blame + log) per file

            self.assertLessEqual(git_call_count, expected_max_calls + 2,  # Allow some tolerance
                                 f"Pre-building should be efficient. Got {git_call_count}, "
                                 f"expected around {expected_max_calls}")

            # The key benefit is that all data is ready in cache for subsequent KPI calculations
            self.assertIsNotNone(result, "Analysis should complete successfully")

    def test_cache_statistics_after_pre_building(self):
        """
        Test that cache statistics reflect pre-built data for all files.
        """
        cache = get_git_cache()

        mock_files = []
        for file_path in self.test_files:
            full_path = Path(self.repo_dir) / file_path
            mock_files.append({
                'path': str(full_path),
                'ext': '.py'
            })

        with patch('subprocess.run') as mock_subprocess, \
                patch('subprocess.check_output') as mock_check_output:
            # Mock git commands for cache statistics test
            mock_subprocess.return_value.stdout = '\n'.join(self.test_files)
            mock_subprocess.return_value.returncode = 0
            mock_check_output.side_effect = [
                'Mock blame output\n'.encode(),       # git blame
                'Mock log output\n'.encode()          # git log
            ]

            # Run analysis with pre-building
            self.analyzer._analyze_repo(self.repo_dir, mock_files, [self.repo_dir])

            # Check cache statistics
            stats = cache.get_cache_stats()

            # Should have entries for all files
            self.assertGreaterEqual(stats['total_ownership_entries'], len(self.test_files),
                                    "Should have ownership entries for all files")
            self.assertGreaterEqual(stats['total_churn_entries'], len(self.test_files),
                                    "Should have churn entries for all files")
            self.assertGreater(stats['total_tracked_files'], 0,
                               "Should have tracked files cached")


if __name__ == '__main__':
    unittest.main()
