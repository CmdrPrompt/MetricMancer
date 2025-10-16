"""
Tests for KPIAggregator class.

KPIAggregator is responsible for aggregating KPIs across the directory hierarchy
using the Composite pattern. It takes individual file KPIs and aggregates them
up through directories to create a complete hierarchical view.

This follows the TDD RED-GREEN-REFACTOR cycle.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Import will fail initially (RED phase)
from app.processing.kpi_aggregator import KPIAggregator


class MockKPI:
    """Mock KPI class for testing."""
    def __init__(self, name="MockKPI", value=42):
        self.name = name
        self.value = value


class MockDirectory:
    """Mock Directory class for testing."""
    def __init__(self, name, path, parent=None):
        self.name = name
        self.path = path
        self.parent = parent
        self.kpis = {}
        self.children = []
        self.files = []
    
    def add_child(self, child):
        self.children.append(child)
        child.parent = self
    
    def add_file(self, file):
        self.files.append(file)


class MockFile:
    """Mock File class for testing."""
    def __init__(self, name, file_path, kpis=None):
        self.name = name
        self.file_path = file_path
        self.kpis = kpis if kpis is not None else {}


class TestKPIAggregatorInitialization(unittest.TestCase):
    """Test KPIAggregator initialization."""
    
    def test_init_default(self):
        """Test initialization with default parameters."""
        aggregator = KPIAggregator()
        
        self.assertIsNotNone(aggregator)
        self.assertIsInstance(aggregator, KPIAggregator)
    
    def test_init_with_custom_aggregation_functions(self):
        """Test initialization with custom aggregation functions."""
        custom_funcs = {
            "complexity": lambda values: sum(values),
            "churn": lambda values: max(values) if values else 0
        }
        
        aggregator = KPIAggregator(aggregation_functions=custom_funcs)
        
        self.assertIsNotNone(aggregator)
        self.assertEqual(len(aggregator.aggregation_functions), 2)


class TestKPIAggregatorAggregateFile(unittest.TestCase):
    """Test aggregation for individual files."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aggregator = KPIAggregator()
    
    def test_aggregate_file_with_kpis(self):
        """Test aggregating KPIs from a file."""
        mock_file = MockFile(
            name="test.py",
            file_path="src/test.py",
            kpis={
                "complexity": MockKPI("complexity", 10),
                "churn": MockKPI("churn", 5)
            }
        )
        
        result = self.aggregator.aggregate_file(mock_file)
        
        self.assertIsNotNone(result)
        self.assertIn("complexity", result)
        self.assertIn("churn", result)
        self.assertEqual(result["complexity"], 10)
        self.assertEqual(result["churn"], 5)
    
    def test_aggregate_file_with_no_kpis(self):
        """Test aggregating file with no KPIs."""
        mock_file = MockFile(name="empty.py", file_path="src/empty.py", kpis={})
        
        result = self.aggregator.aggregate_file(mock_file)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, {})
    
    def test_aggregate_file_with_none_kpis(self):
        """Test aggregating file with None KPIs."""
        mock_file = MockFile(name="test.py", file_path="src/test.py")
        mock_file.kpis = None
        
        result = self.aggregator.aggregate_file(mock_file)
        
        # Should handle None gracefully
        self.assertIsNotNone(result)


