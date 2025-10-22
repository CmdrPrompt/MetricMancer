"""
Tests for Cognitive Complexity Calculator Base Class.

Tests the abstract base class interface and the refactored Python calculator
that extends it.

TDD RED-GREEN-REFACTOR:
1. RED - Write failing tests for base class interface
2. GREEN - Refactor Python calculator to extend base class
3. REFACTOR - Ensure all existing tests still pass
"""

import pytest
from abc import ABC


class TestCognitiveComplexityCalculatorBase:
    """Test the abstract base class interface."""

    def test_base_class_is_abstract(self):
        """Base class should be abstract and not instantiable."""
        from src.kpis.cognitive_complexity.calculator_base import (
            CognitiveComplexityCalculatorBase
        )

        # Should not be able to instantiate abstract base class
        with pytest.raises(TypeError):
            CognitiveComplexityCalculatorBase()

    def test_base_class_defines_calculate_for_file(self):
        """Base class should define calculate_for_file abstract method."""
        from src.kpis.cognitive_complexity.calculator_base import (
            CognitiveComplexityCalculatorBase
        )

        # Check that method exists
        assert hasattr(CognitiveComplexityCalculatorBase, 'calculate_for_file')
        assert callable(getattr(CognitiveComplexityCalculatorBase, 'calculate_for_file'))

    def test_base_class_defines_get_language_name(self):
        """Base class should define get_language_name abstract method."""
        from src.kpis.cognitive_complexity.calculator_base import (
            CognitiveComplexityCalculatorBase
        )

        # Check that method exists
        assert hasattr(CognitiveComplexityCalculatorBase, 'get_language_name')
        assert callable(getattr(CognitiveComplexityCalculatorBase, 'get_language_name'))


class TestPythonCalculatorExtendsBase:
    """Test that Python calculator properly extends base class."""

    def test_python_calculator_extends_base(self):
        """Python calculator should extend CognitiveComplexityCalculatorBase."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )
        from src.kpis.cognitive_complexity.calculator_base import (
            CognitiveComplexityCalculatorBase
        )

        # Should be subclass of base
        assert issubclass(PythonCognitiveComplexityCalculator, CognitiveComplexityCalculatorBase)

    def test_python_calculator_can_be_instantiated(self):
        """Python calculator should be concrete and instantiable."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        # Should be able to create instance
        calculator = PythonCognitiveComplexityCalculator()
        assert calculator is not None

    def test_python_calculator_implements_calculate_for_file(self):
        """Python calculator should implement calculate_for_file method."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        calculator = PythonCognitiveComplexityCalculator()
        assert hasattr(calculator, 'calculate_for_file')
        assert callable(calculator.calculate_for_file)

    def test_python_calculator_implements_get_language_name(self):
        """Python calculator should implement get_language_name method."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        calculator = PythonCognitiveComplexityCalculator()
        assert hasattr(calculator, 'get_language_name')
        assert callable(calculator.get_language_name)

    def test_python_calculator_returns_python_as_language(self):
        """Python calculator should return 'Python' as language name."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        calculator = PythonCognitiveComplexityCalculator()
        assert calculator.get_language_name() == 'Python'


class TestPythonCalculatorInterface:
    """Test the new interface of Python calculator (calculate_for_file)."""

    def test_calculate_for_file_returns_dict(self):
        """calculate_for_file should return dict of function name -> complexity."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        code = '''
def simple_function(x):
    if x > 0:  # +1
        return True
    return False
'''
        calculator = PythonCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        # Should return dict
        assert isinstance(result, dict)
        # Should have function name as key
        assert 'simple_function' in result
        # Should have correct complexity value
        assert result['simple_function'] == 1

    def test_calculate_for_file_with_multiple_functions(self):
        """calculate_for_file should handle multiple functions."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        code = '''
def function_a(x):
    if x > 0:  # +1
        return True
    return False

def function_b(x, y):
    if x > 0:      # +1
        if y > 0:  # +2 (nesting)
            return True
    return False
'''
        calculator = PythonCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        # Should return dict with both functions
        assert isinstance(result, dict)
        assert 'function_a' in result
        assert 'function_b' in result
        assert result['function_a'] == 1
        assert result['function_b'] == 3

    def test_calculate_for_file_with_no_functions(self):
        """calculate_for_file should return empty dict for code with no functions."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        code = '''
# Just a comment
x = 1
y = 2
z = x + y
'''
        calculator = PythonCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        # Should return empty dict
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_calculate_for_file_with_syntax_error(self):
        """calculate_for_file should raise SyntaxError for invalid Python."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        code = '''
def invalid_syntax(x):
    if x > 0
        return True  # Missing colon
'''
        calculator = PythonCognitiveComplexityCalculator()

        # Should raise SyntaxError
        with pytest.raises(SyntaxError):
            calculator.calculate_for_file(code)


class TestPythonCalculatorBackwardCompatibility:
    """Test that refactoring doesn't break existing functionality."""

    def test_nested_if_complexity_unchanged(self):
        """Ensure nested if complexity calculation is unchanged."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        code = '''
def nested_ifs(x, y, z):
    if x:           # +1 (nesting level 0)
        if y:       # +2 (nesting level 1: +1 base + 1 nesting)
            if z:   # +3 (nesting level 2: +1 base + 2 nesting)
                return True
    return False
'''
        calculator = PythonCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        # Should match original implementation
        assert result['nested_ifs'] == 6

    def test_boolean_operators_unchanged(self):
        """Ensure boolean operator handling is unchanged."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        code = '''
def single_and(a, b):
    if a and b:  # +1 for if, +1 for boolean sequence
        return True
    return False
'''
        calculator = PythonCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        # Should match original implementation
        assert result['single_and'] == 2

    def test_recursion_detection_unchanged(self):
        """Ensure recursion detection is unchanged."""
        from src.kpis.cognitive_complexity.calculator_python import (
            PythonCognitiveComplexityCalculator
        )

        code = '''
def factorial(n):
    if n <= 1:           # +1
        return 1
    return n * factorial(n - 1)  # +1 for recursion
'''
        calculator = PythonCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        # Should match original implementation
        assert result['factorial'] == 2
