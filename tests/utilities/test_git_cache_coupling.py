"""Tests for coupling cache integration in GitDataCache (Phase 2.2)."""

import time
import unittest
from unittest.mock import patch

from src.kpis.coupling.coupling_analyzer import CouplingData
from src.utilities.git_cache import GitDataCache


class TestGitDataCacheCoupling(unittest.TestCase):
    """Test coupling cache behavior in GitDataCache."""

    def setUp(self):
        self.cache = GitDataCache()
        self.repo_root = "/test/repo"
        self.normalized_repo_root = self.cache._normalize_repo_path(self.repo_root)

    def tearDown(self):
        self.cache.clear_cache()

    @patch('src.kpis.coupling.coupling_analyzer.CouplingAnalyzer.calculate_coupling_matrix')
    def test_get_coupling_matrix_cache_miss(self, mock_calculate_matrix):
        """Should calculate and cache coupling matrix on cache miss."""
        matrix = {
            ('a.py', 'b.py'): CouplingData('a.py', 'b.py', 0.8, 4, 5, 5, ['c1', 'c2', 'c3', 'c4'])
        }
        mock_calculate_matrix.return_value = matrix

        result = self.cache.get_coupling_matrix(self.repo_root)

        self.assertEqual(result, matrix)
        self.assertIn(self.normalized_repo_root, self.cache.coupling_cache)
        self.assertEqual(self.cache.coupling_cache[self.normalized_repo_root], matrix)
        self.assertIn(self.normalized_repo_root, self.cache.coupling_cache_timestamp)
        mock_calculate_matrix.assert_called_once_with(self.normalized_repo_root, force_recalculate=True)

    @patch('src.kpis.coupling.coupling_analyzer.CouplingAnalyzer.calculate_coupling_matrix')
    def test_get_coupling_matrix_cache_hit(self, mock_calculate_matrix):
        """Should return cached coupling matrix when TTL is still valid."""
        cached_matrix = {
            ('a.py', 'b.py'): CouplingData('a.py', 'b.py', 0.7, 3, 4, 4, ['c1', 'c2', 'c3'])
        }
        self.cache.coupling_cache[self.normalized_repo_root] = cached_matrix
        self.cache.coupling_cache_timestamp[self.normalized_repo_root] = time.time()

        result = self.cache.get_coupling_matrix(self.repo_root)

        self.assertEqual(result, cached_matrix)
        mock_calculate_matrix.assert_not_called()

    @patch('src.kpis.coupling.coupling_analyzer.CouplingAnalyzer.calculate_coupling_matrix')
    def test_get_coupling_matrix_expired_ttl_recalculates(self, mock_calculate_matrix):
        """Should recalculate coupling matrix when TTL has expired."""
        old_matrix = {
            ('a.py', 'b.py'): CouplingData('a.py', 'b.py', 0.4, 3, 8, 7, ['c1', 'c2', 'c3'])
        }
        new_matrix = {
            ('a.py', 'c.py'): CouplingData('a.py', 'c.py', 0.9, 6, 7, 6, ['c4', 'c5', 'c6', 'c7', 'c8', 'c9'])
        }

        self.cache.coupling_cache[self.normalized_repo_root] = old_matrix
        self.cache.coupling_cache_timestamp[self.normalized_repo_root] = (
            time.time() - self.cache.coupling_cache_ttl_seconds - 5
        )
        mock_calculate_matrix.return_value = new_matrix

        result = self.cache.get_coupling_matrix(self.repo_root)

        self.assertEqual(result, new_matrix)
        self.assertEqual(self.cache.coupling_cache[self.normalized_repo_root], new_matrix)
        mock_calculate_matrix.assert_called_once_with(self.normalized_repo_root, force_recalculate=True)

    def test_get_coupling_data_for_file(self):
        """Should return coupled files sorted by score descending for target file."""
        matrix = {
            ('target.py', 'a.py'): CouplingData('target.py', 'a.py', 0.6, 3, 4, 5, ['c1', 'c2', 'c3']),
            ('b.py', 'target.py'): CouplingData('b.py', 'target.py', 0.9, 5, 6, 6, ['c1', 'c2', 'c3', 'c4', 'c5']),
            ('x.py', 'y.py'): CouplingData('x.py', 'y.py', 0.8, 4, 4, 4, ['c1', 'c2', 'c3', 'c4'])
        }
        self.cache.coupling_cache[self.normalized_repo_root] = matrix
        self.cache.coupling_cache_timestamp[self.normalized_repo_root] = time.time()

        result = self.cache.get_coupling_data(self.repo_root, 'target.py')

        self.assertEqual(result, [('b.py', 0.9), ('a.py', 0.6)])

    def test_invalidate_coupling_cache(self):
        """Should remove matrix and timestamp for repository."""
        self.cache.coupling_cache[self.normalized_repo_root] = {}
        self.cache.coupling_cache_timestamp[self.normalized_repo_root] = time.time()

        self.cache.invalidate_coupling_cache(self.repo_root)

        self.assertNotIn(self.normalized_repo_root, self.cache.coupling_cache)
        self.assertNotIn(self.normalized_repo_root, self.cache.coupling_cache_timestamp)


if __name__ == '__main__':
    unittest.main()
