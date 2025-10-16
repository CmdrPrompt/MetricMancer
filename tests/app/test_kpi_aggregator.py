"""
Test suite for KPIAggregator (Phase 4).

Tests the aggregation of KPIs across directory hierarchies using the Composite pattern.
This test suite follows TDD approach and covers:
- File-level KPI aggregation
- Directory-level KPI aggregation  
- Recursive aggregation through subdirectories
- Custom aggregation functions
- Edge cases and error handling

Test Coverage Goals:
- 100% statement coverage
- All aggregation paths tested
- Integration with Phase 1-3 components verified
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.app.kpi_aggregator import KPIAggregator
from src.kpis.complexity import ComplexityKPI
from src.kpis.codechurn import ChurnKPI
from src.kpis.hotspot import HotspotKPI


class TestKPIAggregatorInit:
    """Test KPIAggregator initialization."""
    
    def test_init_with_no_functions(self):
        """Should initialize with empty aggregation functions dict."""
        aggregator = KPIAggregator()
        assert aggregator.aggregation_functions == {}
    
    def test_init_with_custom_functions(self):
        """Should initialize with provided aggregation functions."""
        custom_funcs = {'complexity': sum, 'hotspot': max}
        aggregator = KPIAggregator(aggregation_functions=custom_funcs)
        assert aggregator.aggregation_functions == custom_funcs
    
    def test_init_with_none_functions(self):
        """Should handle None explicitly and use empty dict."""
        aggregator = KPIAggregator(aggregation_functions=None)
        assert aggregator.aggregation_functions == {}


class TestAggregateFile:
    """Test file-level KPI aggregation."""
    
    def test_aggregate_file_with_kpis(self):
        """Should extract KPI values from file object."""
        aggregator = KPIAggregator()
        
        # Create mock file with KPIs
        file_obj = Mock()
        file_obj.name = "test.py"
        file_obj.kpis = {
            'complexity': Mock(value=10),
            'churn': Mock(value=5),
            'hotspot': Mock(value=7)
        }
        
        result = aggregator.aggregate_file(file_obj)
        
        assert result == {
            'complexity': 10,
            'churn': 5,
            'hotspot': 7
        }
    
    def test_aggregate_file_none_object(self):
        """Should return empty dict for None file."""
        aggregator = KPIAggregator()
        result = aggregator.aggregate_file(None)
        assert result == {}
    
    def test_aggregate_file_no_kpis_attribute(self):
        """Should return empty dict when file has no kpis."""
        aggregator = KPIAggregator()
        file_obj = Mock(spec=['name'])  # No kpis attribute
        file_obj.name = "test.py"
        
        result = aggregator.aggregate_file(file_obj)
        assert result == {}
    
    def test_aggregate_file_with_none_kpis(self):
        """Should return empty dict when kpis is None."""
        aggregator = KPIAggregator()
        file_obj = Mock()
        file_obj.kpis = None
        
        result = aggregator.aggregate_file(file_obj)
        assert result == {}
    
    def test_aggregate_file_with_none_kpi_values(self):
        """Should skip KPIs with None value."""
        aggregator = KPIAggregator()
        
        file_obj = Mock()
        file_obj.name = "test.py"
        file_obj.kpis = {
            'complexity': Mock(value=10),
            'churn': Mock(value=None),  # None value
            'hotspot': None  # None KPI object
        }
        
        result = aggregator.aggregate_file(file_obj)
        
        # Should only include complexity
        assert result == {'complexity': 10}
    
    def test_aggregate_file_with_no_value_attribute(self):
        """Should skip KPIs without value attribute."""
        aggregator = KPIAggregator()
        
        file_obj = Mock()
        file_obj.name = "test.py"
        file_obj.kpis = {
            'complexity': Mock(value=10),
            'invalid': Mock(spec=['name'])  # No value attribute
        }
        
        result = aggregator.aggregate_file(file_obj)
        assert result == {'complexity': 10}
    
    def test_aggregate_file_handles_exception(self):
        """Should handle exceptions gracefully and return empty dict."""
        aggregator = KPIAggregator()
        
        file_obj = Mock()
        file_obj.name = "test.py"
        # Make getattr raise exception
        file_obj.kpis = property(lambda self: 1/0)
        
        result = aggregator.aggregate_file(file_obj)
        assert result == {}


class TestAggregateDirectory:
    """Test directory-level KPI aggregation."""
    
    def test_aggregate_directory_with_only_files(self):
        """Should aggregate KPIs from files in directory."""
        aggregator = KPIAggregator()
        
        # Create mock files
        file1 = Mock()
        file1.name = "file1.py"
        file1.kpis = {
            'complexity': Mock(value=10),
            'churn': Mock(value=5)
        }
        
        file2 = Mock()
        file2.name = "file2.py"
        file2.kpis = {
            'complexity': Mock(value=20),
            'churn': Mock(value=15)
        }
        
        # Create directory with files
        dir_obj = Mock()
        dir_obj.name = "src"
        dir_obj.files = [file1, file2]
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        # Default aggregation is sum
        assert result == {
            'complexity': 30,  # 10 + 20
            'churn': 20        # 5 + 15
        }
    
    def test_aggregate_directory_with_subdirectories(self):
        """Should recursively aggregate from subdirectories."""
        aggregator = KPIAggregator()
        
        # Create files in subdirectory
        file1 = Mock()
        file1.name = "sub/file1.py"
        file1.kpis = {'complexity': Mock(value=10)}
        
        # Create subdirectory
        subdir = Mock()
        subdir.name = "sub"
        subdir.files = [file1]
        subdir.children = []
        subdir.kpis = {}
        
        # Create files in parent
        file2 = Mock()
        file2.name = "file2.py"
        file2.kpis = {'complexity': Mock(value=20)}
        
        # Create parent directory
        parent = Mock()
        parent.name = "src"
        parent.files = [file2]
        parent.children = [subdir]
        parent.kpis = {}
        
        result = aggregator.aggregate_directory(parent)
        
        # Should aggregate both subdirectory and parent files
        assert result == {'complexity': 30}  # 10 + 20
    
    def test_aggregate_directory_custom_function_max(self):
        """Should use custom aggregation function (max)."""
        aggregator = KPIAggregator(aggregation_functions={'hotspot': max})
        
        file1 = Mock()
        file1.kpis = {'hotspot': Mock(value=5)}
        
        file2 = Mock()
        file2.kpis = {'hotspot': Mock(value=15)}
        
        file3 = Mock()
        file3.kpis = {'hotspot': Mock(value=10)}
        
        dir_obj = Mock()
        dir_obj.name = "src"
        dir_obj.files = [file1, file2, file3]
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        # Should use max instead of sum
        assert result == {'hotspot': 15}
    
    def test_aggregate_directory_custom_function_average(self):
        """Should use custom aggregation function (average)."""
        def average(values):
            return sum(values) / len(values) if values else 0
        
        aggregator = KPIAggregator(aggregation_functions={'complexity': average})
        
        file1 = Mock()
        file1.kpis = {'complexity': Mock(value=10)}
        
        file2 = Mock()
        file2.kpis = {'complexity': Mock(value=20)}
        
        file3 = Mock()
        file3.kpis = {'complexity': Mock(value=30)}
        
        dir_obj = Mock()
        dir_obj.name = "src"
        dir_obj.files = [file1, file2, file3]
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        # Average of 10, 20, 30 = 20
        assert result == {'complexity': 20}
    
    def test_aggregate_directory_updates_kpis_dict(self):
        """Should update directory's kpis dict with aggregated values."""
        aggregator = KPIAggregator()
        
        file1 = Mock()
        file1.kpis = {'complexity': Mock(value=10)}
        
        dir_obj = Mock()
        dir_obj.name = "src"
        dir_obj.files = [file1]
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        # Should update kpis dict
        assert 'complexity' in dir_obj.kpis
        assert dir_obj.kpis['complexity'].value == 10
        assert dir_obj.kpis['complexity'].name == 'complexity'
    
    def test_aggregate_directory_empty_directory(self):
        """Should handle directory with no files or children."""
        aggregator = KPIAggregator()
        
        dir_obj = Mock()
        dir_obj.name = "empty"
        dir_obj.files = []
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        assert result == {}
    
    def test_aggregate_directory_no_files_attribute(self):
        """Should handle directory without files attribute."""
        aggregator = KPIAggregator()
        
        dir_obj = Mock(spec=['name', 'children', 'kpis'])
        dir_obj.name = "src"
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        assert result == {}
    
    def test_aggregate_directory_no_children_attribute(self):
        """Should handle directory without children attribute."""
        aggregator = KPIAggregator()
        
        file1 = Mock()
        file1.kpis = {'complexity': Mock(value=10)}
        
        dir_obj = Mock(spec=['name', 'files', 'kpis'])
        dir_obj.name = "src"
        dir_obj.files = [file1]
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        # Should still aggregate files
        assert result == {'complexity': 10}
    
    def test_aggregate_directory_aggregation_error(self):
        """Should handle aggregation errors gracefully."""
        def bad_aggregation(values):
            raise ValueError("Aggregation failed")
        
        aggregator = KPIAggregator(aggregation_functions={'complexity': bad_aggregation})
        
        file1 = Mock()
        file1.kpis = {'complexity': Mock(value=10)}
        
        dir_obj = Mock()
        dir_obj.name = "src"
        dir_obj.files = [file1]
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        # Should skip failed KPI
        assert result == {}
    
    def test_aggregate_directory_deep_hierarchy(self):
        """Should handle deep directory hierarchies."""
        aggregator = KPIAggregator()
        
        # Level 3 (deepest)
        file_deep = Mock()
        file_deep.kpis = {'complexity': Mock(value=5)}
        
        dir_deep = Mock()
        dir_deep.name = "deep"
        dir_deep.files = [file_deep]
        dir_deep.children = []
        dir_deep.kpis = {}
        
        # Level 2
        file_mid = Mock()
        file_mid.kpis = {'complexity': Mock(value=10)}
        
        dir_mid = Mock()
        dir_mid.name = "mid"
        dir_mid.files = [file_mid]
        dir_mid.children = [dir_deep]
        dir_mid.kpis = {}
        
        # Level 1 (root)
        file_root = Mock()
        file_root.kpis = {'complexity': Mock(value=15)}
        
        dir_root = Mock()
        dir_root.name = "root"
        dir_root.files = [file_root]
        dir_root.children = [dir_mid]
        dir_root.kpis = {}
        
        result = aggregator.aggregate_directory(dir_root)
        
        # Should aggregate all levels: 15 + 10 + 5 = 30
        assert result == {'complexity': 30}
    
    def test_aggregate_directory_multiple_kpi_types(self):
        """Should aggregate multiple KPI types simultaneously."""
        aggregator = KPIAggregator()
        
        file1 = Mock()
        file1.kpis = {
            'complexity': Mock(value=10),
            'churn': Mock(value=5),
            'hotspot': Mock(value=7)
        }
        
        file2 = Mock()
        file2.kpis = {
            'complexity': Mock(value=20),
            'churn': Mock(value=15),
            'hotspot': Mock(value=13)
        }
        
        dir_obj = Mock()
        dir_obj.name = "src"
        dir_obj.files = [file1, file2]
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        assert result == {
            'complexity': 30,
            'churn': 20,
            'hotspot': 20
        }
    
    def test_aggregate_directory_handles_exception(self):
        """Should handle exceptions in directory processing."""
        aggregator = KPIAggregator()
        
        # Mock object that raises exception
        dir_obj = Mock()
        dir_obj.name = "src"
        # Make getattr raise exception
        type(dir_obj).files = property(lambda self: 1/0)
        
        result = aggregator.aggregate_directory(dir_obj)
        
        # Should return empty dict on exception
        assert result == {}


