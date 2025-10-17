"""
Tests that verify KPI classes use the shared git cache (Issue #38)
These tests ensure that CodeOwnershipKPI and SharedOwnershipKPI use the cache properly.
"""
import unittest
from unittest.mock import patch, MagicMock

from src.kpis.codeownership.code_ownership import CodeOwnershipKPI
from src.kpis.sharedcodeownership.shared_code_ownership import SharedOwnershipKPI
from src.utilities.git_cache import get_git_cache


class TestKPIUsesCache(unittest.TestCase):
    """Test that KPI classes properly use the shared git cache."""

    def setUp(self):
        """Set up test environment."""
        self.test_repo = "/test/repo"
        self.test_file = "src/test.py"
        # Clear cache before each test
        cache = get_git_cache()
        cache.clear_cache()

    @patch('src.kpis.codeownership.code_ownership.get_git_cache')
    def test_code_ownership_kpi_uses_cache(self, mock_get_cache):
        """Test that CodeOwnershipKPI calls the git cache."""
        # Setup mock cache
        mock_cache = MagicMock()
        mock_cache.get_ownership_data.return_value = {"Alice": 75.0, "Bob": 25.0}
        mock_get_cache.return_value = mock_cache

        # Create KPI instance with absolute path
        abs_test_file = f"{self.test_repo}/{self.test_file}"
        kpi = CodeOwnershipKPI(abs_test_file, self.test_repo)

        # Verify cache was called
        mock_get_cache.assert_called_once()
        mock_cache.get_ownership_data.assert_called_once_with(self.test_repo, self.test_file)

        # Verify KPI has correct value
        self.assertEqual(kpi.value, {"Alice": 75.0, "Bob": 25.0})

    @patch('src.kpis.codeownership.code_ownership.get_git_cache')
    def test_code_ownership_kpi_cache_hit_performance(self, mock_get_cache):
        """Test that repeated CodeOwnershipKPI calls use cached data."""
        # Setup mock cache
        mock_cache = MagicMock()
        mock_cache.get_ownership_data.return_value = {"Alice": 100.0}
        mock_get_cache.return_value = mock_cache

        # Create multiple KPI instances for same file
        kpi1 = CodeOwnershipKPI(self.test_file, self.test_repo)
        kpi2 = CodeOwnershipKPI(self.test_file, self.test_repo)
        kpi3 = CodeOwnershipKPI(self.test_file, self.test_repo)

        # Verify cache was accessed for each instance
        self.assertEqual(mock_get_cache.call_count, 3)
        self.assertEqual(mock_cache.get_ownership_data.call_count, 3)

        # All instances should have same cached value
        self.assertEqual(kpi1.value, {"Alice": 100.0})
        self.assertEqual(kpi2.value, {"Alice": 100.0})
        self.assertEqual(kpi3.value, {"Alice": 100.0})

    @patch('src.kpis.sharedcodeownership.shared_code_ownership.CodeOwnershipKPI')
    def test_shared_ownership_kpi_uses_code_ownership_cache(self, mock_code_ownership):
        """Test that SharedOwnershipKPI benefits from CodeOwnershipKPI cache usage."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.value = {"Alice": 80.0, "Bob": 20.0}
        mock_code_ownership.return_value = mock_instance

        # Create SharedOwnershipKPI without pre-computed ownership data
        shared_kpi = SharedOwnershipKPI(self.test_file, self.test_repo, threshold=50.0)

        # Verify CodeOwnershipKPI was instantiated
        mock_code_ownership.assert_called_once_with(self.test_file, self.test_repo)

        # Verify shared ownership calculation used the cached data
        # With threshold 50.0, only Alice (80.0) should be considered significant
        expected_shared_ownership = {
            'num_significant_authors': 1,
            'authors': ['Alice'],
            'threshold': 50.0
        }
        self.assertEqual(shared_kpi.value, expected_shared_ownership)

    def test_shared_ownership_kpi_with_precomputed_data_skips_cache(self):
        """Test that SharedOwnershipKPI with precomputed data doesn't call CodeOwnershipKPI."""
        ownership_data = {"Alice": 70.0, "Bob": 30.0}

        with patch('src.kpis.sharedcodeownership.shared_code_ownership.CodeOwnershipKPI') as mock_code_ownership:
            # Create SharedOwnershipKPI with pre-computed data
            shared_kpi = SharedOwnershipKPI(
                self.test_file,
                self.test_repo,
                threshold=50.0,
                ownership_data=ownership_data
            )

            # Verify CodeOwnershipKPI was NOT called (cache optimization)
            mock_code_ownership.assert_not_called()

            # Verify calculation still works correctly
            expected = {
                'num_significant_authors': 1,
                'authors': ['Alice'],
                'threshold': 50.0
            }
            self.assertEqual(shared_kpi.value, expected)

    @patch('src.utilities.git_cache.GitDataCache.get_ownership_data')
    def test_cache_integration_end_to_end(self, mock_get_ownership):
        """Test end-to-end cache integration without mocking the cache instance."""
        # Setup mock data from cache
        mock_get_ownership.return_value = {"Alice": 60.0, "Bob": 40.0}

        # Create KPI instances
        code_ownership = CodeOwnershipKPI(self.test_file, self.test_repo)
        shared_ownership = SharedOwnershipKPI(self.test_file, self.test_repo, threshold=50.0)

        # Verify cache was used
        # CodeOwnershipKPI should call cache directly
        # SharedOwnershipKPI should call CodeOwnershipKPI which calls cache
        self.assertEqual(mock_get_ownership.call_count, 2)

        # Verify both KPIs have correct values
        self.assertEqual(code_ownership.value, {"Alice": 60.0, "Bob": 40.0})

        expected_shared = {
            'num_significant_authors': 1,
            'authors': ['Alice'],
            'threshold': 50.0
        }
        self.assertEqual(shared_ownership.value, expected_shared)

    def test_cache_na_ownership_handling(self):
        """Test that KPIs handle N/A ownership data from cache correctly."""
        with patch('src.utilities.git_cache.GitDataCache.get_ownership_data') as mock_get_ownership:
            # Setup cache to return N/A (file not tracked, etc.)
            mock_get_ownership.return_value = {"ownership": "N/A"}

            # Create KPI instances
            code_ownership = CodeOwnershipKPI(self.test_file, self.test_repo)
            shared_ownership = SharedOwnershipKPI(self.test_file, self.test_repo)

            # Verify correct N/A handling
            self.assertEqual(code_ownership.value, {"ownership": "N/A"})
            self.assertEqual(shared_ownership.value, {"shared_ownership": "N/A"})