class TestKPIAggregatorAggregateDirectory(unittest.TestCase):
    """Test aggregation for directories (Composite pattern)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aggregator = KPIAggregator()
    
    def test_aggregate_empty_directory(self):
        """Test aggregating empty directory."""
        mock_dir = MockDirectory(name="empty", path="src/empty")
        
        result = self.aggregator.aggregate_directory(mock_dir)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, {})
    
    def test_aggregate_directory_with_files_only(self):
        """Test aggregating directory with only files."""
        mock_dir = MockDirectory(name="src", path="src")
        
        # Add files with KPIs
        file1 = MockFile("test1.py", "src/test1.py", {
            "complexity": MockKPI("complexity", 10),
            "churn": MockKPI("churn", 3)
        })
        file2 = MockFile("test2.py", "src/test2.py", {
            "complexity": MockKPI("complexity", 15),
            "churn": MockKPI("churn", 7)
        })
        
        mock_dir.add_file(file1)
        mock_dir.add_file(file2)
        
        result = self.aggregator.aggregate_directory(mock_dir)
        
        # Should aggregate KPIs from both files
        self.assertIsNotNone(result)
        self.assertIn("complexity", result)
        self.assertIn("churn", result)
        # Default aggregation is sum
        self.assertEqual(result["complexity"], 25)  # 10 + 15
        self.assertEqual(result["churn"], 10)  # 3 + 7
    
    def test_aggregate_directory_with_subdirectories(self):
        """Test aggregating directory with subdirectories (recursive)."""
        # Create hierarchy: root/
        #                    ├── file1.py
        #                    └── subdir/
        #                        └── file2.py
        
        root = MockDirectory(name="root", path="root")
        subdir = MockDirectory(name="subdir", path="root/subdir")
        
        file1 = MockFile("file1.py", "root/file1.py", {
            "complexity": MockKPI("complexity", 10)
        })
        file2 = MockFile("file2.py", "root/subdir/file2.py", {
            "complexity": MockKPI("complexity", 20)
        })
        
        root.add_file(file1)
        root.add_child(subdir)
        subdir.add_file(file2)
        
        result = self.aggregator.aggregate_directory(root)
        
        # Should aggregate from both levels
        self.assertIsNotNone(result)
        self.assertIn("complexity", result)
        self.assertEqual(result["complexity"], 30)  # 10 + 20
    
    def test_aggregate_directory_updates_directory_kpis(self):
        """Test that aggregation updates the directory's KPI dictionary."""
        mock_dir = MockDirectory(name="src", path="src")
        
        file1 = MockFile("test.py", "src/test.py", {
            "complexity": MockKPI("complexity", 15)
        })
        mock_dir.add_file(file1)
        
        # Initially empty
        self.assertEqual(mock_dir.kpis, {})
        
        self.aggregator.aggregate_directory(mock_dir)
        
        # Should now have aggregated KPIs
        self.assertNotEqual(mock_dir.kpis, {})
        self.assertIn("complexity", mock_dir.kpis)


class TestKPIAggregatorAggregationStrategies(unittest.TestCase):
    """Test different aggregation strategies."""
    
    def test_sum_aggregation(self):
        """Test sum aggregation strategy (default)."""
        aggregator = KPIAggregator()
        
        mock_dir = MockDirectory(name="src", path="src")
        mock_dir.add_file(MockFile("f1.py", "src/f1.py", {
            "complexity": MockKPI("complexity", 10)
        }))
        mock_dir.add_file(MockFile("f2.py", "src/f2.py", {
            "complexity": MockKPI("complexity", 20)
        }))
        
        result = aggregator.aggregate_directory(mock_dir)
        
        self.assertEqual(result["complexity"], 30)
    
    def test_max_aggregation(self):
        """Test max aggregation strategy."""
        aggregator = KPIAggregator(aggregation_functions={
            "hotspot": lambda values: max(values) if values else 0
        })
        
        mock_dir = MockDirectory(name="src", path="src")
        mock_dir.add_file(MockFile("f1.py", "src/f1.py", {
            "hotspot": MockKPI("hotspot", 7)
        }))
        mock_dir.add_file(MockFile("f2.py", "src/f2.py", {
            "hotspot": MockKPI("hotspot", 3)
        }))
        
        result = aggregator.aggregate_directory(mock_dir)
        
        self.assertEqual(result["hotspot"], 7)  # max(7, 3)
    
    def test_average_aggregation(self):
        """Test average aggregation strategy."""
        aggregator = KPIAggregator(aggregation_functions={
            "ownership": lambda values: sum(values) / len(values) if values else 0
        })
        
        mock_dir = MockDirectory(name="src", path="src")
        mock_dir.add_file(MockFile("f1.py", "src/f1.py", {
            "ownership": MockKPI("ownership", 80)
        }))
        mock_dir.add_file(MockFile("f2.py", "src/f2.py", {
            "ownership": MockKPI("ownership", 60)
        }))
        
        result = aggregator.aggregate_directory(mock_dir)
        
        self.assertEqual(result["ownership"], 70)  # (80 + 60) / 2


class TestKPIAggregatorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aggregator = KPIAggregator()
    
    def test_aggregate_directory_with_mixed_kpis(self):
        """Test aggregating directory where files have different KPIs."""
        mock_dir = MockDirectory(name="src", path="src")
        
        # File 1 has complexity and churn
        file1 = MockFile("f1.py", "src/f1.py", {
            "complexity": MockKPI("complexity", 10),
            "churn": MockKPI("churn", 5)
        })
        
        # File 2 has only complexity
        file2 = MockFile("f2.py", "src/f2.py", {
            "complexity": MockKPI("complexity", 20)
        })
        
        mock_dir.add_file(file1)
        mock_dir.add_file(file2)
        
        result = self.aggregator.aggregate_directory(mock_dir)
        
        # Should aggregate all KPIs found
        self.assertIn("complexity", result)
        self.assertIn("churn", result)
        self.assertEqual(result["complexity"], 30)
        self.assertEqual(result["churn"], 5)
    
    def test_aggregate_deeply_nested_hierarchy(self):
        """Test aggregating deeply nested directory structure."""
        # Create: root/a/b/c/file.py
        root = MockDirectory(name="root", path="root")
        a = MockDirectory(name="a", path="root/a")
        b = MockDirectory(name="b", path="root/a/b")
        c = MockDirectory(name="c", path="root/a/b/c")
        
        root.add_child(a)
        a.add_child(b)
        b.add_child(c)
        
        file = MockFile("file.py", "root/a/b/c/file.py", {
            "complexity": MockKPI("complexity", 100)
        })
        c.add_file(file)
        
        result = self.aggregator.aggregate_directory(root)
        
        # Should propagate all the way up
        self.assertEqual(result["complexity"], 100)
    
    def test_aggregate_with_invalid_kpi_values(self):
        """Test aggregating with invalid KPI values."""
        mock_dir = MockDirectory(name="src", path="src")
        
        # Create file with KPI that has non-numeric value
        file1 = MockFile("f1.py", "src/f1.py", {
            "complexity": MockKPI("complexity", "invalid")
        })
        mock_dir.add_file(file1)
        
        # Should handle gracefully without crashing
        try:
            result = self.aggregator.aggregate_directory(mock_dir)
            # Either returns empty dict or handles the error
            self.assertIsNotNone(result)
        except (TypeError, ValueError):
            # Or raises appropriate error
            pass


class TestKPIAggregatorHierarchy(unittest.TestCase):
    """Test aggregation across entire hierarchy."""
    
    def test_aggregate_hierarchy_bottom_up(self):
        """Test that aggregation works bottom-up through hierarchy."""
        aggregator = KPIAggregator()
        
        # Create realistic structure
        root = MockDirectory(name="project", path="project")
        src = MockDirectory(name="src", path="project/src")
        tests = MockDirectory(name="tests", path="project/tests")
        
        root.add_child(src)
        root.add_child(tests)
        
        # Add files to src
        src.add_file(MockFile("main.py", "project/src/main.py", {
            "complexity": MockKPI("complexity", 50)
        }))
        src.add_file(MockFile("utils.py", "project/src/utils.py", {
            "complexity": MockKPI("complexity", 20)
        }))
        
        # Add files to tests
        tests.add_file(MockFile("test_main.py", "project/tests/test_main.py", {
            "complexity": MockKPI("complexity", 10)
        }))
        
        # Aggregate root (should aggregate all children)
        result = aggregator.aggregate_directory(root)
        
        self.assertEqual(result["complexity"], 80)  # 50 + 20 + 10
        
        # Verify intermediate directories also have aggregated values
        self.assertIn("complexity", src.kpis)
        self.assertEqual(src.kpis["complexity"].value, 70)  # 50 + 20
        self.assertIn("complexity", tests.kpis)
        self.assertEqual(tests.kpis["complexity"].value, 10)


if __name__ == "__main__":
    unittest.main()
