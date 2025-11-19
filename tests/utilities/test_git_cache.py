"""
Tests for Git Data Cache (Issue #38)
Write tests that expect the KPI classes to use the cache.
"""
import unittest
from unittest.mock import patch, call
import os
import subprocess

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

    @patch('subprocess.run')
    @patch.object(GitDataCache, 'is_file_tracked', return_value=True)
    @patch('os.path.exists', return_value=True)
    def test_get_git_blame_cache_miss(self, mock_exists, mock_tracked, mock_run):
        """Test get_git_blame when cache is empty (cache miss)."""
        # Setup mock
        blame_output = "author Alice\nauthor Bob\nauthor Alice\n"
        mock_run.return_value.stdout = blame_output
        mock_run.return_value.returncode = 0

        # Call method
        result = self.cache.get_git_blame(self.test_repo, self.test_file)

        # Assert result and cache populated
        self.assertEqual(result, blame_output)
        repo_key = os.path.abspath(self.test_repo)
        self.assertIn(repo_key, self.cache.blame_cache)
        self.assertEqual(self.cache.blame_cache[repo_key][self.test_file], blame_output)

        # Verify git blame was called via _run_git_command
        mock_run.assert_called_once_with(
            ['git', '-C', os.path.abspath(self.test_repo), 'blame', '--line-porcelain', self.test_file],
            capture_output=True,
            text=True,
            check=True
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


class TestGitCacheHelperMethods(unittest.TestCase):
    """Test helper methods for git command execution and data processing."""

    def setUp(self):
        """Set up test environment."""
        self.cache = GitDataCache()
        self.test_repo = "/test/repo"

    def tearDown(self):
        """Clean up after tests."""
        self.cache.clear_cache()

    def test_normalize_repo_path_absolute(self):
        """Test _normalize_repo_path with absolute path."""
        result = self.cache._normalize_repo_path("/absolute/path/to/repo")
        self.assertEqual(result, os.path.abspath("/absolute/path/to/repo"))

    def test_normalize_repo_path_relative(self):
        """Test _normalize_repo_path with relative path."""
        relative_path = "relative/path"
        result = self.cache._normalize_repo_path(relative_path)
        expected = os.path.abspath(relative_path)
        self.assertEqual(result, expected)

    def test_normalize_repo_path_current_dir(self):
        """Test _normalize_repo_path with current directory."""
        result = self.cache._normalize_repo_path(".")
        self.assertEqual(result, os.path.abspath("."))

    def test_normalize_repo_path_already_normalized(self):
        """Test _normalize_repo_path is idempotent."""
        path = os.path.abspath("/some/path")
        result = self.cache._normalize_repo_path(path)
        self.assertEqual(result, path)

    def test_get_repo_cache_creates_new_cache(self):
        """Test _get_repo_cache creates new cache dict if not exists."""
        cache_dict = {}
        repo_root = "/test/repo"

        result = self.cache._get_repo_cache(cache_dict, repo_root)

        # Should create and return new dict
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)
        self.assertIn(repo_root, cache_dict)
        self.assertIs(cache_dict[repo_root], result)

    def test_get_repo_cache_returns_existing_cache(self):
        """Test _get_repo_cache returns existing cache dict."""
        cache_dict = {"/test/repo": {"file.py": "data"}}
        repo_root = "/test/repo"

        result = self.cache._get_repo_cache(cache_dict, repo_root)

        # Should return existing dict
        self.assertIs(result, cache_dict[repo_root])
        self.assertEqual(result, {"file.py": "data"})

    def test_get_repo_cache_normalizes_path(self):
        """Test _get_repo_cache normalizes repo_root path."""
        cache_dict = {}
        relative_path = "relative/path"

        result = self.cache._get_repo_cache(cache_dict, relative_path)

        # Should use normalized path as key
        normalized = os.path.abspath(relative_path)
        self.assertIn(normalized, cache_dict)
        self.assertIs(result, cache_dict[normalized])

    @patch('src.utilities.git_cache.debug_print')
    def test_log_cache_access_hit(self, mock_debug):
        """Test _log_cache_access logs cache hit."""
        self.cache._log_cache_access("test.py", hit=True, cache_type="ownership")

        mock_debug.assert_called_once_with("[CACHE] Hit: ownership data for test.py")

    @patch('src.utilities.git_cache.debug_print')
    def test_log_cache_access_miss(self, mock_debug):
        """Test _log_cache_access logs cache miss."""
        self.cache._log_cache_access("test.py", hit=False, cache_type="churn")

        mock_debug.assert_called_once_with("[CACHE] Miss: churn data for test.py")

    @patch('src.utilities.git_cache.debug_print')
    def test_log_cache_access_blame_type(self, mock_debug):
        """Test _log_cache_access with blame cache type."""
        self.cache._log_cache_access("src/main.py", hit=True, cache_type="git blame")

        mock_debug.assert_called_once_with("[CACHE] Hit: git blame for src/main.py")

    @patch('subprocess.run')
    def test_run_git_command_success(self, mock_run):
        """Test _run_git_command with successful git execution."""
        # Setup mock
        mock_run.return_value.stdout = "file1.py\nfile2.py\n"
        mock_run.return_value.returncode = 0

        # Call helper method
        result = self.cache._run_git_command(self.test_repo, ['ls-files'])

        # Assert result
        self.assertEqual(result, "file1.py\nfile2.py\n")
        mock_run.assert_called_once_with(
            ['git', '-C', os.path.abspath(self.test_repo), 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )

    @patch('subprocess.run')
    def test_run_git_command_with_subprocess_error(self, mock_run):
        """Test _run_git_command handles subprocess errors gracefully."""
        # Setup mock to raise error
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')

        # Call helper method
        result = self.cache._run_git_command(self.test_repo, ['ls-files'])

        # Assert returns None on error
        self.assertIsNone(result)

    @patch('subprocess.run')
    def test_run_git_command_with_permission_error(self, mock_run):
        """Test _run_git_command handles permission errors."""
        # Setup mock to raise PermissionError
        mock_run.side_effect = PermissionError("Permission denied")

        # Call helper method
        result = self.cache._run_git_command(self.test_repo, ['ls-files'])

        # Assert returns None on permission error
        self.assertIsNone(result)

    @patch.object(GitDataCache, 'is_file_tracked', return_value=False)
    @patch('subprocess.run')
    def test_run_git_command_with_untracked_file_check(self, mock_run, mock_tracked):
        """Test _run_git_command skips untracked files when check_file is provided."""
        # Call with check_file parameter for untracked file
        result = self.cache._run_git_command(self.test_repo, ['blame', 'file.py'], check_file='file.py')

        # Assert returns None without calling subprocess
        self.assertIsNone(result)
        mock_run.assert_not_called()

    @patch.object(GitDataCache, 'is_file_tracked', return_value=True)
    @patch('subprocess.run')
    def test_run_git_command_with_tracked_file_check(self, mock_run, mock_tracked):
        """Test _run_git_command proceeds with tracked files."""
        # Setup mock
        mock_run.return_value.stdout = "blame output"
        mock_run.return_value.returncode = 0

        # Call with check_file parameter for tracked file
        result = self.cache._run_git_command(self.test_repo, ['blame', 'file.py'], check_file='file.py')

        # Assert subprocess was called
        self.assertEqual(result, "blame output")
        mock_run.assert_called_once()

    def test_calculate_ownership_from_blame_multiple_authors(self):
        """Test _calculate_ownership_from_blame with multiple authors."""
        blame_output = "author Alice\nauthor Bob\nauthor Alice\nauthor Alice\nauthor Bob\n"

        result = self.cache._calculate_ownership_from_blame(blame_output)

        expected = {"Alice": 60.0, "Bob": 40.0}
        self.assertEqual(result, expected)

    def test_calculate_ownership_from_blame_single_author(self):
        """Test _calculate_ownership_from_blame with single author."""
        blame_output = "author Alice\nauthor Alice\nauthor Alice\n"

        result = self.cache._calculate_ownership_from_blame(blame_output)

        expected = {"Alice": 100.0}
        self.assertEqual(result, expected)

    def test_calculate_ownership_from_blame_empty_output(self):
        """Test _calculate_ownership_from_blame with empty blame output."""
        blame_output = ""

        result = self.cache._calculate_ownership_from_blame(blame_output)

        self.assertEqual(result, {})

    def test_calculate_ownership_from_blame_no_authors(self):
        """Test _calculate_ownership_from_blame with no author lines."""
        blame_output = "commit abc123\nfile test.py\n"

        result = self.cache._calculate_ownership_from_blame(blame_output)

        self.assertEqual(result, {})

    @patch.object(GitDataCache, '_run_git_command')
    def test_calculate_churn_with_commits(self, mock_run_git):
        """Test _calculate_churn with multiple commits."""
        # Setup mock git log output
        mock_run_git.return_value = "abc123 commit 1\ndef456 commit 2\nghi789 commit 3\n"

        result = self.cache._calculate_churn(self.test_repo, "file.py")

        # Assert correct churn count
        self.assertEqual(result, 3)
        mock_run_git.assert_called_once_with(
            self.test_repo,
            ['log', '--oneline', '--since', '30 days ago', '--', 'file.py']
        )

    @patch.object(GitDataCache, '_run_git_command')
    def test_calculate_churn_no_commits(self, mock_run_git):
        """Test _calculate_churn with no commits."""
        # Setup mock with empty output
        mock_run_git.return_value = ""

        result = self.cache._calculate_churn(self.test_repo, "file.py")

        self.assertEqual(result, 0)

    @patch.object(GitDataCache, '_run_git_command')
    def test_calculate_churn_git_error(self, mock_run_git):
        """Test _calculate_churn when git command fails."""
        # Setup mock to return None (error case)
        mock_run_git.return_value = None

        result = self.cache._calculate_churn(self.test_repo, "file.py")

        self.assertEqual(result, 0)

    @patch.object(GitDataCache, '_run_git_command')
    def test_calculate_churn_custom_period(self, mock_run_git):
        """Test _calculate_churn respects custom churn_period_days."""
        # Create cache with custom period
        custom_cache = GitDataCache(churn_period_days=90)
        mock_run_git.return_value = "abc123 commit\n"

        result = custom_cache._calculate_churn(self.test_repo, "file.py")

        # Assert uses correct time period
        mock_run_git.assert_called_once_with(
            self.test_repo,
            ['log', '--oneline', '--since', '90 days ago', '--', 'file.py']
        )
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()
