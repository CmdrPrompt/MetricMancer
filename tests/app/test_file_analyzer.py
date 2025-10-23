"""
Tests for FileAnalyzer.

Tests the file-level analysis component that orchestrates
reading files, parsing functions, and calculating KPIs.
"""
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import os

from src.app import FileAnalyzer
from src.kpis.model import File, Function


class TestFileAnalyzerInitialization(unittest.TestCase):
    """Test FileAnalyzer initialization."""

    def test_initialization(self):
        """Should initialize with config and calculator."""
        mock_config = {'.py': {'parser': 'python'}}
        mock_calculator = Mock()

        analyzer = FileAnalyzer(mock_config, mock_calculator)

        self.assertEqual(analyzer.config, mock_config)
        self.assertEqual(analyzer.kpi_calculator, mock_calculator)


class TestFileAnalyzerSupportedExtensions(unittest.TestCase):
    """Test extension validation."""

    def setUp(self):
        self.config = {
            '.py': {'parser': 'python'},
            '.java': {'parser': 'java'},
            '.js': {'parser': 'javascript'}
        }
        self.mock_calculator = Mock()
        self.analyzer = FileAnalyzer(self.config, self.mock_calculator)

    def test_is_supported_extension_python(self):
        """Should recognize .py as supported."""
        self.assertTrue(self.analyzer._is_supported_extension('.py'))

    def test_is_supported_extension_java(self):
        """Should recognize .java as supported."""
        self.assertTrue(self.analyzer._is_supported_extension('.java'))

    def test_is_supported_extension_unsupported(self):
        """Should reject unsupported extensions."""
        self.assertFalse(self.analyzer._is_supported_extension('.txt'))
        self.assertFalse(self.analyzer._is_supported_extension('.md'))
        self.assertFalse(self.analyzer._is_supported_extension('.unknown'))


