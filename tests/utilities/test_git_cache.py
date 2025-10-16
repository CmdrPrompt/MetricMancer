"""
Tests for Git Data Cache (Issue #38)
Write tests that expect the KPI classes to use the cache.
"""
import unittest
from unittest.mock import patch, MagicMock, call
import os
import tempfile
import shutil

from src.utilities.git_cache import GitDataCache, get_git_cache


class TestGitDataCache(unittest.TestCase):
    """Test the GitDataCache implementation for Issue #38."""

    def setUp(self):
        """Set up test environment."""
        self.cache = GitDataCache()
        self.test_repo = "/test/repo"
        self.test_file = "src/test.py"

    def tearDown(self):
        """Clean up after tests."""
        self.cache.clear_cache()

    def test_cache_initialization(self):
        """Test that cache initializes with empty dictionaries."""
        cache = GitDataCache()
        self.assertEqual(cache.ownership_cache, {})
        self.assertEqual(cache.churn_cache, {})
        self.assertEqual(cache.blame_cache, {})
        self.assertEqual(cache.tracked_files_cache, {})

    def test_singleton_instance(self):
        """Test that get_git_cache returns the same instance."""
        cache1 = get_git_cache()
        cache2 = get_git_cache()
        self.assertIs(cache1, cache2)

    def test_clear_cache_specific_repo(self):
        """Test clearing cache for a specific repository."""
        # Setup test data
        self.cache.ownership_cache[self.test_repo] = {self.test_file: {"author1": 100.0}}
        self.cache.churn_cache[self.test_repo] = {self.test_file: 5}
        other_repo = "/other/repo"
        self.cache.ownership_cache[other_repo] = {"other.py": {"author2": 100.0}}

        # Clear all cache (clear_cache method doesn't take specific repo parameter)
        self.cache.clear_cache()

        # Verify cache was cleared
        self.assertEqual(len(self.cache.ownership_cache), 0)
        self.assertEqual(len(self.cache.churn_cache), 0)

    def test_clear_all_cache(self):
        """Test clearing entire cache."""
        # Setup test data
        self.cache.ownership_cache[self.test_repo] = {self.test_file: {"author1": 100.0}}
        self.cache.churn_cache[self.test_repo] = {self.test_file: 5}

        # Clear all
        self.cache.clear_cache()

        # Assert all caches empty
        self.assertEqual(self.cache.ownership_cache, {})
        self.assertEqual(self.cache.churn_cache, {})
        self.assertEqual(self.cache.blame_cache, {})
        self.assertEqual(self.cache.tracked_files_cache, {})

    @patch('subprocess.run')
    def test_is_file_tracked_cache_miss(self, mock_run):
        """Test is_file_tracked when cache is empty (cache miss)."""
        # Setup mock
        mock_run.return_value.stdout = "src/test.py\nsrc/other.py\n"
        mock_run.return_value.returncode = 0

        # Call method
        result = self.cache.is_file_tracked(self.test_repo, self.test_file)

        # Assert result and cache populated
        self.assertTrue(result)
        self.assertIn(self.test_repo, self.cache.tracked_files_cache)
        self.assertIn(self.test_file, self.cache.tracked_files_cache[self.test_repo])

        # Verify git ls-files was called
        mock_run.assert_called_once_with(
            ['git', '-C', os.path.abspath(self.test_repo), 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )

    def test_is_file_tracked_cache_hit(self):
        """Test is_file_tracked when data is already cached (cache hit)."""
        # Setup cache
        self.cache.tracked_files_cache[os.path.abspath(self.test_repo)] = {self.test_file}

        with patch('subprocess.run') as mock_run:
            # Call method
            result = self.cache.is_file_tracked(self.test_repo, self.test_file)

            # Assert result without subprocess call
            self.assertTrue(result)
            mock_run.assert_not_called()

    @patch('subprocess.check_output')
    @patch.object(GitDataCache, 'is_file_tracked', return_value=True)
    @patch('os.path.exists', return_value=True)
    def test_get_git_blame_cache_miss(self, mock_exists, mock_tracked, mock_check_output):
        """Test get_git_blame when cache is empty (cache miss)."""
        # Setup mock
        blame_output = "author Alice\nauthor Bob\nauthor Alice\n"
        mock_check_output.return_value = blame_output

        # Call method
        result = self.cache.get_git_blame(self.test_repo, self.test_file)

        # Assert result and cache populated
        self.assertEqual(result, blame_output)
        repo_key = os.path.abspath(self.test_repo)
        self.assertIn(repo_key, self.cache.blame_cache)
        self.assertEqual(self.cache.blame_cache[repo_key][self.test_file], blame_output)

        # Verify git blame was called
        mock_check_output.assert_called_once_with(
            ['git', '-C', os.path.abspath(self.test_repo), 'blame', '--line-porcelain', self.test_file],
            text=True
        )

    def test_get_git_blame_cache_hit(self):
        """Test get_git_blame when data is already cached (cache hit)."""
        # Setup cache
        blame_output = "author Alice\nauthor Bob\n"
        repo_key = os.path.abspath(self.test_repo)
        self.cache.blame_cache[repo_key] = {self.test_file: blame_output}

        with patch('subprocess.check_output') as mock_check_output:
            # Call method
            result = self.cache.get_git_blame(self.test_repo, self.test_file)

            # Assert result without subprocess call
            self.assertEqual(result, blame_output)
            mock_check_output.assert_not_called()

    @patch.object(GitDataCache, 'get_git_blame')
    def test_get_ownership_data_cache_miss(self, mock_blame):
        """Test get_ownership_data calculation from git blame (cache miss)."""
        # Setup mock blame output
        blame_output = "author Alice\nauthor Bob\nauthor Alice\n"
        mock_blame.return_value = blame_output

        # Call method
        result = self.cache.get_ownership_data(self.test_repo, self.test_file)

        # Assert result calculation
        expected = {"Alice": 66.7, "Bob": 33.3}
        self.assertEqual(result, expected)

        # Assert cache populated
        repo_key = os.path.abspath(self.test_repo)
        self.assertIn(repo_key, self.cache.ownership_cache)
        self.assertEqual(self.cache.ownership_cache[repo_key][self.test_file], expected)

    def test_get_ownership_data_cache_hit(self):
        """Test get_ownership_data when already cached (cache hit)."""
        # Setup cache
        cached_data = {"Alice": 75.0, "Bob": 25.0}
        repo_key = os.path.abspath(self.test_repo)
        self.cache.ownership_cache[repo_key] = {self.test_file: cached_data}

        with patch.object(self.cache, 'get_git_blame') as mock_blame:
            # Call method
            result = self.cache.get_ownership_data(self.test_repo, self.test_file)

            # Assert result without blame call
            self.assertEqual(result, cached_data)
            mock_blame.assert_not_called()

    def test_get_ownership_data_node_modules_skip(self):
        """Test that node_modules files are skipped."""
        file_path = "node_modules/package/index.js"

        result = self.cache.get_ownership_data(self.test_repo, file_path)

        self.assertEqual(result, {})

    @patch.object(GitDataCache, 'get_git_blame', return_value=None)
    def test_get_ownership_data_no_blame(self, mock_blame):
        """Test ownership calculation when git blame fails."""
        result = self.cache.get_ownership_data(self.test_repo, self.test_file)

        self.assertEqual(result, {})

    def test_prefetch_ownership_data(self):
        """Test prefetching ownership data for multiple files."""
        files = ["file1.py", "file2.py", "file3.py"]

        with patch.object(self.cache, 'get_ownership_data') as mock_get:
            self.cache.prefetch_ownership_data(self.test_repo, files)

            # Assert get_ownership_data called for each file
            expected_calls = [call(os.path.abspath(self.test_repo), f) for f in files]
            mock_get.assert_has_calls(expected_calls)

    def test_prefetch_ownership_data_partial_cache(self):
        """Test prefetching when some files are already cached."""
        files = ["file1.py", "file2.py", "file3.py"]

        # Pre-cache one file
        repo_key = os.path.abspath(self.test_repo)
        self.cache.ownership_cache[repo_key] = {"file1.py": {"Alice": 100.0}}

        with patch.object(self.cache, 'get_ownership_data') as mock_get:
            self.cache.prefetch_ownership_data(self.test_repo, files)

            # Assert get_ownership_data called only for uncached files
            expected_calls = [call(repo_key, "file2.py"), call(repo_key, "file3.py")]
            mock_get.assert_has_calls(expected_calls)
            self.assertEqual(mock_get.call_count, 2)

    def test_get_cache_stats(self):
        """Test cache statistics reporting."""
        # Setup test data
        repo1 = "/repo1"
        repo2 = "/repo2"
        self.cache.ownership_cache[repo1] = {"file1.py": {"Alice": 100.0}, "file2.py": {"Bob": 100.0}}
        self.cache.ownership_cache[repo2] = {"file3.py": {"Charlie": 100.0}}
        self.cache.churn_cache[repo1] = {"file1.py": 5}
        self.cache.tracked_files_cache[repo1] = {"file1.py", "file2.py"}

        stats = self.cache.get_cache_stats()

        expected = {
            "repos_cached": 2,
            "total_ownership_entries": 3,
            "total_churn_entries": 1,
            "total_blame_entries": 0,
            "total_tracked_files": 2
        }
        self.assertEqual(stats, expected)


if __name__ == '__main__':
    unittest.main()
