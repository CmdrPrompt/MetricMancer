"""
Tests for Java Cognitive Complexity Calculator.

Tests tree-sitter-based cognitive complexity calculation for Java code.
Based on SonarSource specification.

TDD RED-GREEN-REFACTOR:
1. RED - Write failing tests for Java calculator
2. GREEN - Implement Java calculator
3. REFACTOR - Ensure clean code
"""

import pytest


class TestJavaCalculatorBasicStructures:
    """Test basic control structures in Java."""

    def test_simple_if_statement(self):
        """Single if statement should have cognitive complexity of 1."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static int simpleIf(int x) {
        if (x > 0) {  // +1
            return 1;
        }
        return 0;
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert 'simpleIf' in result
        assert result['simpleIf'] == 1

    def test_if_else_statement(self):
        """If-else statement should have cognitive complexity of 2."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static int ifElse(int x) {
        if (x > 0) {    // +1
            return 1;
        } else {        // +1
            return 0;
        }
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ifElse'] == 2

    def test_for_loop(self):
        """For loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static void forLoop(int[] items) {
        for (int item : items) {  // +1
            System.out.println(item);
        }
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['forLoop'] == 1

    def test_while_loop(self):
        """While loop should add +1 to cognitive complexity."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static int whileLoop(int n) {
        int count = 0;
        while (count < n) {  // +1
            count++;
        }
        return count;
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['whileLoop'] == 1

    def test_switch_statement(self):
        """Each case in switch should add +1."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static String switchCase(int x) {
        switch (x) {
            case 1:     // +1
                return "one";
            case 2:     // +1
                return "two";
            default:    // +1
                return "other";
        }
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['switchCase'] == 3


class TestJavaCalculatorNesting:
    """Test nesting penalty in Java."""

    def test_nested_if_statements(self):
        """Nested if statements should increase complexity with nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static boolean nestedIfs(boolean x, boolean y, boolean z) {
        if (x) {           // +1 (nesting level 0)
            if (y) {       // +2 (1 base + 1 nesting)
                if (z) {   // +3 (1 base + 2 nesting)
                    return true;
                }
            }
        }
        return false;
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['nestedIfs'] == 6  # 1 + 2 + 3

    def test_if_in_loop(self):
        """If statement inside loop should have nesting penalty."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static void ifInLoop(int[] items) {
        for (int item : items) {    // +1 (nesting level 0)
            if (item > 0) {         // +2 (1 base + 1 nesting)
                System.out.println(item);
            }
        }
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ifInLoop'] == 3  # 1 + 2


class TestJavaCalculatorBooleanOperators:
    """Test boolean operators in Java."""

    def test_logical_and_operator(self):
        """Logical && should add +1."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static boolean logicalAnd(boolean a, boolean b) {
        if (a && b) {  // +1 for if, +1 for &&
            return true;
        }
        return false;
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logicalAnd'] == 2

    def test_logical_or_operator(self):
        """Logical || should add +1."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static boolean logicalOr(boolean a, boolean b) {
        if (a || b) {  // +1 for if, +1 for ||
            return true;
        }
        return false;
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['logicalOr'] == 2


class TestJavaCalculatorExceptionHandling:
    """Test exception handling in Java."""

    def test_try_catch(self):
        """Try-catch should add +1 for catch block."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static void tryCatch() {
        try {
            riskyOperation();
        } catch (Exception e) {  // +1
            handleError();
        }
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['tryCatch'] == 1

    def test_multiple_catch_blocks(self):
        """Each catch block should add +1."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static void multipleCatch() {
        try {
            riskyOperation();
        } catch (IOException e) {     // +1
            handleIO();
        } catch (Exception e) {       // +1
            handleGeneric();
        }
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['multipleCatch'] == 2


class TestJavaCalculatorEdgeCases:
    """Test edge cases for Java."""

    def test_empty_method(self):
        """Empty method should have complexity 0."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static void emptyMethod() {
        // Empty
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['emptyMethod'] == 0

    def test_multiple_methods(self):
        """Should handle multiple methods in one class."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static int methodA(int x) {
        if (x > 0) {  // +1
            return 1;
        }
        return 0;
    }

    public static int methodB(int x, int y) {
        if (x > 0) {      // +1
            if (y > 0) {  // +2
                return 1;
            }
        }
        return 0;
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['methodA'] == 1
        assert result['methodB'] == 3

    def test_ternary_operator(self):
        """Ternary operator (? :) should add +1."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        code = '''
public class Test {
    public static String ternary(int x) {
        return x > 0 ? "positive" : "non-positive";  // +1
    }
}
'''
        calculator = JavaCognitiveComplexityCalculator()
        result = calculator.calculate_for_file(code)

        assert result['ternary'] == 1


class TestJavaCalculatorLanguageName:
    """Test language name."""

    def test_get_language_name_returns_java(self):
        """Calculator should return 'Java' as language name."""
        from src.kpis.cognitive_complexity.calculator_java import (
            JavaCognitiveComplexityCalculator
        )

        calculator = JavaCognitiveComplexityCalculator()
        assert calculator.get_language_name() == 'Java'
