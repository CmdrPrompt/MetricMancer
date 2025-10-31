"""
Tests for JavaScript Cognitive Complexity Calculator.

Tests tree-sitter-based cognitive complexity calculation for JavaScript code.
Based on SonarSource specification.

TDD RED-GREEN-REFACTOR:
1. RED - Write failing tests for JavaScript calculator
2. GREEN - Implement JavaScript calculator
3. REFACTOR - Ensure clean code
"""


class TestJavaScriptCalculatorBasicStructures:
    """Test basic control structures in JavaScript."""

    def test_simple_if_statement(self):
        """Single if statement should have cognitive complexity of 1."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function simpleIf(x) {
    if (x > 0) {  // +1
        return 1;
    }
    return 0;
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert 'simpleIf' in result
        assert result['simpleIf'] == 1

    def test_if_else_statement(self):
        """If-else statement should have cognitive complexity of 2."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function ifElse(x) {
    if (x > 0) {    // +1
        return 1;
    } else {        // +1
        return 0;
    }
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ifElse'] == 2

    def test_for_loop(self):
        """For loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function forLoop(items) {
    for (let item of items) {  // +1
        console.log(item);
    }
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['forLoop'] == 1

    def test_while_loop(self):
        """While loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function whileLoop(n) {
    let count = 0;
    while (count < n) {  // +1
        count++;
    }
    return count;
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['whileLoop'] == 1

    def test_switch_statement(self):
        """Each case in switch should add +1."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function switchCase(x) {
    switch (x) {
        case 1:     // +1
            return "one";
        case 2:     // +1
            return "two";
        default:    // +1
            return "other";
    }
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['switchCase'] == 3


class TestJavaScriptCalculatorNesting:
    """Test nesting penalty in JavaScript."""

    def test_nested_if_statements(self):
        """Nested if statements should increase complexity with nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function nestedIfs(x, y, z) {
    if (x) {           // +1 (nesting level 0)
        if (y) {       // +2 (1 base + 1 nesting)
            if (z) {   // +3 (1 base + 2 nesting)
                return true;
            }
        }
    }
    return false;
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['nestedIfs'] == 6  # 1 + 2 + 3

    def test_if_in_loop(self):
        """If statement inside loop should have nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function ifInLoop(items) {
    for (let item of items) {    // +1 (nesting level 0)
        if (item > 0) {          // +2 (1 base + 1 nesting)
            console.log(item);
        }
    }
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ifInLoop'] == 3  # 1 + 2


class TestJavaScriptCalculatorBooleanOperators:
    """Test boolean operators in JavaScript."""

    def test_logical_and_operator(self):
        """Logical && should add +1."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function logicalAnd(a, b) {
    if (a && b) {  // +1 for if, +1 for &&
        return true;
    }
    return false;
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logicalAnd'] == 2

    def test_logical_or_operator(self):
        """Logical || should add +1."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function logicalOr(a, b) {
    if (a || b) {  // +1 for if, +1 for ||
        return true;
    }
    return false;
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logicalOr'] == 2


class TestJavaScriptCalculatorExceptionHandling:
    """Test exception handling in JavaScript."""

    def test_try_catch(self):
        """Try-catch should add +1 for catch block."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function tryCatch() {
    try {
        riskyOperation();
    } catch (e) {  // +1
        handleError();
    }
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['tryCatch'] == 1

    def test_try_catch_finally(self):
        """Finally block should not add complexity."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function tryCatchFinally() {
    try {
        riskyOperation();
    } catch (e) {  // +1
        handleError();
    } finally {    // +0 (finally doesn't add complexity)
        cleanup();
    }
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['tryCatchFinally'] == 1


class TestJavaScriptCalculatorArrowFunctions:
    """Test arrow functions in JavaScript."""

    def test_simple_arrow_function(self):
        """Arrow function with if statement should work."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
const arrowIf = (x) => {
    if (x > 0) {  // +1
        return 1;
    }
    return 0;
};
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert 'arrowIf' in result
        assert result['arrowIf'] == 1

    def test_nested_arrow_function(self):
        """Nested arrow function should isolate complexity."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
const outer = (x) => {
    if (x > 0) {  // +1
        const inner = (y) => {
            if (y > 0) {  // +1 (but in separate function)
                return y;
            }
            return 0;
        };
        return inner(x);
    }
    return 0;
};
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['outer'] == 1
        assert result['inner'] == 1


class TestJavaScriptCalculatorEdgeCases:
    """Test edge cases for JavaScript."""

    def test_empty_function(self):
        """Empty function should have complexity 0."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function emptyFunction() {
    // Empty
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['emptyFunction'] == 0

    def test_multiple_functions(self):
        """Should handle multiple functions in one file."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function functionA(x) {
    if (x > 0) {  // +1
        return 1;
    }
    return 0;
}

function functionB(x, y) {
    if (x > 0) {      // +1
        if (y > 0) {  // +2
            return 1;
        }
    }
    return 0;
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['functionA'] == 1
        assert result['functionB'] == 3

    def test_ternary_operator(self):
        """Ternary operator (? :) should add +1."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        code = '''
function ternary(x) {
    return x > 0 ? "positive" : "non-positive";  // +1
}
'''
        calculator = JavaScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ternary'] == 1


class TestJavaScriptCalculatorLanguageName:
    """Test language name."""

    def test_get_language_name_returns_javascript(self):
        """Calculator should return 'JavaScript' as language name."""
        from src.kpis.cognitive_complexity.calculator_javascript import (
            JavaScriptCognitiveComplexityCalculator
        )

        calculator = JavaScriptCognitiveComplexityCalculator()
        assert calculator.get_language_name() == 'JavaScript'