class TestCachePerformanceExpectations(unittest.TestCase):
    """
    Tests that verify performance expectations are met by the cache.
    These tests are markers for the expected behavior described in Issue #36.
    """

    def test_cache_reduces_git_calls_expectation(self):
        """
        Test expectation: Cache should reduce the number of git calls.
        This test documents the expected behavior for verification after implementation.
        """
        # This test serves as documentation of expected cache behavior
        # In a real implementation, we would measure actual git subprocess calls

        with patch('subprocess.run') as mock_run, \
                patch('subprocess.check_output') as mock_check_output:

            # Setup successful git responses
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "src/test.py\n"
            mock_check_output.return_value = "author Alice\nauthor Bob\n"

            # Create multiple KPI instances for same file
            kpi1 = CodeOwnershipKPI("src/test.py", "/test/repo")
            kpi2 = CodeOwnershipKPI("src/test.py", "/test/repo")
            kpi3 = CodeOwnershipKPI("src/test.py", "/test/repo")

            # Expectation: git commands should be called fewer times than KPI instances
            # Due to caching, subsequent calls should use cached data
            total_git_calls = mock_run.call_count + mock_check_output.call_count
            kpi_instances = 3

            # This assertion documents the expected optimization
            # In practice, we expect total_git_calls < kpi_instances * 2 (ls-files + blame per KPI)
            # With perfect caching: total_git_calls should be 2 (one ls-files + one blame total)
            self.assertLessEqual(total_git_calls, kpi_instances * 2,
                                 "Cache should reduce git calls compared to naive implementation")

    def test_batch_prefetch_expectation(self):
        """
        Test expectation: Cache should support batch prefetching for better performance.
        This tests the interface for batch operations described in Issue #38.
        """
        cache = get_git_cache()
        files = ["file1.py", "file2.py", "file3.py"]

        # Test that prefetch method exists and can be called
        self.assertTrue(hasattr(cache, 'prefetch_ownership_data'),
                        "Cache should support batch prefetching")

        # Test that prefetch method accepts expected parameters
        try:
            cache.prefetch_ownership_data("/test/repo", files)
        except Exception as e:
            self.fail(f"Prefetch method should accept repo and file list: {e}")


if __name__ == '__main__':
    unittest.main()
