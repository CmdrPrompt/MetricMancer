"""
Tests for FileProcessor class.

FileProcessor is responsible for processing individual files by:
1. Reading file content using FileReader
2. Analyzing complexity using ComplexityAnalyzer
3. Calculating KPIs using KPIOrchestrator
4. Combining results into a FileMetrics object

This follows the TDD RED-GREEN-REFACTOR cycle.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Import will fail initially (RED phase)
from app.processing.file_processor import FileProcessor
from app.file_reader import FileReader
from app.processing.kpi_orchestrator import KPIOrchestrator


class MockKPI:
    """Mock KPI class for testing."""
    def __init__(self, name="MockKPI", value=42):
        self.name = name
        self.value = value


class TestFileProcessorInitialization(unittest.TestCase):
    """Test FileProcessor initialization and dependency injection."""
    
    def test_init_with_default_dependencies(self):
        """Test initialization with default dependencies."""
        processor = FileProcessor()
        
        self.assertIsNotNone(processor.file_reader)
        self.assertIsNotNone(processor.kpi_orchestrator)
        # complexity_analyzer is None by default (needs lang_config for real use)
        self.assertIsInstance(processor.file_reader, FileReader)
        self.assertIsInstance(processor.kpi_orchestrator, KPIOrchestrator)
    
    def test_init_with_custom_dependencies(self):
        """Test initialization with custom dependencies (Dependency Injection)."""
        mock_reader = Mock(spec=FileReader)
        mock_orchestrator = Mock(spec=KPIOrchestrator)
        mock_analyzer = Mock()  # Generic mock, no spec needed
        
        processor = FileProcessor(
            file_reader=mock_reader,
            kpi_orchestrator=mock_orchestrator,
            complexity_analyzer=mock_analyzer
        )
        
        self.assertIs(processor.file_reader, mock_reader)
        self.assertIs(processor.kpi_orchestrator, mock_orchestrator)
        self.assertIs(processor.complexity_analyzer, mock_analyzer)


class TestFileProcessorProcessFile(unittest.TestCase):
    """Test the main process_file method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_reader = Mock(spec=FileReader)
        self.mock_orchestrator = Mock(spec=KPIOrchestrator)
        self.mock_analyzer = Mock()  # Generic mock
        
        self.processor = FileProcessor(
            file_reader=self.mock_reader,
            kpi_orchestrator=self.mock_orchestrator,
            complexity_analyzer=self.mock_analyzer
        )
    
    def test_process_file_success(self):
        """Test successful file processing with all steps working."""
        file_path = Path("/test/file.py")
        repo_root = Path("/test")
        
        # Mock file reading
        file_content = "def hello():\n    print('world')\n"
        self.mock_reader.read_file.return_value = file_content
        
        # Mock complexity analysis
        complexity_result = Mock()
        complexity_result.complexity = 5
        complexity_result.function_count = 1
        self.mock_analyzer.analyze_file.return_value = complexity_result
        
        # Mock KPI calculation
        mock_kpi1 = MockKPI(name="churn", value=3)
        mock_kpi2 = MockKPI(name="hotspot", value=7)
        self.mock_orchestrator.calculate_file_kpis.return_value = {
            "churn": mock_kpi1,
            "hotspot": mock_kpi2
        }
        
        # Process file
        result = self.processor.process_file(file_path, repo_root)
        
        # Verify result structure
        self.assertIsNotNone(result)
        self.assertEqual(result["file_path"], file_path)
        self.assertEqual(result["repo_root"], repo_root)
        self.assertEqual(result["complexity"], 5)
        self.assertEqual(result["function_count"], 1)
        self.assertIn("churn", result["kpis"])
        self.assertIn("hotspot", result["kpis"])
        
        # Verify dependencies were called correctly
        self.mock_reader.read_file.assert_called_once_with(file_path)
        self.mock_analyzer.analyze_file.assert_called_once()
        self.mock_orchestrator.calculate_file_kpis.assert_called_once()
    
    def test_process_file_read_error(self):
        """Test file processing when file reading fails."""
        file_path = Path("/test/file.py")
        repo_root = Path("/test")
        
        # Mock file reading failure
        self.mock_reader.read_file.return_value = None
        
        # Process file
        result = self.processor.process_file(file_path, repo_root)
        
        # Should return None or error result
        self.assertIsNone(result)
        
        # Should not call other dependencies
        self.mock_analyzer.analyze_file.assert_not_called()
        self.mock_orchestrator.calculate_file_kpis.assert_not_called()
    
    def test_process_file_complexity_error(self):
        """Test file processing when complexity analysis fails."""
        file_path = Path("/test/file.py")
        repo_root = Path("/test")
        
        # Mock successful file reading
        self.mock_reader.read_file.return_value = "print('hello')"
        
        # Mock complexity analysis failure
        self.mock_analyzer.analyze_file.side_effect = Exception("Analysis error")
        
        # Process file
        result = self.processor.process_file(file_path, repo_root)
        
        # Should handle error gracefully
        self.assertIsNone(result)
    
    def test_process_file_kpi_error(self):
        """Test file processing when KPI calculation fails."""
        file_path = Path("/test/file.py")
        repo_root = Path("/test")
        
        # Mock successful file reading
        self.mock_reader.read_file.return_value = "print('hello')"
        
        # Mock successful complexity analysis
        complexity_result = Mock()
        complexity_result.complexity = 5
        complexity_result.function_count = 1
        self.mock_analyzer.analyze_file.return_value = complexity_result
        
        # Mock KPI calculation failure
        self.mock_orchestrator.calculate_file_kpis.side_effect = Exception("KPI error")
        
        # Process file - should still return result with complexity but no KPIs
        result = self.processor.process_file(file_path, repo_root)
        
        # Should have basic info but empty KPIs
        self.assertIsNotNone(result)
        self.assertEqual(result["complexity"], 5)
        self.assertEqual(result["kpis"], {})


class TestFileProcessorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_reader = Mock(spec=FileReader)
        self.mock_orchestrator = Mock(spec=KPIOrchestrator)
        self.mock_analyzer = Mock()  # Generic mock
        
        self.processor = FileProcessor(
            file_reader=self.mock_reader,
            kpi_orchestrator=self.mock_orchestrator,
            complexity_analyzer=self.mock_analyzer
        )
    
    def test_process_file_with_empty_content(self):
        """Test processing file with empty content."""
        file_path = Path("/test/empty.py")
        repo_root = Path("/test")
        
        # Mock empty file
        self.mock_reader.read_file.return_value = ""
        
        # Mock zero complexity
        complexity_result = Mock()
        complexity_result.complexity = 0
        complexity_result.function_count = 0
        self.mock_analyzer.analyze_file.return_value = complexity_result
        
        self.mock_orchestrator.calculate_file_kpis.return_value = {}
        
        # Process file
        result = self.processor.process_file(file_path, repo_root)
        
        # Should handle empty file gracefully
        self.assertIsNotNone(result)
        self.assertEqual(result["complexity"], 0)
        self.assertEqual(result["function_count"], 0)
    
    def test_process_file_with_relative_path(self):
        """Test processing with relative paths."""
        file_path = Path("src/file.py")
        repo_root = Path(".")
        
        self.mock_reader.read_file.return_value = "print('test')"
        
        complexity_result = Mock()
        complexity_result.complexity = 1
        complexity_result.function_count = 0
        self.mock_analyzer.analyze_file.return_value = complexity_result
        
        self.mock_orchestrator.calculate_file_kpis.return_value = {}
        
        # Should handle relative paths
        result = self.processor.process_file(file_path, repo_root)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["file_path"], file_path)
        self.assertEqual(result["repo_root"], repo_root)
    
    def test_process_file_builds_correct_context(self):
        """Test that process_file builds correct context for KPI calculation."""
        file_path = Path("/test/file.py")
        repo_root = Path("/test")
        
        self.mock_reader.read_file.return_value = "def test(): pass"
        
        complexity_result = Mock()
        complexity_result.complexity = 2
        complexity_result.function_count = 1
        self.mock_analyzer.analyze_file.return_value = complexity_result
        
        self.mock_orchestrator.calculate_file_kpis.return_value = {}
        
        # Process file
        self.processor.process_file(file_path, repo_root)
        
        # Verify context passed to orchestrator
        call_args = self.mock_orchestrator.calculate_file_kpis.call_args
        context = call_args[0][0]  # First positional argument
        
        self.assertIn("file_path", context)
        self.assertIn("repo_root", context)
        self.assertIn("content", context)
        self.assertIn("complexity", context)
        self.assertEqual(context["file_path"], file_path)
        self.assertEqual(context["repo_root"], repo_root)
        self.assertEqual(context["complexity"], 2)


class TestFileProcessorIntegration(unittest.TestCase):
    """Integration tests with real dependencies."""
    
    def test_process_file_with_real_dependencies(self):
        """Test processing with real FileReader and ComplexityAnalyzer."""
        # Use real dependencies
        processor = FileProcessor()
        
        # Create a temporary test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def simple_function():\n    return 42\n")
            temp_file = Path(f.name)
        
        try:
            # Process file
            result = processor.process_file(temp_file, temp_file.parent)
            
            # Verify result
            self.assertIsNotNone(result)
            self.assertEqual(result["file_path"], temp_file)
            self.assertGreaterEqual(result["complexity"], 0)
            
        finally:
            # Cleanup
            temp_file.unlink()


if __name__ == "__main__":
    unittest.main()
