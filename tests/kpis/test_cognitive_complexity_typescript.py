"""
Tests for TypeScript Cognitive Complexity Calculator.

Tests tree-sitter-based cognitive complexity calculation for TypeScript code.
Based on SonarSource specification.

TDD RED-GREEN-REFACTOR:
1. RED - Write failing tests for TypeScript calculator
2. GREEN - Implement TypeScript calculator
3. REFACTOR - Ensure clean code
"""

import pytest


class TestTypeScriptCalculatorBasicStructures:
    """Test basic control structures in TypeScript."""

    def test_simple_if_statement(self):
        """Single if statement should have cognitive complexity of 1."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function simpleIf(x: number): number {
    if (x > 0) {  // +1
        return 1;
    }
    return 0;
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert 'simpleIf' in result
        assert result['simpleIf'] == 1

    def test_if_else_statement(self):
        """If-else statement should have cognitive complexity of 2."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function ifElse(x: number): number {
    if (x > 0) {    // +1
        return 1;
    } else {        // +1
        return 0;
    }
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ifElse'] == 2

    def test_for_loop(self):
        """For loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function forLoop(items: number[]): void {
    for (let item of items) {  // +1
        console.log(item);
    }
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['forLoop'] == 1

    def test_while_loop(self):
        """While loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function whileLoop(n: number): number {
    let count: number = 0;
    while (count < n) {  // +1
        count++;
    }
    return count;
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['whileLoop'] == 1

    def test_switch_statement(self):
        """Each case in switch should add +1."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function switchCase(x: number): string {
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
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['switchCase'] == 3


class TestTypeScriptCalculatorNesting:
    """Test nesting penalty in TypeScript."""

    def test_nested_if_statements(self):
        """Nested if statements should increase complexity with nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function nestedIfs(x: boolean, y: boolean, z: boolean): boolean {
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
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['nestedIfs'] == 6  # 1 + 2 + 3

    def test_if_in_loop(self):
        """If statement inside loop should have nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function ifInLoop(items: number[]): void {
    for (let item of items) {    // +1 (nesting level 0)
        if (item > 0) {          // +2 (1 base + 1 nesting)
            console.log(item);
        }
    }
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ifInLoop'] == 3  # 1 + 2


class TestTypeScriptCalculatorBooleanOperators:
    """Test boolean operators in TypeScript."""

    def test_logical_and_operator(self):
        """Logical && should add +1."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function logicalAnd(a: boolean, b: boolean): boolean {
    if (a && b) {  // +1 for if, +1 for &&
        return true;
    }
    return false;
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logicalAnd'] == 2

    def test_logical_or_operator(self):
        """Logical || should add +1."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function logicalOr(a: boolean, b: boolean): boolean {
    if (a || b) {  // +1 for if, +1 for ||
        return true;
    }
    return false;
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logicalOr'] == 2


class TestTypeScriptCalculatorExceptionHandling:
    """Test exception handling in TypeScript."""

    def test_try_catch(self):
        """Try-catch should add +1 for catch block."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function tryCatch(): void {
    try {
        riskyOperation();
    } catch (e: Error) {  // +1
        handleError();
    }
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['tryCatch'] == 1

    def test_try_catch_finally(self):
        """Finally block should not add complexity."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function tryCatchFinally(): void {
    try {
        riskyOperation();
    } catch (e: Error) {  // +1
        handleError();
    } finally {           // +0 (finally doesn't add complexity)
        cleanup();
    }
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['tryCatchFinally'] == 1


class TestTypeScriptCalculatorArrowFunctions:
    """Test arrow functions in TypeScript."""

    def test_simple_arrow_function(self):
        """Arrow function with if statement should work."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
const arrowIf = (x: number): number => {
    if (x > 0) {  // +1
        return 1;
    }
    return 0;
};
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert 'arrowIf' in result
        assert result['arrowIf'] == 1

    def test_nested_arrow_function(self):
        """Nested arrow function should isolate complexity."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
const outer = (x: number): number => {
    if (x > 0) {  // +1
        const inner = (y: number): number => {
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
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['outer'] == 1
        assert result['inner'] == 1


class TestTypeScriptCalculatorTypeFeatures:
    """Test TypeScript-specific features."""

    def test_interface_method(self):
        """Method in class should be analyzed."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
class Calculator {
    add(x: number, y: number): number {
        if (x > 0 && y > 0) {  // +1 for if, +1 for &&
            return x + y;
        }
        return 0;
    }
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert 'add' in result
        assert result['add'] == 2

    def test_generic_function(self):
        """Generic function should work correctly."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function identity<T>(value: T): T {
    if (value) {  // +1
        return value;
    }
    return value;
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['identity'] == 1


class TestTypeScriptCalculatorEdgeCases:
    """Test edge cases for TypeScript."""

    def test_empty_function(self):
        """Empty function should have complexity 0."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function emptyFunction(): void {
    // Empty
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['emptyFunction'] == 0

    def test_multiple_functions(self):
        """Should handle multiple functions in one file."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function functionA(x: number): number {
    if (x > 0) {  // +1
        return 1;
    }
    return 0;
}

function functionB(x: number, y: number): number {
    if (x > 0) {      // +1
        if (y > 0) {  // +2
            return 1;
        }
    }
    return 0;
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['functionA'] == 1
        assert result['functionB'] == 3

    def test_ternary_operator(self):
        """Ternary operator (? :) should add +1."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        code = '''
function ternary(x: number): string {
    return x > 0 ? "positive" : "non-positive";  // +1
}
'''
        calculator = TypeScriptCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ternary'] == 1


class TestTypeScriptCalculatorLanguageName:
    """Test language name."""

    def test_get_language_name_returns_typescript(self):
        """Calculator should return 'TypeScript' as language name."""
        from src.kpis.cognitive_complexity.calculator_typescript import (
            TypeScriptCognitiveComplexityCalculator
        )

        calculator = TypeScriptCognitiveComplexityCalculator()
        assert calculator.get_language_name() == 'TypeScript'
