"""
Tests for Go Cognitive Complexity Calculator.

Tests tree-sitter-based cognitive complexity calculation for Go code.
Based on SonarSource specification.

TDD RED-GREEN-REFACTOR:
1. RED - Write failing tests for Go calculator
2. GREEN - Implement Go calculator
3. REFACTOR - Ensure clean code
"""

import pytest


class TestGoCalculatorBasicStructures:
    """Test basic control structures in Go."""

    def test_simple_if_statement(self):
        """Single if statement should have cognitive complexity of 1."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func simpleIf(x int) int {
    if x > 0 {  // +1
        return 1
    }
    return 0
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert 'simpleIf' in result
        assert result['simpleIf'] == 1

    def test_if_else_statement(self):
        """If-else statement should have cognitive complexity of 2."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func ifElse(x int) int {
    if x > 0 {    // +1
        return 1
    } else {      // +1
        return 0
    }
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ifElse'] == 2

    def test_for_loop(self):
        """For loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func forLoop(items []int) {
    for _, item := range items {  // +1
        println(item)
    }
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['forLoop'] == 1

    def test_switch_statement(self):
        """Each case in switch should add +1."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func switchCase(x int) string {
    switch x {
    case 1:     // +1
        return "one"
    case 2:     // +1
        return "two"
    default:    // +1
        return "other"
    }
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['switchCase'] == 3


class TestGoCalculatorNesting:
    """Test nesting penalty in Go."""

    def test_nested_if_statements(self):
        """Nested if statements should increase complexity with nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func nestedIfs(x, y, z bool) bool {
    if x {         // +1 (nesting level 0)
        if y {     // +2 (1 base + 1 nesting)
            if z { // +3 (1 base + 2 nesting)
                return true
            }
        }
    }
    return false
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['nestedIfs'] == 6  # 1 + 2 + 3

    def test_if_in_loop(self):
        """If statement inside loop should have nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func ifInLoop(items []int) {
    for _, item := range items {  // +1 (nesting level 0)
        if item > 0 {             // +2 (1 base + 1 nesting)
            println(item)
        }
    }
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ifInLoop'] == 3  # 1 + 2


class TestGoCalculatorBooleanOperators:
    """Test boolean operators in Go."""

    def test_logical_and_operator(self):
        """Logical && should add +1."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func logicalAnd(a, b bool) bool {
    if a && b {  // +1 for if, +1 for &&
        return true
    }
    return false
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logicalAnd'] == 2

    def test_logical_or_operator(self):
        """Logical || should add +1."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func logicalOr(a, b bool) bool {
    if a || b {  // +1 for if, +1 for ||
        return true
    }
    return false
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logicalOr'] == 2


class TestGoCalculatorGoSpecific:
    """Test Go-specific constructs."""

    def test_select_statement(self):
        """Select statement (channel operations) should add +1 per case."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func selectExample(ch1, ch2 chan int) {
    select {        // select itself doesn't increment (like switch)
    case <-ch1:     // +1 for case
        println("ch1")
    case <-ch2:     // +1 for case
        println("ch2")
    }
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        # 2 cases = 2 (select itself doesn't count, per SonarSource spec)
        assert result['selectExample'] == 2

    def test_defer_statement(self):
        """Defer statement should add +1 (Go-specific)."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func deferExample() {
    defer cleanup()  // +1
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['deferExample'] == 1

    def test_go_statement(self):
        """Go statement (goroutine) should add +1."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func goroutineExample() {
    go doWork()  // +1
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['goroutineExample'] == 1


class TestGoCalculatorEdgeCases:
    """Test edge cases for Go."""

    def test_empty_function(self):
        """Empty function should have complexity 0."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func emptyFunc() {
    // Empty
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['emptyFunc'] == 0

    def test_multiple_functions(self):
        """Should handle multiple functions in one file."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        code = '''
package main

func funcA(x int) int {
    if x > 0 {  // +1
        return 1
    }
    return 0
}

func funcB(x, y int) int {
    if x > 0 {      // +1
        if y > 0 {  // +2
            return 1
        }
    }
    return 0
}
'''
        calculator = GoCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['funcA'] == 1
        assert result['funcB'] == 3


class TestGoCalculatorLanguageName:
    """Test language name."""

    def test_get_language_name_returns_go(self):
        """Calculator should return 'Go' as language name."""
        from src.kpis.cognitive_complexity.calculator_go import (
            GoCognitiveComplexityCalculator
        )

        calculator = GoCognitiveComplexityCalculator()
        assert calculator.get_language_name() == 'Go'
