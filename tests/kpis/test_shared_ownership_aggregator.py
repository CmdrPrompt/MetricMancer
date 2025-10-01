import unittest
from unittest.mock import Mock
from src.kpis.sharedcodeownership.shared_ownership_aggregator import (
    SharedOwnershipAggregatorKPI, 
    SharedOwnershipStats,
    aggregate_shared_ownership_for_directory,
    aggregate_shared_ownership_for_repository
)

class TestSharedOwnershipAggregator(unittest.TestCase):
    
    def create_mock_file(self, filename: str, significant_authors: int, error: bool = False):
        """Create a mock file with SharedOwnership KPI."""
        file_obj = Mock()
        file_obj.name = filename
        file_obj.file_path = filename
        
        shared_ownership_kpi = Mock()
        if error:
            shared_ownership_kpi.value = {'error': 'Test error'}
        else:
            shared_ownership_kpi.value = {'significant_authors': significant_authors}
        
        file_obj.kpis = {'Shared Ownership': shared_ownership_kpi}
        return file_obj
    
    def test_shared_ownership_stats_dataclass(self):
        """Test SharedOwnershipStats dataclass initialization and properties."""
        stats = SharedOwnershipStats()
        
        # Test defaults
        self.assertEqual(stats.total_files, 0)
        self.assertEqual(stats.files_with_shared_ownership, 0)
        self.assertEqual(stats.files_with_single_owner, 0)
        self.assertEqual(stats.files_with_no_significant_owner, 0)
        self.assertEqual(stats.files_with_error, 0)
        self.assertIsNotNone(stats.shared_ownership_distribution)
        self.assertEqual(len(stats.shared_ownership_distribution), 0)
        
        # Test properties with zero files
        self.assertEqual(stats.shared_ownership_percentage, 0.0)
        self.assertEqual(stats.single_ownership_percentage, 0.0)
        self.assertEqual(stats.average_authors_per_file, 0.0)
    
    def test_shared_ownership_stats_properties(self):
        """Test SharedOwnershipStats property calculations."""
        stats = SharedOwnershipStats()
        stats.total_files = 10
        stats.files_with_shared_ownership = 3
        stats.files_with_single_owner = 6
        stats.files_with_no_significant_owner = 1
        stats.shared_ownership_distribution = {0: 1, 1: 6, 2: 2, 3: 1}
        
        # Test percentages
        self.assertEqual(stats.shared_ownership_percentage, 30.0)  # 3/10 * 100
        self.assertEqual(stats.single_ownership_percentage, 60.0)   # 6/10 * 100
        
        # Test average authors: (0*1 + 1*6 + 2*2 + 3*1) / 10 = 13/10 = 1.3
        self.assertEqual(stats.average_authors_per_file, 1.3)
    
    def test_aggregator_initialization(self):
        """Test aggregator KPI initialization."""
        aggregator = SharedOwnershipAggregatorKPI()
        
        self.assertEqual(aggregator.name, "Shared Ownership Aggregation")
        self.assertIn("Aggregated", aggregator.description)
    
    def test_aggregator_basic_statistics(self):
        """Test basic aggregation statistics."""
        files = [
            self.create_mock_file("file1.py", 2),  # Shared
            self.create_mock_file("file2.py", 1),  # Single
            self.create_mock_file("file3.py", 0),  # No significant
            self.create_mock_file("file4.py", 3),  # Shared
        ]
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate(files)
        
        self.assertEqual(stats.total_files, 4)
        self.assertEqual(stats.files_with_shared_ownership, 2)  # file1, file4
        self.assertEqual(stats.files_with_single_owner, 1)      # file2
        self.assertEqual(stats.files_with_no_significant_owner, 1)  # file3
        self.assertEqual(stats.files_with_error, 0)
    
    def test_aggregator_percentages(self):
        """Test percentage calculations."""
        files = [
            self.create_mock_file("file1.py", 2),  # Shared
            self.create_mock_file("file2.py", 1),  # Single
            self.create_mock_file("file3.py", 1),  # Single
            self.create_mock_file("file4.py", 3),  # Shared
        ]
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate(files)
        
        self.assertEqual(stats.shared_ownership_percentage, 50.0)  # 2/4 * 100
        self.assertEqual(stats.single_ownership_percentage, 50.0)   # 2/4 * 100
    
    def test_aggregator_distribution(self):
        """Test author distribution tracking."""
        files = [
            self.create_mock_file("file1.py", 1),
            self.create_mock_file("file2.py", 1),
            self.create_mock_file("file3.py", 2),
            self.create_mock_file("file4.py", 3),
            self.create_mock_file("file5.py", 3),
        ]
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate(files)
        
        expected_distribution = {1: 2, 2: 1, 3: 2}
        self.assertEqual(stats.shared_ownership_distribution, expected_distribution)
        
        # Test calculated average: (1*2 + 2*1 + 3*2) / 5 = (2 + 2 + 6) / 5 = 2.0
        self.assertEqual(stats.average_authors_per_file, 2.0)
    
    def test_aggregator_most_shared_file(self):
        """Test most shared file tracking."""
        files = [
            self.create_mock_file("simple.py", 1),
            self.create_mock_file("shared.py", 2),
            self.create_mock_file("very_shared.py", 5),
            self.create_mock_file("another.py", 3),
        ]
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate(files)
        
        self.assertEqual(stats.most_shared_file, "very_shared.py")
        self.assertEqual(stats.most_shared_authors, 5)
    
    def test_aggregator_average_authors(self):
        """Test average authors per file calculation."""
        files = [
            self.create_mock_file("file1.py", 1),  # 1 author
            self.create_mock_file("file2.py", 2),  # 2 authors
            self.create_mock_file("file3.py", 3),  # 3 authors
        ]
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate(files)
        
        # (1 + 2 + 3) / 3 = 2.0
        self.assertEqual(stats.average_authors_per_file, 2.0)
    
    def test_aggregator_handles_errors(self):
        """Test error handling in aggregation."""
        files = [
            self.create_mock_file("good.py", 2),
            self.create_mock_file("error.py", 0, error=True),
        ]
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate(files)
        
        self.assertEqual(stats.total_files, 2)
        self.assertEqual(stats.files_with_shared_ownership, 1)
        self.assertEqual(stats.files_with_error, 1)
    
    def test_aggregator_missing_shared_ownership_kpi(self):
        """Test handling of files without SharedOwnership KPI."""
        file_obj = Mock()
        file_obj.name = "no_kpi.py"
        file_obj.file_path = "no_kpi.py"
        file_obj.kpis = {}  # No SharedOwnership KPI
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate([file_obj])
        
        self.assertEqual(stats.total_files, 1)
        self.assertEqual(stats.files_with_error, 1)
    
    def test_aggregator_invalid_kpi_value(self):
        """Test handling of invalid SharedOwnership KPI values."""
        file_obj = Mock()
        file_obj.name = "invalid.py"
        file_obj.file_path = "invalid.py"
        
        shared_ownership_kpi = Mock()
        shared_ownership_kpi.value = "invalid_format"  # Not a dict
        
        file_obj.kpis = {'Shared Ownership': shared_ownership_kpi}
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate([file_obj])
        
        self.assertEqual(stats.total_files, 1)
        self.assertEqual(stats.files_with_error, 1)
    
    def test_aggregator_empty_files(self):
        """Test aggregation with no files."""
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate([])
        
        self.assertEqual(stats.total_files, 0)
        self.assertEqual(stats.files_with_shared_ownership, 0)
        self.assertEqual(stats.files_with_single_owner, 0)
        self.assertEqual(stats.files_with_no_significant_owner, 0)
        self.assertEqual(stats.files_with_error, 0)
        self.assertEqual(stats.shared_ownership_percentage, 0.0)
        self.assertEqual(stats.average_authors_per_file, 0.0)
    
    def test_aggregator_exception_handling(self):
        """Test aggregator handles exceptions gracefully."""
        # Create mock file that will cause an exception during processing
        file_obj = Mock()
        file_obj.name = "exception.py"
        file_obj.kpis = {'Shared Ownership': None}  # This will cause AttributeError
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate([file_obj])
        
        # Should return error stats
        self.assertEqual(stats.total_files, 1)
        self.assertEqual(stats.files_with_error, 1)
        
        # In current implementation, value is set to the stats object, not error dict
        self.assertIsInstance(aggregator.value, SharedOwnershipStats)
        self.assertEqual(aggregator.value.files_with_error, 1)
    
    def test_convenience_functions(self):
        """Test convenience functions for directory and repository aggregation."""
        files = [
            self.create_mock_file("file1.py", 2),
            self.create_mock_file("file2.py", 1),
        ]
        
        # Test directory aggregation
        dir_stats = aggregate_shared_ownership_for_directory(files)
        self.assertIsInstance(dir_stats, SharedOwnershipStats)
        self.assertEqual(dir_stats.total_files, 2)
        self.assertEqual(dir_stats.files_with_shared_ownership, 1)
        
        # Test repository aggregation
        repo_stats = aggregate_shared_ownership_for_repository(files)
        self.assertIsInstance(repo_stats, SharedOwnershipStats)
        self.assertEqual(repo_stats.total_files, 2)
        self.assertEqual(repo_stats.files_with_single_owner, 1)
    
    def test_aggregator_realistic_scenario(self):
        """Test aggregator with realistic file distribution."""
        files = [
            # Package 1: mostly single ownership
            self.create_mock_file("pkg1/file1.py", 1),
            self.create_mock_file("pkg1/file2.py", 1),
            self.create_mock_file("pkg1/file3.py", 2),  # Some collaboration
            
            # Package 2: more collaboration
            self.create_mock_file("pkg2/shared1.py", 3),
            self.create_mock_file("pkg2/shared2.py", 2),
            self.create_mock_file("pkg2/single.py", 1),
            
            # Package 3: mixed with some issues
            self.create_mock_file("pkg3/old.py", 0),     # Below threshold
            self.create_mock_file("pkg3/error.py", 0, error=True),
            self.create_mock_file("pkg3/active.py", 4),  # High collaboration
        ]
        
        aggregator = SharedOwnershipAggregatorKPI()
        stats = aggregator.calculate(files)
        
        # Verify totals
        self.assertEqual(stats.total_files, 9)
        self.assertEqual(stats.files_with_shared_ownership, 4)  # 2, 3, 2, 4 authors
        self.assertEqual(stats.files_with_single_owner, 3)     # 3 files with 1 author
        self.assertEqual(stats.files_with_no_significant_owner, 1)  # 1 file with 0 authors
        self.assertEqual(stats.files_with_error, 1)
        
        # Verify percentages
        expected_shared_pct = (4 / 9) * 100  # ≈ 44.44%
        expected_single_pct = (3 / 9) * 100  # ≈ 33.33%
        
        self.assertAlmostEqual(stats.shared_ownership_percentage, expected_shared_pct, places=1)
        self.assertAlmostEqual(stats.single_ownership_percentage, expected_single_pct, places=1)
        
        # Verify most shared file
        self.assertEqual(stats.most_shared_file, "pkg3/active.py")
        self.assertEqual(stats.most_shared_authors, 4)
        
        # Verify distribution
        expected_distribution = {0: 1, 1: 3, 2: 2, 3: 1, 4: 1}
        self.assertEqual(stats.shared_ownership_distribution, expected_distribution)

if __name__ == '__main__':
    unittest.main()