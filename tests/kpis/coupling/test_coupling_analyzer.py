"""
Tests for CouplingAnalyzer - Temporal coupling detection.

Tests coupling calculation, threshold filtering, and edge cases.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from pathlib import Path

from src.kpis.coupling.coupling_analyzer import CouplingAnalyzer, CouplingData


class TestCouplingData(unittest.TestCase):
    """Test CouplingData dataclass."""
    
    def test_coupling_data_creation(self):
        """Test basic CouplingData creation."""
        data = CouplingData(
            file_a="src/a.py",
            file_b="src/b.py",
            coupling_score=0.85,
            commits_together=17,
            total_commits_a=20,
            total_commits_b=25,
            commits=["abc123", "def456"]
        )
        
        self.assertEqual(data.file_a, "src/a.py")
        self.assertEqual(data.file_b, "src/b.py")
        self.assertEqual(data.coupling_score, 0.85)
        self.assertEqual(data.commits_together, 17)
        self.assertEqual(data.total_commits_a, 20)
        self.assertEqual(data.total_commits_b, 25)
        self.assertEqual(len(data.commits), 2)
    
    def test_coupling_strength_very_high(self):
        """Test strength property for very high coupling."""
        data = CouplingData("a", "b", 0.85, 17, 20, 20, [])
        self.assertEqual(data.strength, "VERY_HIGH")
        
        data = CouplingData("a", "b", 0.7, 14, 20, 20, [])
        self.assertEqual(data.strength, "VERY_HIGH")
    
    def test_coupling_strength_high(self):
        """Test strength property for high coupling."""
        data = CouplingData("a", "b", 0.65, 13, 20, 20, [])
        self.assertEqual(data.strength, "HIGH")
        
        data = CouplingData("a", "b", 0.5, 10, 20, 20, [])
        self.assertEqual(data.strength, "HIGH")
    
    def test_coupling_strength_medium(self):
        """Test strength property for medium coupling."""
        data = CouplingData("a", "b", 0.4, 8, 20, 20, [])
        self.assertEqual(data.strength, "MEDIUM")
        
        data = CouplingData("a", "b", 0.3, 6, 20, 20, [])
        self.assertEqual(data.strength, "MEDIUM")
    
    def test_coupling_strength_low(self):
        """Test strength property for low coupling."""
        data = CouplingData("a", "b", 0.2, 4, 20, 20, [])
        self.assertEqual(data.strength, "LOW")
        
        data = CouplingData("a", "b", 0.0, 0, 20, 20, [])
        self.assertEqual(data.strength, "LOW")


class TestCouplingAnalyzer(unittest.TestCase):
    """Test CouplingAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CouplingAnalyzer(
            time_period_days=90,
            min_coupling_threshold=0.3,
            min_commits=3
        )
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization with custom parameters."""
        analyzer = CouplingAnalyzer(
            time_period_days=60,
            min_coupling_threshold=0.5,
            min_commits=5
        )
        
        self.assertEqual(analyzer.time_period_days, 60)
        self.assertEqual(analyzer.min_coupling_threshold, 0.5)
        self.assertEqual(analyzer.min_commits, 5)
    
    def test_analyzer_default_initialization(self):
        """Test analyzer initialization with default parameters."""
        analyzer = CouplingAnalyzer()
        
        self.assertEqual(analyzer.time_period_days, 90)
        self.assertEqual(analyzer.min_coupling_threshold, 0.3)
        self.assertEqual(analyzer.min_commits, 3)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_calculate_coupling_matrix_empty_history(self, mock_get_history):
        """Test coupling calculation with no commit history."""
        mock_get_history.return_value = []
        
        matrix = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        self.assertEqual(len(matrix), 0)
        mock_get_history.assert_called_once()
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_calculate_coupling_matrix_single_commit(self, mock_get_history):
        """Test coupling calculation with single commit."""
        mock_get_history.return_value = [
            {
                'commit_hash': 'abc123',
                'timestamp': 1234567890,
                'author': 'Test Author',
                'changed_files': ['src/a.py', 'src/b.py']
            }
        ]
        
        # Single commit doesn't meet min_commits threshold (3)
        matrix = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        self.assertEqual(len(matrix), 0)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_calculate_coupling_matrix_basic_coupling(self, mock_get_history):
        """Test basic coupling calculation."""
        # Files a.py and b.py change together 4 times out of 5 commits each
        mock_get_history.return_value = [
            {
                'commit_hash': 'c1',
                'timestamp': 1,
                'author': 'Dev',
                'changed_files': ['src/a.py', 'src/b.py']
            },
            {
                'commit_hash': 'c2',
                'timestamp': 2,
                'author': 'Dev',
                'changed_files': ['src/a.py', 'src/b.py']
            },
            {
                'commit_hash': 'c3',
                'timestamp': 3,
                'author': 'Dev',
                'changed_files': ['src/a.py', 'src/b.py']
            },
            {
                'commit_hash': 'c4',
                'timestamp': 4,
                'author': 'Dev',
                'changed_files': ['src/a.py', 'src/b.py']
            },
            {
                'commit_hash': 'c5',
                'timestamp': 5,
                'author': 'Dev',
                'changed_files': ['src/a.py']  # Only a.py
            }
        ]
        
        matrix = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        # Should have one coupling pair
        self.assertEqual(len(matrix), 1)
        
        key = ('src/a.py', 'src/b.py')
        self.assertIn(key, matrix)
        
        coupling = matrix[key]
        self.assertEqual(coupling.file_a, 'src/a.py')
        self.assertEqual(coupling.file_b, 'src/b.py')
        self.assertEqual(coupling.commits_together, 4)
        self.assertEqual(coupling.total_commits_a, 5)
        self.assertEqual(coupling.total_commits_b, 4)
        
        # Coupling score = 4 / min(5, 4) = 4 / 4 = 1.0
        self.assertEqual(coupling.coupling_score, 1.0)
        self.assertEqual(coupling.strength, "VERY_HIGH")
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_calculate_coupling_matrix_multiple_pairs(self, mock_get_history):
        """Test coupling calculation with multiple file pairs."""
        # Need more commits to meet min_commits=3 threshold
        mock_get_history.return_value = [
            {
                'commit_hash': 'c1',
                'timestamp': 1,
                'author': 'Dev',
                'changed_files': ['a.py', 'b.py', 'c.py']
            },
            {
                'commit_hash': 'c2',
                'timestamp': 2,
                'author': 'Dev',
                'changed_files': ['a.py', 'b.py', 'c.py']
            },
            {
                'commit_hash': 'c3',
                'timestamp': 3,
                'author': 'Dev',
                'changed_files': ['a.py', 'b.py', 'c.py']
            },
            {
                'commit_hash': 'c4',
                'timestamp': 4,
                'author': 'Dev',
                'changed_files': ['a.py', 'b.py']
            },
            {
                'commit_hash': 'c5',
                'timestamp': 5,
                'author': 'Dev',
                'changed_files': ['a.py', 'c.py']
            },
            {
                'commit_hash': 'c6',
                'timestamp': 6,
                'author': 'Dev',
                'changed_files': ['b.py', 'c.py']
            }
        ]
        
        matrix = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        # Should have 3 coupling pairs (a-b, a-c, b-c) - all meet min_commits=3
        self.assertGreater(len(matrix), 0)
        
        # Check that pairs are sorted (file_a < file_b)
        for (file_a, file_b), data in matrix.items():
            self.assertLess(file_a, file_b)
            self.assertEqual(data.file_a, file_a)
            self.assertEqual(data.file_b, file_b)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_calculate_coupling_matrix_threshold_filtering(self, mock_get_history):
        """Test that low coupling scores are filtered out."""
        # a.py and b.py: 3 together out of 10 each = 0.3 (at threshold)
        # a.py and c.py: 2 together out of 10 each = 0.2 (below threshold)
        mock_get_history.return_value = [
            {'commit_hash': f'c{i}', 'timestamp': i, 'author': 'Dev', 
             'changed_files': ['a.py', 'b.py'] if i <= 3 else ['a.py']}
            for i in range(1, 11)
        ] + [
            {'commit_hash': f'c{i}', 'timestamp': i, 'author': 'Dev',
             'changed_files': ['a.py', 'c.py'] if i <= 2 else ['a.py']}
            for i in range(11, 21)
        ]
        
        analyzer = CouplingAnalyzer(min_coupling_threshold=0.3, min_commits=3)
        matrix = analyzer.calculate_coupling_matrix("/fake/repo")
        
        # a-b should be included (score = 3/3 = 1.0)
        # a-c should be excluded (score = 2/2 = 1.0 BUT only 2 commits, below min_commits)
        self.assertIn(('a.py', 'b.py'), matrix)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_calculate_coupling_matrix_min_commits_filtering(self, mock_get_history):
        """Test that pairs with too few co-changes are filtered out."""
        # a.py and b.py: only 2 co-changes (below min_commits=3)
        mock_get_history.return_value = [
            {
                'commit_hash': 'c1',
                'timestamp': 1,
                'author': 'Dev',
                'changed_files': ['a.py', 'b.py']
            },
            {
                'commit_hash': 'c2',
                'timestamp': 2,
                'author': 'Dev',
                'changed_files': ['a.py', 'b.py']
            }
        ]
        
        matrix = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        # Should be empty due to min_commits filter
        self.assertEqual(len(matrix), 0)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_get_coupled_files(self, mock_get_history):
        """Test getting coupled files for a target file."""
        mock_get_history.return_value = [
            {
                'commit_hash': f'c{i}',
                'timestamp': i,
                'author': 'Dev',
                'changed_files': ['target.py', f'file{j}.py']
            }
            for i in range(1, 10)
            for j in range(1, 4) if (i % j == 0)  # Different coupling strengths
        ]
        
        coupled = self.analyzer.get_coupled_files("/fake/repo", "target.py")
        
        # Should return list of (file, score) tuples
        self.assertIsInstance(coupled, list)
        
        if coupled:
            # Should be sorted by score descending
            scores = [score for _, score in coupled]
            self.assertEqual(scores, sorted(scores, reverse=True))
            
            # All scores should be between 0 and 1
            for _, score in coupled:
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_get_coupled_files_no_coupling(self, mock_get_history):
        """Test getting coupled files when target has no coupling."""
        mock_get_history.return_value = [
            {
                'commit_hash': 'c1',
                'timestamp': 1,
                'author': 'Dev',
                'changed_files': ['other.py', 'another.py']
            }
        ]
        
        coupled = self.analyzer.get_coupled_files("/fake/repo", "target.py")
        
        self.assertEqual(len(coupled), 0)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_get_strongest_couplings(self, mock_get_history):
        """Test getting strongest coupling pairs."""
        # Create mock data with varying coupling strengths
        mock_get_history.return_value = [
            {
                'commit_hash': f'c{i}',
                'timestamp': i,
                'author': 'Dev',
                'changed_files': [
                    'strong_a.py', 'strong_b.py'  # Always together
                ] if i <= 5 else [
                    'weak_a.py', 'weak_b.py'  # Together, but more individual changes
                ]
            }
            for i in range(1, 11)
        ]
        
        top_couplings = self.analyzer.get_strongest_couplings("/fake/repo", top_n=10)
        
        # Should return list of (file_a, file_b, score) tuples
        self.assertIsInstance(top_couplings, list)
        
        if top_couplings:
            # Should be sorted by score descending
            scores = [score for _, _, score in top_couplings]
            self.assertEqual(scores, sorted(scores, reverse=True))
            
            # Should respect top_n limit
            self.assertLessEqual(len(top_couplings), 10)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_get_strongest_couplings_respects_limit(self, mock_get_history):
        """Test that get_strongest_couplings respects top_n limit."""
        # Create many file pairs
        mock_get_history.return_value = [
            {
                'commit_hash': f'c{i}',
                'timestamp': i,
                'author': 'Dev',
                'changed_files': [f'file{j}.py' for j in range(10)]
            }
            for i in range(1, 10)
        ]
        
        top_3 = self.analyzer.get_strongest_couplings("/fake/repo", top_n=3)
        
        self.assertLessEqual(len(top_3), 3)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_caching_behavior(self, mock_get_history):
        """Test that coupling matrix is cached."""
        mock_get_history.return_value = [
            {
                'commit_hash': 'c1',
                'timestamp': 1,
                'author': 'Dev',
                'changed_files': ['a.py', 'b.py']
            }
        ]
        
        # First call should trigger calculation
        matrix1 = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        # Second call should use cache
        matrix2 = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        # Should be same object (cached)
        self.assertIs(matrix1, matrix2)
        
        # get_commit_history should only be called once
        self.assertEqual(mock_get_history.call_count, 1)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_force_recalculate(self, mock_get_history):
        """Test that force_recalculate bypasses cache."""
        mock_get_history.return_value = [
            {
                'commit_hash': 'c1',
                'timestamp': 1,
                'author': 'Dev',
                'changed_files': ['a.py', 'b.py']
            }
        ]
        
        # First call
        matrix1 = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        # Second call with force_recalculate
        matrix2 = self.analyzer.calculate_coupling_matrix("/fake/repo", force_recalculate=True)
        
        # get_commit_history should be called twice
        self.assertEqual(mock_get_history.call_count, 2)
    
    def test_clear_cache(self):
        """Test cache clearing."""
        # Populate cache (using mock)
        self.analyzer._coupling_matrix_cache["/repo1"] = {}
        self.analyzer._coupling_matrix_cache["/repo2"] = {}
        
        self.assertEqual(len(self.analyzer._coupling_matrix_cache), 2)
        
        self.analyzer.clear_cache()
        
        self.assertEqual(len(self.analyzer._coupling_matrix_cache), 0)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_coupling_score_calculation_accuracy(self, mock_get_history):
        """Test accuracy of coupling score calculation."""
        # a.py: 10 commits
        # b.py: 5 commits
        # Together: 4 commits
        # Expected score: 4 / min(10, 5) = 4 / 5 = 0.8
        
        mock_get_history.return_value = [
            {'commit_hash': f'c{i}', 'timestamp': i, 'author': 'Dev',
             'changed_files': ['a.py', 'b.py']}
            for i in range(1, 5)
        ] + [
            {'commit_hash': f'c{i}', 'timestamp': i, 'author': 'Dev',
             'changed_files': ['a.py']}
            for i in range(5, 11)
        ] + [
            {'commit_hash': f'c{i}', 'timestamp': i, 'author': 'Dev',
             'changed_files': ['b.py']}
            for i in range(11, 12)
        ]
        
        matrix = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        coupling = matrix[('a.py', 'b.py')]
        self.assertEqual(coupling.commits_together, 4)
        self.assertEqual(coupling.total_commits_a, 10)
        self.assertEqual(coupling.total_commits_b, 5)
        self.assertAlmostEqual(coupling.coupling_score, 0.8, places=2)


class TestCouplingAnalyzerEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CouplingAnalyzer()
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_single_file_in_commit(self, mock_get_history):
        """Test commits with only one file (no pairs)."""
        mock_get_history.return_value = [
            {
                'commit_hash': 'c1',
                'timestamp': 1,
                'author': 'Dev',
                'changed_files': ['only_file.py']
            }
        ]
        
        matrix = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        # No pairs possible
        self.assertEqual(len(matrix), 0)
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_all_files_change_together(self, mock_get_history):
        """Test scenario where all files always change together."""
        mock_get_history.return_value = [
            {
                'commit_hash': f'c{i}',
                'timestamp': i,
                'author': 'Dev',
                'changed_files': ['a.py', 'b.py', 'c.py']
            }
            for i in range(1, 10)
        ]
        
        matrix = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        # All pairs should have coupling score of 1.0
        for coupling in matrix.values():
            self.assertEqual(coupling.coupling_score, 1.0)
            self.assertEqual(coupling.strength, "VERY_HIGH")
    
    @patch('src.kpis.coupling.coupling_analyzer.get_commit_history')
    def test_file_path_sorting_in_pairs(self, mock_get_history):
        """Test that file pairs are always sorted (file_a < file_b)."""
        mock_get_history.return_value = [
            {
                'commit_hash': f'c{i}',
                'timestamp': i,
                'author': 'Dev',
                'changed_files': ['z.py', 'a.py', 'm.py']
            }
            for i in range(1, 5)
        ]
        
        matrix = self.analyzer.calculate_coupling_matrix("/fake/repo")
        
        for (file_a, file_b) in matrix.keys():
            self.assertLess(file_a, file_b)


if __name__ == '__main__':
    unittest.main()
