"""SharedOwnership aggregation for packages and repositories."""

from typing import Dict, List, Optional, Any, Mapping, Union
from dataclasses import field
from dataclasses import dataclass
from ..base_kpi import BaseKPI


@dataclass
class SharedOwnershipStats:
    """Statistics for SharedOwnership at package/repo level."""
    total_files: int = 0
    files_with_shared_ownership: int = 0  # Files with 2+ significant authors
    files_with_single_owner: int = 0      # Files with 1 significant author
    files_with_no_significant_owner: int = 0  # Files below threshold
    files_with_error: int = 0             # Files with calculation errors
    # Detailed breakdown
    shared_ownership_distribution: Dict[int, int] = field(default_factory=dict)  # {num_authors: count}
    most_shared_file: Optional[str] = None
    most_shared_authors: int = 0
    def __post_init__(self):
        if self.shared_ownership_distribution is None:
            self.shared_ownership_distribution = {}
    @property
    def shared_ownership_percentage(self) -> float:
        """Percentage of files with shared ownership (2+ authors)."""
        if self.total_files == 0:
            return 0.0
        return (self.files_with_shared_ownership / self.total_files) * 100
    @property
    def single_ownership_percentage(self) -> float:
        """Percentage of files with single ownership."""
        if self.total_files == 0:
            return 0.0
        return (self.files_with_single_owner / self.total_files) * 100
    @property
    def average_authors_per_file(self) -> float:
        """Average number of significant authors per file."""
        if self.total_files == 0:
            return 0.0
        total_authors = 0
        for num_authors, file_count in self.shared_ownership_distribution.items():
            total_authors += num_authors * file_count
        return total_authors / self.total_files


class SharedOwnershipAggregatorKPI(BaseKPI):
    """Aggregates SharedOwnership statistics for packages and repositories."""
    
    def __init__(self):
        super().__init__("Shared Ownership Aggregation")
        self.description = "Aggregated SharedOwnership statistics for directories and repositories"
    
    def calculate(self, files: List[Any]) -> SharedOwnershipStats:
        """
        Calculate aggregated SharedOwnership statistics for a collection of files.
        
        Args:
            files: List of File objects with SharedOwnership KPIs
            
        Returns:
            SharedOwnershipStats with aggregated data
        """
        try:
            stats = SharedOwnershipStats()
            stats.shared_ownership_distribution = {}
            
            for file_obj in files:
                stats.total_files += 1
                
                # Get SharedOwnership KPI from file
                shared_ownership_kpi = file_obj.kpis.get('Shared Ownership')
                if not shared_ownership_kpi or not hasattr(shared_ownership_kpi, 'value'):
                    stats.files_with_error += 1
                    continue
                
                shared_ownership_value = shared_ownership_kpi.value
                
                if isinstance(shared_ownership_value, dict) and 'error' in shared_ownership_value:
                    stats.files_with_error += 1
                    continue
                
                if isinstance(shared_ownership_value, Mapping) and 'significant_authors' in shared_ownership_value:
                    num_authors = shared_ownership_value['significant_authors']
                    
                    # Count distribution
                    stats.shared_ownership_distribution[num_authors] = (
                        stats.shared_ownership_distribution.get(num_authors, 0) + 1
                    )
                    
                    # Categorize files
                    if num_authors >= 2:
                        stats.files_with_shared_ownership += 1
                        
                        # Track most shared file
                        if num_authors > stats.most_shared_authors:
                            stats.most_shared_authors = num_authors
                            stats.most_shared_file = file_obj.name
                    
                    elif num_authors == 1:
                        stats.files_with_single_owner += 1
                    
                    else:  # num_authors == 0
                        stats.files_with_no_significant_owner += 1
                
                else:
                    # Unexpected format
                    stats.files_with_error += 1
            
            self.value = stats
            return stats
        
        except Exception as e:
            # Create error stats but also store error in value
            error_stats = SharedOwnershipStats()
            error_stats.total_files = len(files) if files else 0
            error_stats.files_with_error = len(files) if files else 0
            
            # Store error in KPI value for debugging
            self.value = {'error': str(e), 'stats': error_stats}
            return error_stats


def aggregate_shared_ownership_for_directory(directory_files: List[Any]) -> SharedOwnershipStats:
    """
    Convenience function to aggregate SharedOwnership for a directory.
    
    Args:
        directory_files: List of File objects in the directory
        
    Returns:
        SharedOwnershipStats for the directory
    """
    aggregator = SharedOwnershipAggregatorKPI()
    return aggregator.calculate(directory_files)


def aggregate_shared_ownership_for_repository(repo_files: List[Any]) -> SharedOwnershipStats:
    """
    Convenience function to aggregate SharedOwnership for entire repository.
    
    Args:
        repo_files: List of all File objects in the repository
        
    Returns:
        SharedOwnershipStats for the repository
    """
    aggregator = SharedOwnershipAggregatorKPI()
    return aggregator.calculate(repo_files)
