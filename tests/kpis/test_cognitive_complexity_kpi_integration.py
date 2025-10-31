"""
Integration tests for CognitiveComplexityKPI using factory pattern.

Tests that CognitiveComplexityKPI.calculate() correctly uses the factory
to select and use language-specific calculators.

TDD RED-GREEN-REFACTOR:
1. RED - Write tests for factory integration
2. GREEN - Update KPI to use factory
3. REFACTOR - Ensure clean code
"""


class TestCognitiveComplexityKPIIntegration:
    """Test CognitiveComplexityKPI integration with factory."""

    def test_kpi_calculate_uses_factory_for_python(self):
        """KPI should use factory to get Python calculator for .py files."""
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityKPI
        )

        code = '''
def simple_function(x):
    if x > 0:  # +1
        return True
    return False
'''
        kpi = CognitiveComplexityKPI()
        result = kpi.calculate('test.py', code)

        # Should calculate correctly using Python calculator
        assert result.value == 1
        assert 'simple_function' in result.calculation_values
        assert result.calculation_values['simple_function'] == 1

    def test_kpi_calculate_returns_none_for_unsupported_language(self):
        """KPI should return None for unsupported languages."""
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityKPI
        )

        code = '''
# Some unsupported language code
function test() {
    if (true) {
        return 1;
    }
}
'''
        kpi = CognitiveComplexityKPI()
        result = kpi.calculate('test.xyz', code)  # .xyz is not supported

        # Should return None for unsupported language
        assert result.value is None
        assert result.calculation_values == {}

    def test_kpi_calculate_handles_parsing_errors_gracefully(self):
        """KPI should handle parsing errors without crashing."""
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityKPI
        )

        invalid_code = '''
def invalid_syntax(x):
    if x > 0
        return True  # Missing colon
'''
        kpi = CognitiveComplexityKPI()
        result = kpi.calculate('test.py', invalid_code)

        # Should return None for syntax errors
        assert result.value is None
        assert result.calculation_values == {}

    def test_kpi_calculate_with_multiple_functions(self):
        """KPI should sum complexity across all functions."""
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityKPI
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
        kpi = CognitiveComplexityKPI()
        result = kpi.calculate('test.py', code)

        # Should sum both functions: 1 + 3 = 4
        assert result.value == 4
        assert result.calculation_values['function_a'] == 1
        assert result.calculation_values['function_b'] == 3

    def test_kpi_calculate_with_no_functions(self):
        """KPI should return 0 for files with no functions."""
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityKPI
        )

        code = '''
# Just a comment
x = 1
y = 2
z = x + y
'''
        kpi = CognitiveComplexityKPI()
        result = kpi.calculate('test.py', code)

        # Should return 0 for no functions
        assert result.value == 0
        assert result.calculation_values == {}

    def test_kpi_preserves_metadata(self):
        """KPI should preserve name, unit, description metadata."""
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityKPI
        )

        kpi = CognitiveComplexityKPI()

        assert kpi.name == 'cognitive_complexity'
        assert kpi.unit == 'points'
        assert 'difficult' in kpi.description.lower()  # Contains 'difficult'

    def test_kpi_backward_compatibility_with_existing_code(self):
        """KPI should work exactly as before for Python files."""
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityKPI
        )

        # This is code from existing tests - should work identically
        code = '''
def nested_ifs(x, y, z):
    if x:           # +1 (nesting level 0)
        if y:       # +2 (nesting level 1: +1 base + 1 nesting)
            if z:   # +3 (nesting level 2: +1 base + 2 nesting)
                return True
    return False
'''
        kpi = CognitiveComplexityKPI()
        result = kpi.calculate('test.py', code)

        # Should match original implementation exactly
        assert result.value == 6
        assert result.calculation_values['nested_ifs'] == 6