class TestKPIAggregatorIntegration:
    """Integration tests with real KPI objects."""
    
    def test_aggregate_with_real_complexity_kpi(self):
        """Should work with actual ComplexityKPI objects."""
        aggregator = KPIAggregator()
        
        file1 = Mock()
        file1.name = "file1.py"
        file1.kpis = {
            'complexity': ComplexityKPI(value=10)
        }
        
        file2 = Mock()
        file2.name = "file2.py"
        file2.kpis = {
            'complexity': ComplexityKPI(value=20)
        }
        
        dir_obj = Mock()
        dir_obj.name = "src"
        dir_obj.files = [file1, file2]
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        assert result == {'complexity': 30}
        assert isinstance(dir_obj.kpis['complexity'].value, (int, float))
    
    def test_aggregate_with_real_churn_kpi(self):
        """Should work with actual ChurnKPI objects."""
        aggregator = KPIAggregator()
        
        file1 = Mock()
        file1.kpis = {'churn': ChurnKPI(value=5)}
        
        file2 = Mock()
        file2.kpis = {'churn': ChurnKPI(value=15)}
        
        dir_obj = Mock()
        dir_obj.name = "src"
        dir_obj.files = [file1, file2]
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        assert result == {'churn': 20}
    
    def test_aggregate_with_mixed_real_kpis(self):
        """Should work with multiple real KPI types."""
        aggregator = KPIAggregator()
        
        file1 = Mock()
        file1.kpis = {
            'complexity': ComplexityKPI(value=10),
            'churn': ChurnKPI(value=5),
            'hotspot': HotspotKPI(value=7)
        }
        
        dir_obj = Mock()
        dir_obj.name = "src"
        dir_obj.files = [file1]
        dir_obj.children = []
        dir_obj.kpis = {}
        
        result = aggregator.aggregate_directory(dir_obj)
        
        assert result['complexity'] == 10
        assert result['churn'] == 5
        assert result['hotspot'] == 7