class TestFileAnalyzerReadFile(unittest.TestCase):
    """Test file reading functionality."""

    def setUp(self):
        self.config = {'.py': {'parser': 'python'}}
        self.mock_calculator = Mock()
        self.analyzer = FileAnalyzer(self.config, self.mock_calculator)

    def test_read_file_content_success(self):
        """Should read file content successfully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test():\n    pass")
            temp_path = f.name

        try:
            content = self.analyzer._read_file_content(Path(temp_path))
            self.assertEqual(content, "def test():\n    pass")
        finally:
            os.unlink(temp_path)

    def test_read_file_content_nonexistent(self):
        """Should return None for nonexistent file."""
        nonexistent = Path('/nonexistent/file.py')
        content = self.analyzer._read_file_content(nonexistent)
        self.assertIsNone(content)

    @patch('pathlib.Path.open')
    def test_read_file_content_permission_error(self, mock_open_method):
        """Should return None on permission error."""
        mock_open_method.side_effect = PermissionError("Access denied")

        content = self.analyzer._read_file_content(Path('/some/file.py'))
        self.assertIsNone(content)


class TestFileAnalyzerCreateFunctions(unittest.TestCase):
    """Test function object creation."""

    def setUp(self):
        self.config = {'.py': {'parser': 'python'}}
        self.mock_calculator = Mock()
        self.analyzer = FileAnalyzer(self.config, self.mock_calculator)

    def test_create_function_objects_single_function(self):
        """Should create function objects with complexity."""
        functions_data = [
            {'name': 'test_function', 'complexity': 5}
        ]

        result = self.analyzer._create_function_objects(functions_data)

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Function)
        self.assertEqual(result[0].name, 'test_function')
        self.assertIn('complexity', result[0].kpis)
        self.assertEqual(result[0].kpis['complexity'].value, 5)

    def test_create_function_objects_multiple_functions(self):
        """Should create multiple function objects."""
        functions_data = [
            {'name': 'func1', 'complexity': 3},
            {'name': 'func2', 'complexity': 7},
            {'name': 'func3', 'complexity': 2}
        ]

        result = self.analyzer._create_function_objects(functions_data)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].name, 'func1')
        self.assertEqual(result[1].name, 'func2')
        self.assertEqual(result[2].name, 'func3')
        self.assertEqual(result[0].kpis['complexity'].value, 3)
        self.assertEqual(result[1].kpis['complexity'].value, 7)
        self.assertEqual(result[2].kpis['complexity'].value, 2)

    def test_create_function_objects_missing_complexity(self):
        """Should handle missing complexity field."""
        functions_data = [
            {'name': 'func1'},  # No complexity
            {'name': 'func2', 'complexity': 5}
        ]

        result = self.analyzer._create_function_objects(functions_data)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].kpis['complexity'].value, 0)  # Default
        self.assertEqual(result[1].kpis['complexity'].value, 5)

    def test_create_function_objects_missing_name(self):
        """Should use 'N/A' for missing function name."""
        functions_data = [
            {'complexity': 5}  # No name
        ]

        result = self.analyzer._create_function_objects(functions_data)

        self.assertEqual(result[0].name, 'N/A')

    def test_create_function_objects_empty_list(self):
        """Should handle empty functions list."""
        result = self.analyzer._create_function_objects([])
        self.assertEqual(result, [])


class TestFileAnalyzerAnalyzeFile(unittest.TestCase):
    """Test full file analysis workflow."""

    def setUp(self):
        self.config = {'.py': {'parser': 'python'}}
        self.mock_calculator = Mock()

        # Mock complexity analyzer
        self.mock_complexity_analyzer = Mock()
        self.mock_calculator.complexity_analyzer = self.mock_complexity_analyzer

        self.analyzer = FileAnalyzer(self.config, self.mock_calculator)

    def test_analyze_file_unsupported_extension(self):
        """Should return None for unsupported extension."""
        file_info = {'path': '/repo/test.txt', 'ext': '.txt'}
        repo_root = Path('/repo')

        result = self.analyzer.analyze_file(file_info, repo_root)

        self.assertIsNone(result)

    @patch('src.app.kpi.file_analyzer.FileAnalyzer._read_file_content')
    def test_analyze_file_read_error(self, mock_read):
        """Should return None if file cannot be read."""
        mock_read.return_value = None

        file_info = {'path': '/repo/test.py', 'ext': '.py'}
        repo_root = Path('/repo')

        result = self.analyzer.analyze_file(file_info, repo_root)

        self.assertIsNone(result)

    @patch('src.app.kpi.file_analyzer.FileAnalyzer._read_file_content')
    def test_analyze_file_success(self, mock_read):
        """Should analyze file successfully and return File object."""
        # Setup mocks
        mock_read.return_value = "def test(): pass"

        functions_data = [{'name': 'test', 'complexity': 1}]
        self.mock_complexity_analyzer.analyze_functions.return_value = functions_data

        # Mock KPIs
        mock_kpis = {
            'complexity': Mock(name='complexity'),
            'churn': Mock(name='churn'),
            'hotspot': Mock(name='hotspot'),
            'Code Ownership': Mock(name='Code Ownership'),
            'Shared Ownership': Mock(name='Shared Ownership')
        }
        self.mock_calculator.calculate_all.return_value = mock_kpis

        file_info = {'path': '/repo/src/test.py', 'ext': '.py'}
        repo_root = Path('/repo')

        result = self.analyzer.analyze_file(file_info, repo_root)

        # Verify result
        self.assertIsInstance(result, File)
        self.assertEqual(result.name, 'test.py')
        self.assertEqual(result.file_path, 'src/test.py')
        self.assertEqual(len(result.functions), 1)
        self.assertEqual(result.functions[0].name, 'test')
        self.assertEqual(result.kpis, mock_kpis)

        # Verify complexity analyzer was called
        self.mock_complexity_analyzer.analyze_functions.assert_called_once()

        # Verify KPI calculator was called
        self.mock_calculator.calculate_all.assert_called_once()
        call_kwargs = self.mock_calculator.calculate_all.call_args[1]
        self.assertEqual(call_kwargs['file_info'], file_info)
        self.assertEqual(call_kwargs['repo_root'], repo_root)
        self.assertEqual(call_kwargs['content'], "def test(): pass")
        self.assertEqual(call_kwargs['functions_data'], functions_data)


class TestFileAnalyzerMultipleFiles(unittest.TestCase):
    """Test batch file analysis."""

    def setUp(self):
        self.config = {'.py': {'parser': 'python'}}
        self.mock_calculator = Mock()
        self.mock_complexity_analyzer = Mock()
        self.mock_calculator.complexity_analyzer = self.mock_complexity_analyzer
        self.analyzer = FileAnalyzer(self.config, self.mock_calculator)

    @patch('src.app.kpi.file_analyzer.FileAnalyzer.analyze_file')
    def test_analyze_multiple_files_all_succeed(self, mock_analyze):
        """Should analyze all files successfully."""
        # Mock successful analysis
        mock_file1 = Mock(spec=File)
        mock_file2 = Mock(spec=File)
        mock_analyze.side_effect = [mock_file1, mock_file2]

        files_info = [
            {'path': '/repo/a.py', 'ext': '.py'},
            {'path': '/repo/b.py', 'ext': '.py'}
        ]
        repo_root = Path('/repo')

        result = self.analyzer.analyze_multiple_files(files_info, repo_root)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], mock_file1)
        self.assertEqual(result[1], mock_file2)
        self.assertEqual(mock_analyze.call_count, 2)

    @patch('src.app.kpi.file_analyzer.FileAnalyzer.analyze_file')
    def test_analyze_multiple_files_some_fail(self, mock_analyze):
        """Should filter out failed files (None results)."""
        # Mock mixed results
        mock_file1 = Mock(spec=File)
        mock_analyze.side_effect = [mock_file1, None, None]

        files_info = [
            {'path': '/repo/a.py', 'ext': '.py'},
            {'path': '/repo/b.txt', 'ext': '.txt'},  # Unsupported
            {'path': '/repo/c.py', 'ext': '.py'}     # Read error
        ]
        repo_root = Path('/repo')

        result = self.analyzer.analyze_multiple_files(files_info, repo_root)

        # Should only include successful analysis
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_file1)

    @patch('src.app.kpi.file_analyzer.FileAnalyzer.analyze_file')
    def test_analyze_multiple_files_empty_list(self, mock_analyze):
        """Should handle empty file list."""
        result = self.analyzer.analyze_multiple_files([], Path('/repo'))

        self.assertEqual(result, [])
        mock_analyze.assert_not_called()


class TestFileAnalyzerStatistics(unittest.TestCase):
    """Test statistics reporting."""

    def setUp(self):
        self.config = {'.py': {'parser': 'python'}}
        self.mock_calculator = Mock()
        self.analyzer = FileAnalyzer(self.config, self.mock_calculator)

    def test_get_statistics(self):
        """Should return timing statistics from KPICalculator."""
        mock_timing = {
            'complexity': 0.123,
            'churn': 0.456,
            'hotspot': 0.001,
            'ownership': 0.789,
            'shared_ownership': 0.012
        }
        self.mock_calculator.get_timing_report.return_value = mock_timing

        result = self.analyzer.get_statistics()

        self.assertEqual(result['kpi_timing'], mock_timing)
        self.assertAlmostEqual(result['total_kpi_time'], 1.381, places=3)


class TestFileAnalyzerIntegration(unittest.TestCase):
    """Integration tests with real components."""

    def setUp(self):
        from src.kpis.complexity import ComplexityAnalyzer
        from src.app import KPICalculator
        from src.languages.config import Config

        # Use real language configuration
        lang_config = Config()
        self.config = lang_config.languages

        complexity_analyzer = ComplexityAnalyzer()
        kpi_calculator = KPICalculator(complexity_analyzer)
        self.analyzer = FileAnalyzer(self.config, kpi_calculator)

    @patch('src.utilities.git_cache.get_git_cache')
    def test_analyze_real_python_file(self, mock_git_cache):
        """Should analyze a real Python file end-to-end."""
        # Mock git cache
        mock_cache = Mock()
        mock_cache.get_churn_data.return_value = 5
        mock_git_cache.return_value = mock_cache

        # Create temporary Python file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            dir=tempfile.gettempdir()
        ) as f:
            f.write("""
def simple_function():
    return 42

def complex_function(x):
    if x > 0:
        return x * 2
    else:
        return x * -1
""")
            temp_path = f.name

        try:
            repo_root = Path(tempfile.gettempdir())
            file_info = {
                'path': temp_path,
                'ext': '.py'
            }

            result = self.analyzer.analyze_file(file_info, repo_root)

            # Verify File object
            self.assertIsInstance(result, File)
            self.assertTrue(result.name.endswith('.py'))

            # Verify functions parsed
            self.assertEqual(len(result.functions), 2)
            function_names = [f.name for f in result.functions]
            self.assertIn('simple_function', function_names)
            self.assertIn('complex_function', function_names)

            # Verify KPIs present
            self.assertIn('complexity', result.kpis)
            self.assertIn('churn', result.kpis)
            self.assertIn('hotspot', result.kpis)
            self.assertIn('Code Ownership', result.kpis)
            self.assertIn('Shared Ownership', result.kpis)

            # Verify complexity calculated
            complexity_value = result.kpis['complexity'].value
            self.assertGreater(complexity_value, 0)

        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
