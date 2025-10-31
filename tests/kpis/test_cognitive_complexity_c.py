"""
Tests for C Cognitive Complexity Calculator.

Tests tree-sitter-based cognitive complexity calculation for C code.
Based on SonarSource specification.

TDD RED-GREEN-REFACTOR:
1. RED - Write failing tests for C calculator
2. GREEN - Implement C calculator
3. REFACTOR - Ensure clean code
"""


class TestCCalculatorBasicStructures:
    """Test basic control structures in C."""

    def test_simple_if_statement(self):
        """Single if statement should have cognitive complexity of 1."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int simple_if(int x) {
    if (x > 0) {  // +1
        return 1;
    }
    return 0;
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert 'simple_if' in result
        assert result['simple_if'] == 1

    def test_if_else_statement(self):
        """If-else statement should have cognitive complexity of 2."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int if_else(int x) {
    if (x > 0) {    // +1
        return 1;
    } else {        // +1
        return 0;
    }
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['if_else'] == 2

    def test_for_loop(self):
        """For loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
void for_loop(int n) {
    for (int i = 0; i < n; i++) {  // +1
        printf("%d", i);
    }
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['for_loop'] == 1

    def test_while_loop(self):
        """While loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int while_loop(int n) {
    int count = 0;
    while (count < n) {  // +1
        count++;
    }
    return count;
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['while_loop'] == 1

    def test_do_while_loop(self):
        """Do-while loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int do_while_loop(int n) {
    int count = 0;
    do {            // +1
        count++;
    } while (count < n);
    return count;
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['do_while_loop'] == 1

    def test_switch_statement(self):
        """Each case in switch should add +1."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int switch_case(int x) {
    switch (x) {
        case 1:     // +1
            return 1;
        case 2:     // +1
            return 2;
        default:    // +1
            return 0;
    }
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['switch_case'] == 3


class TestCCalculatorNesting:
    """Test nesting penalty in C."""

    def test_nested_if_statements(self):
        """Nested if statements should increase complexity with nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int nested_ifs(int x, int y, int z) {
    if (x) {           // +1 (nesting level 0)
        if (y) {       // +2 (1 base + 1 nesting)
            if (z) {   // +3 (1 base + 2 nesting)
                return 1;
            }
        }
    }
    return 0;
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['nested_ifs'] == 6  # 1 + 2 + 3

    def test_if_in_loop(self):
        """If statement inside loop should have nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
void if_in_loop(int arr[], int n) {
    for (int i = 0; i < n; i++) {    // +1 (nesting level 0)
        if (arr[i] > 0) {            // +2 (1 base + 1 nesting)
            printf("%d", arr[i]);
        }
    }
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['if_in_loop'] == 3  # 1 + 2


class TestCCalculatorBooleanOperators:
    """Test boolean operators in C."""

    def test_logical_and_operator(self):
        """Logical && should add +1."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int logical_and(int a, int b) {
    if (a && b) {  // +1 for if, +1 for &&
        return 1;
    }
    return 0;
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logical_and'] == 2

    def test_logical_or_operator(self):
        """Logical || should add +1."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int logical_or(int a, int b) {
    if (a || b) {  // +1 for if, +1 for ||
        return 1;
    }
    return 0;
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logical_or'] == 2


class TestCCalculatorEdgeCases:
    """Test edge cases for C."""

    def test_empty_function(self):
        """Empty function should have complexity 0."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
void empty_function(void) {
    // Empty
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['empty_function'] == 0

    def test_multiple_functions(self):
        """Should handle multiple functions in one file."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int function_a(int x) {
    if (x > 0) {  // +1
        return 1;
    }
    return 0;
}

int function_b(int x, int y) {
    if (x > 0) {      // +1
        if (y > 0) {  // +2
            return 1;
        }
    }
    return 0;
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['function_a'] == 1
        assert result['function_b'] == 3

    def test_ternary_operator(self):
        """Ternary operator (? :) should add +1."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int ternary(int x) {
    return x > 0 ? 1 : 0;  // +1
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ternary'] == 1

    def test_goto_statement(self):
        """Goto statement should add +1 (control flow jump)."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        code = '''
int with_goto(int x) {
    if (x < 0) {  // +1
        goto error;
    }
    return x;
error:           // goto adds +1
    return -1;
}
'''
        calculator = CCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['with_goto'] == 2  # +1 for if, +1 for goto


class TestCCalculatorLanguageName:
    """Test language name."""

    def test_get_language_name_returns_c(self):
        """Calculator should return 'C' as language name."""
        from src.kpis.cognitive_complexity.calculator_c import (
            CCognitiveComplexityCalculator
        )

        calculator = CCognitiveComplexityCalculator()
        assert calculator.get_language_name() == 'C'
