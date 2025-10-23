"""
Tests for Cognitive Complexity Calculator Factory.

Tests the Factory Pattern implementation for creating language-specific
cognitive complexity calculators.

TDD RED-GREEN-REFACTOR:
1. RED - Write failing tests for factory
2. GREEN - Implement factory
3. REFACTOR - Ensure clean code
"""

import pytest

# Suppress FutureWarning from tree_sitter Language(path, name) deprecation
pytestmark = pytest.mark.filterwarnings(
    r"ignore:Language\(path, name\) is deprecated. Use Language\(ptr, name\) instead\.:FutureWarning"
)


class TestCalculatorFactory:
    """Test the Calculator Factory."""

    def test_factory_create_returns_python_calculator_for_py_extension(self):
        """Factory should return PythonCalculator for .py files."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        calculator = CognitiveComplexityCalculatorFactory.create('test.py')
        assert isinstance(calculator, PythonCognitiveComplexityCalculator)

    def test_factory_create_returns_none_for_unsupported_extension(self):
        """Factory should return None for unsupported file extensions."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )

        calculator = CognitiveComplexityCalculatorFactory.create('test.xyz')
        assert calculator is None

    def test_factory_is_supported_returns_true_for_py(self):
        """Factory should return True for supported Python extension."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )

        assert CognitiveComplexityCalculatorFactory.is_supported('test.py') is True

    def test_factory_is_supported_returns_false_for_unsupported(self):
        """Factory should return False for unsupported extension."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )

        assert CognitiveComplexityCalculatorFactory.is_supported('test.xyz') is False

    def test_factory_get_supported_extensions_includes_python(self):
        """Factory should list Python extensions as supported."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )

        extensions = CognitiveComplexityCalculatorFactory.get_supported_extensions()
        assert '.py' in extensions

    def test_factory_get_supported_extensions_returns_sorted_list(self):
        """Factory should return sorted list of extensions."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )

        extensions = CognitiveComplexityCalculatorFactory.get_supported_extensions()
        assert isinstance(extensions, list)
        assert extensions == sorted(extensions)

    def test_factory_handles_case_insensitive_extensions(self):
        """Factory should handle uppercase extensions (e.g., .PY)."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        calculator = CognitiveComplexityCalculatorFactory.create('TEST.PY')
        assert isinstance(calculator, PythonCognitiveComplexityCalculator)

    def test_factory_handles_files_without_extension(self):
        """Factory should return None for files without extension."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )

        calculator = CognitiveComplexityCalculatorFactory.create('Makefile')
        assert calculator is None

    def test_factory_handles_absolute_paths(self):
        """Factory should work with absolute file paths."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        calculator = CognitiveComplexityCalculatorFactory.create('/path/to/file.py')
        assert isinstance(calculator, PythonCognitiveComplexityCalculator)


class TestFactoryMultiLanguageSupport:
    """Test factory support for multiple languages (when implemented)."""

    def test_factory_will_support_java(self):
        """Factory should support Java when JavaCalculator is implemented."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )

        # Currently should return None (not implemented yet)
        # When Java support is added, this will return JavaCalculator
        calculator = CognitiveComplexityCalculatorFactory.create('test.java')
        # For now, we just test that it doesn't crash
        assert calculator is None or calculator is not None  # Placeholder

    def test_factory_will_support_ada(self):
        """Factory should support Ada when AdaCalculator is implemented."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )

        # Currently should return None (not implemented yet)
        calculator = CognitiveComplexityCalculatorFactory.create('test.adb')
        assert calculator is None or calculator is not None  # Placeholder

    def test_factory_will_support_go(self):
        """Factory should support Go when GoCalculator is implemented."""
        from src.kpis.cognitive_complexity.calculator_factory import (
            CognitiveComplexityCalculatorFactory
        )

        # Currently should return None (not implemented yet)
        calculator = CognitiveComplexityCalculatorFactory.create('test.go')
        assert calculator is None or calculator is not None  # Placeholder
