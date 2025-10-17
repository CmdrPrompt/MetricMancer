"""
Test suite for FileProcessor (Phase 5) - TDD RED-GREEN-REFACTOR approach.

RED PHASE: Writing tests FIRST before implementation.

FileProcessor extracts file processing logic from analyzer.py:
- File content reading
- Function complexity analysis
- KPI calculations (complexity, churn, ownership)
- File object creation

This test suite covers:
- Initialization
- File content reading with error handling
- Function complexity analysis
- Churn KPI calculation
- Ownership KPI calculations
- Complete file processing pipeline
- Error handling and edge cases

Test Coverage Goals:
- 100% statement coverage
- All file processing paths tested
- Integration with existing KPI classes verified
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
from src.app.file_processor import FileProcessor
from src.kpis.complexity import ComplexityKPI, ComplexityAnalyzer
from src.kpis.codechurn import ChurnKPI
from src.kpis.codeownership import CodeOwnershipKPI
from src.kpis.hotspot import HotspotKPI
from src.kpis.model import File, Function


class TestFileProcessorInit:
    """Test FileProcessor initialization."""

    def test_init_with_required_dependencies(self):
        """Should initialize with complexity analyzer and language config."""
        complexity_analyzer = Mock(spec=ComplexityAnalyzer)
        lang_config = {'python': {'extensions': ['.py']}}

        processor = FileProcessor(complexity_analyzer, lang_config)

        assert processor.complexity_analyzer is complexity_analyzer
        assert processor.lang_config == lang_config

    def test_init_stores_dependencies(self):
        """Should store dependencies for later use."""
        analyzer = Mock()
        config = {'test': 'config'}

        processor = FileProcessor(analyzer, config)

        # Should be accessible
        assert hasattr(processor, 'complexity_analyzer')
        assert hasattr(processor, 'lang_config')


class TestReadFileContent:
    """Test file content reading."""

    def test_read_valid_file(self):
        """Should read file content successfully."""
        processor = FileProcessor(Mock(), {})
        test_content = "def hello():\n    print('world')"

        with patch('pathlib.Path.open', mock_open(read_data=test_content)):
            content = processor.read_file_content(Path('test.py'))

        assert content == test_content

    def test_read_file_with_utf8_encoding(self):
        """Should read file with UTF-8 encoding."""
        processor = FileProcessor(Mock(), {})

        with patch('pathlib.Path.open', mock_open(read_data='test')) as m:
            processor.read_file_content(Path('test.py'))

            # Verify UTF-8 encoding was used
            m.assert_called_once()
            args, kwargs = m.call_args
            assert kwargs.get('encoding') == 'utf-8'

    def test_read_file_ignores_encoding_errors(self):
        """Should ignore encoding errors."""
        processor = FileProcessor(Mock(), {})

        with patch('pathlib.Path.open', mock_open(read_data='test')) as m:
            processor.read_file_content(Path('test.py'))

            args, kwargs = m.call_args
            assert kwargs.get('errors') == 'ignore'

    def test_read_nonexistent_file_returns_none(self):
        """Should return None when file doesn't exist."""
        processor = FileProcessor(Mock(), {})

        with patch('pathlib.Path.open', side_effect=FileNotFoundError()):
            content = processor.read_file_content(Path('nonexistent.py'))

        assert content is None

    def test_read_file_with_permission_error_returns_none(self):
        """Should return None on permission error."""
        processor = FileProcessor(Mock(), {})

        with patch('pathlib.Path.open', side_effect=PermissionError()):
            content = processor.read_file_content(Path('protected.py'))

        assert content is None

    def test_read_file_with_unicode_error_returns_none(self):
        """Should return None on unicode decode error."""
        processor = FileProcessor(Mock(), {})

        with patch('pathlib.Path.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'test')):
            content = processor.read_file_content(Path('bad_encoding.py'))

        assert content is None


class TestAnalyzeFunctionsComplexity:
    """Test function complexity analysis."""

    def test_analyze_functions_with_valid_content(self):
        """Should analyze functions and return complexity data."""
        analyzer = Mock(spec=ComplexityAnalyzer)
        analyzer.analyze_functions.return_value = [
            {'name': 'func1', 'complexity': 5},
            {'name': 'func2', 'complexity': 10}
        ]

        processor = FileProcessor(analyzer, {})
        lang_config = {'python': {}}

        functions, total_complexity, elapsed = processor.analyze_functions_complexity(
            "def func1(): pass\ndef func2(): pass",
            lang_config
        )

        assert len(functions) == 2
        assert total_complexity == 15  # 5 + 10
        assert elapsed >= 0

    def test_analyze_functions_creates_function_objects(self):
        """Should create Function objects with complexity KPIs."""
        analyzer = Mock()
        analyzer.analyze_functions.return_value = [
            {'name': 'test_func', 'complexity': 7}
        ]

        processor = FileProcessor(analyzer, {})
        functions, _, _ = processor.analyze_functions_complexity("code", {})

        assert isinstance(functions[0], Function)
        assert functions[0].name == 'test_func'
        assert 'complexity' in functions[0].kpis

    def test_analyze_functions_with_no_functions(self):
        """Should handle files with no functions."""
        analyzer = Mock()
        analyzer.analyze_functions.return_value = []

        processor = FileProcessor(analyzer, {})
        functions, total_complexity, elapsed = processor.analyze_functions_complexity("# just comments", {})

        assert functions == []
        assert total_complexity == 0
        assert elapsed >= 0

    def test_analyze_functions_handles_missing_complexity(self):
        """Should handle functions without complexity field."""
        analyzer = Mock()
        analyzer.analyze_functions.return_value = [
            {'name': 'func1'},  # No complexity
            {'name': 'func2', 'complexity': 5}
        ]

        processor = FileProcessor(analyzer, {})
        functions, total_complexity, _ = processor.analyze_functions_complexity("code", {})

        # Should default to 0 for missing complexity
        assert len(functions) == 2
        assert total_complexity == 5

    def test_analyze_functions_measures_elapsed_time(self):
        """Should measure and return elapsed time."""
        analyzer = Mock()
        analyzer.analyze_functions.return_value = []

        processor = FileProcessor(analyzer, {})
        _, _, elapsed = processor.analyze_functions_complexity("code", {})

        assert isinstance(elapsed, float)
        assert elapsed >= 0


class TestCalculateChurnKPI:
    """Test churn KPI calculation."""

    @patch('src.app.core.file_processor.ChurnKPI')
    def test_calculate_churn_for_file(self, mock_churn_class):
        """Should calculate churn KPI for file."""
        mock_churn_kpi = Mock()
        mock_churn_kpi.value = 10
        mock_churn_class.return_value.calculate.return_value = mock_churn_kpi

        processor = FileProcessor(Mock(), {})
        file_path = Path('/repo/src/test.py')
        repo_root = Path('/repo')

        churn_kpi, elapsed = processor.calculate_churn_kpi(file_path, repo_root)

        assert churn_kpi == mock_churn_kpi
        assert elapsed >= 0

    @patch('src.app.core.file_processor.ChurnKPI')
    def test_calculate_churn_uses_relative_path(self, mock_churn_class):
        """Should use relative path for churn calculation."""
        mock_churn_class.return_value.calculate.return_value = Mock(value=5)

        processor = FileProcessor(Mock(), {})
        file_path = Path('/repo/src/module/file.py')
        repo_root = Path('/repo')

        processor.calculate_churn_kpi(file_path, repo_root)

        # Should be called with string paths
        mock_churn_class.return_value.calculate.assert_called_once()
        args, kwargs = mock_churn_class.return_value.calculate.call_args
        assert 'file_path' in kwargs
        assert 'repo_root' in kwargs

    @patch('src.app.core.file_processor.ChurnKPI')
    def test_calculate_churn_measures_elapsed_time(self, mock_churn_class):
        """Should measure elapsed time for churn calculation."""
        mock_churn_class.return_value.calculate.return_value = Mock(value=3)

        processor = FileProcessor(Mock(), {})
        _, elapsed = processor.calculate_churn_kpi(Path('/repo/file.py'), Path('/repo'))

        assert isinstance(elapsed, float)
        assert elapsed >= 0


class TestCalculateOwnershipKPIs:
    """Test ownership KPI calculations."""

    @patch('src.app.core.file_processor.SharedOwnershipKPI')
    @patch('src.app.core.file_processor.CodeOwnershipKPI')
    def test_calculate_both_ownership_kpis(self, mock_code_ownership, mock_shared_ownership):
        """Should calculate both code ownership and shared ownership KPIs."""
        mock_code_kpi = Mock()
        mock_shared_kpi = Mock()
        mock_code_ownership.return_value = mock_code_kpi
        mock_shared_ownership.return_value = mock_shared_kpi

        processor = FileProcessor(Mock(), {})
        file_path = Path('/repo/test.py')
        repo_root = Path('/repo')

        code_kpi, shared_kpi, code_time, shared_time = processor.calculate_ownership_kpis(
            file_path, repo_root
        )

        assert code_kpi == mock_code_kpi
        assert shared_kpi == mock_shared_kpi
        assert code_time >= 0
        assert shared_time >= 0

    @patch('src.app.core.file_processor.SharedOwnershipKPI')
    @patch('src.app.core.file_processor.CodeOwnershipKPI')
    def test_calculate_ownership_uses_resolved_paths(self, mock_code, mock_shared):
        """Should use resolved absolute paths."""
        processor = FileProcessor(Mock(), {})

        processor.calculate_ownership_kpis(Path('test.py'), Path('.'))

        # Both should be called
        assert mock_code.called
        assert mock_shared.called

    @patch('src.app.core.file_processor.SharedOwnershipKPI', side_effect=Exception('Git error'))
    @patch('src.app.core.file_processor.CodeOwnershipKPI', side_effect=Exception('Git error'))
    def test_calculate_ownership_handles_exceptions(self, mock_code, mock_shared):
        """Should use fallback KPIs on exceptions."""
        processor = FileProcessor(Mock(), {})

        with patch('src.app.core.file_processor.FallbackCodeOwnershipKPI') as fallback_code:
            with patch('src.app.core.file_processor.FallbackSharedOwnershipKPI') as fallback_shared:
                fallback_code.return_value = Mock()
                fallback_shared.return_value = Mock()

                code_kpi, shared_kpi, _, _ = processor.calculate_ownership_kpis(
                    Path('test.py'), Path('.')
                )

                # Should use fallbacks
                assert fallback_code.called
                assert fallback_shared.called

    @patch('src.app.core.file_processor.SharedOwnershipKPI')
    @patch('src.app.core.file_processor.CodeOwnershipKPI')
    def test_calculate_ownership_measures_separate_times(self, mock_code, mock_shared):
        """Should measure elapsed time separately for each KPI."""
        mock_code.return_value = Mock()
        mock_shared.return_value = Mock()

        processor = FileProcessor(Mock(), {})
        _, _, code_time, shared_time = processor.calculate_ownership_kpis(
            Path('test.py'), Path('.')
        )

        # Both should have timing
        assert isinstance(code_time, float)
        assert isinstance(shared_time, float)
        assert code_time >= 0
        assert shared_time >= 0


class TestProcessFile:
    """Test complete file processing pipeline."""

    def test_process_file_returns_file_object(self):
        """Should return File object with all KPIs."""
        analyzer = Mock()
        analyzer.analyze_functions.return_value = []

        lang_config = {'.py': {'parser': 'python'}}
        processor = FileProcessor(analyzer, lang_config)

        with patch.object(processor, 'read_file_content', return_value="code"):
            with patch.object(processor, 'analyze_functions_complexity', return_value=([], 10, 0.1)):
                with patch.object(processor, 'calculate_churn_kpi', return_value=(Mock(value=5), 0.1)):
                    with patch.object(processor, 'calculate_ownership_kpis',
                                      return_value=(Mock(), Mock(), 0.1, 0.1)):
                        file_info = {'path': Path('test.py'), 'ext': '.py'}

                        result, timing = processor.process_file(file_info, Path('/repo'))

        assert isinstance(result, File)
        assert result.name == 'test.py'

    def test_process_file_returns_none_when_no_content(self):
        """Should return None when file content cannot be read."""
        processor = FileProcessor(Mock(), {})

        with patch.object(processor, 'read_file_content', return_value=None):
            file_info = {'path': Path('missing.py'), 'ext': '.py'}

            result, timing = processor.process_file(file_info, Path('/repo'))

        assert result is None

    def test_process_file_calculates_all_kpis(self):
        """Should calculate all KPIs: complexity, churn, hotspot, ownership."""
        analyzer = Mock()
        analyzer.analyze_functions.return_value = [{'name': 'func', 'complexity': 5}]

        lang_config = {'.py': {'parser': 'python'}}
        processor = FileProcessor(analyzer, lang_config)

        with patch.object(processor, 'read_file_content', return_value="code"):
            with patch.object(processor, 'analyze_functions_complexity',
                              return_value=([Mock()], 10, 0.1)):
                with patch.object(processor, 'calculate_churn_kpi',
                                  return_value=(Mock(value=5), 0.1)):
                    with patch.object(processor, 'calculate_ownership_kpis',
                                      return_value=(Mock(), Mock(), 0.1, 0.1)):
                        file_info = {'path': Path('test.py'), 'ext': '.py'}

                        result, timing = processor.process_file(file_info, Path('/repo'))

        # Should have KPIs
        assert result is not None
        assert hasattr(result, 'kpis')

    def test_process_file_tracks_timing(self):
        """Should track timing for each operation."""
        analyzer = Mock()
        analyzer.analyze_functions.return_value = []

        lang_config = {'.py': {'parser': 'python'}}
        processor = FileProcessor(analyzer, lang_config)

        with patch.object(processor, 'read_file_content', return_value="code"):
            with patch.object(processor, 'analyze_functions_complexity',
                              return_value=([], 5, 0.05)) as mock_complexity:
                with patch.object(processor, 'calculate_churn_kpi',
                                  return_value=(Mock(value=3), 0.03)) as mock_churn:
                    with patch.object(processor, 'calculate_ownership_kpis',
                                      return_value=(Mock(), Mock(), 0.02, 0.04)) as mock_ownership:
                        file_info = {'path': Path('test.py'), 'ext': '.py'}

                        result = processor.process_file(file_info, Path('/repo'))

        # All timing methods should be called
        assert mock_complexity.called
        assert mock_churn.called
        assert mock_ownership.called

    def test_process_file_returns_timing_dict(self):
        """Should return timing information for each operation."""
        analyzer = Mock()
        analyzer.analyze_functions.return_value = []

        processor = FileProcessor(analyzer, {})

        with patch.object(processor, 'read_file_content', return_value="code"):
            with patch.object(processor, 'analyze_functions_complexity',
                              return_value=([], 5, 0.1)):
                with patch.object(processor, 'calculate_churn_kpi',
                                  return_value=(Mock(value=3), 0.2)):
                    with patch.object(processor, 'calculate_ownership_kpis',
                                      return_value=(Mock(), Mock(), 0.3, 0.4)):
                        file_info = {'path': Path('test.py'), 'ext': '.py'}

                        file_obj, timing = processor.process_file(file_info, Path('/repo'))

        # Should return timing dict
        assert isinstance(timing, dict)
        assert 'complexity' in timing
        assert 'filechurn' in timing
        assert 'ownership' in timing
        assert 'sharedownership' in timing


class TestFileProcessorIntegration:
    """Integration tests with real components."""

    def test_process_file_with_real_complexity_analyzer(self):
        """Should work with real ComplexityAnalyzer."""
        analyzer = ComplexityAnalyzer()
        lang_config = {'.py': {'parser': 'python', 'extensions': ['.py']}}
        processor = FileProcessor(analyzer, lang_config)

        code = "def simple_function():\n    return 42"

        with patch.object(processor, 'read_file_content', return_value=code):
            with patch.object(processor, 'calculate_churn_kpi',
                              return_value=(ChurnKPI(value=0), 0.0)):
                with patch.object(processor, 'calculate_ownership_kpis',
                                  return_value=(Mock(), Mock(), 0.0, 0.0)):
                    file_info = {'path': Path('test.py'), 'ext': '.py'}

                    result, timing = processor.process_file(file_info, Path('/repo'))

        assert result is not None
        assert isinstance(result, File)
        assert 'complexity' in timing
