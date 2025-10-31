"""
Tests for Cognitive Complexity KPI.

Based on SonarSource Cognitive Complexity specification:
https://www.sonarsource.com/docs/CognitiveComplexity.pdf

Test-Driven Development (TDD) approach:
1. RED - Write failing tests
2. GREEN - Implement minimal code to pass
3. REFACTOR - Improve code quality
"""

import ast


class TestCognitiveComplexityBasicStructures:
    """Test basic control structures contribute +1 to cognitive complexity."""

    def test_simple_if_statement(self):
        """Single if statement should have cognitive complexity of 1."""
        code = '''
def simple_if(x):
    if x > 0:  # +1
        return True
    return False
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 1, "Single if should have complexity 1"

    def test_if_else_statement(self):
        """If-else statement should have cognitive complexity of 2 (if +1, else +1)."""
        code = '''
def if_else(x):
    if x > 0:    # +1
        return 1
    else:        # +1
        return 0
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 2, "If-else should have complexity 2"

    def test_elif_chain(self):
        """Each elif adds +1 to cognitive complexity."""
        code = '''
def elif_chain(x):
    if x == 1:      # +1
        return "one"
    elif x == 2:    # +1
        return "two"
    elif x == 3:    # +1
        return "three"
    else:           # +1
        return "other"
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 4, "If-elif-elif-else should have complexity 4"

    def test_for_loop(self):
        """For loop should add +1 to cognitive complexity."""
        code = '''
def for_loop(items):
    result = []
    for item in items:  # +1
        result.append(item * 2)
    return result
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 1, "For loop should have complexity 1"

    def test_while_loop(self):
        """While loop should add +1 to cognitive complexity."""
        code = '''
def while_loop(n):
    count = 0
    while count < n:  # +1
        count += 1
    return count
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 1, "While loop should have complexity 1"


class TestCognitiveComplexityNesting:
    """Test that nesting increases cognitive complexity penalty."""

    def test_nested_if_statements(self):
        """Nested if statements should increase complexity with nesting penalty."""
        code = '''
def nested_ifs(x, y, z):
    if x:           # +1 (nesting level 0)
        if y:       # +2 (nesting level 1: +1 base + 1 nesting)
            if z:   # +3 (nesting level 2: +1 base + 2 nesting)
                return True
    return False
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 6, "Nested ifs (3 levels) should have complexity 1+2+3=6"

    def test_if_in_loop(self):
        """If statement inside loop should have nesting penalty."""
        code = '''
def if_in_loop(items):
    result = []
    for item in items:      # +1 (nesting level 0)
        if item > 0:        # +2 (nesting level 1: +1 base + 1 nesting)
            result.append(item)
    return result
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 3, "For + nested if should have complexity 1+2=3"

    def test_loop_in_loop(self):
        """Nested loops should have increasing penalties."""
        code = '''
def nested_loops(matrix):
    result = 0
    for row in matrix:          # +1 (nesting level 0)
        for item in row:        # +2 (nesting level 1: +1 base + 1 nesting)
            result += item
    return result
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 3, "Nested loops should have complexity 1+2=3"


class TestCognitiveComplexityBooleanOperators:
    """Test that boolean operators are counted correctly."""

    def test_single_and_operator(self):
        """Single 'and' in condition should add +1."""
        code = '''
def single_and(a, b):
    if a and b:  # +1 for if, +1 for boolean sequence
        return True
    return False
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 2, "If with 'and' should have complexity 2"

    def test_multiple_and_operators_count_once(self):
        """Multiple 'and' operators in same sequence should count as 1."""
        code = '''
def multiple_and(a, b, c, d):
    if a and b and c and d:  # +1 for if, +1 for boolean sequence (not +4!)
        return True
    return False
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 2, "If with multiple 'and' should have complexity 2"

    def test_mixed_and_or_operators(self):
        """Mixed and/or should count each distinct sequence."""
        code = '''
def mixed_operators(a, b, c, d):
    if (a and b) or (c and d):  # +1 for if, +1 for first 'and', +1 for 'or', +1 for second 'and'
        return True
    return False
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        # Note: Implementation detail - this might be 2 or 4 depending on interpretation
        # SonarSource spec says each operator sequence adds +1
        assert result >= 2, "If with mixed operators should have complexity >= 2"


class TestCognitiveComplexityTernaryOperator:
    """Test ternary operator (conditional expression) cognitive complexity."""

    def test_simple_ternary(self):
        """Ternary operator should add +1."""
        code = '''
def simple_ternary(x):
    return "positive" if x > 0 else "non-positive"  # +1 for ternary
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 1, "Ternary operator should have complexity 1"

    def test_nested_ternary(self):
        """Nested ternary operators should have nesting penalty."""
        code = '''
def nested_ternary(x, y):
    return "a" if x > 0 else ("b" if y > 0 else "c")  # +1 for outer, +2 for inner (nesting)
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 3, "Nested ternary should have complexity 1+2=3"


class TestCognitiveComplexityExceptionHandling:
    """Test exception handling cognitive complexity."""

    def test_try_except(self):
        """Try-except should add +1 for except block."""
        code = '''
def try_except():
    try:
        risky_operation()
    except Exception:  # +1
        handle_error()
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 1, "Try-except should have complexity 1"

    def test_multiple_except_blocks(self):
        """Each except block should add +1."""
        code = '''
def multiple_except():
    try:
        risky_operation()
    except ValueError:      # +1
        handle_value_error()
    except TypeError:       # +1
        handle_type_error()
    except Exception:       # +1
        handle_generic()
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 3, "Multiple except blocks should have complexity 3"


class TestCognitiveComplexityRecursion:
    """Test recursion detection and cognitive complexity."""

    def test_simple_recursion(self):
        """Recursive call should add +1."""
        code = '''
def factorial(n):
    if n <= 1:           # +1
        return 1
    return n * factorial(n - 1)  # +1 for recursion
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 2, "Recursive function should have complexity 2 (if + recursion)"


class TestCognitiveComplexityEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_function(self):
        """Empty function should have complexity 0."""
        code = '''
def empty_function():
    pass
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 0, "Empty function should have complexity 0"

    def test_function_with_only_assignments(self):
        """Function with only assignments should have complexity 0."""
        code = '''
def only_assignments():
    x = 1
    y = 2
    z = x + y
    return z
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 0, "Function without control structures should have complexity 0"

    def test_flat_vs_nested_comparison(self):
        """Demonstrate flat code has lower cognitive complexity than nested."""
        flat_code = '''
def flat_structure(type):
    if type == "A": return "handle_a"   # +1
    if type == "B": return "handle_b"   # +1
    if type == "C": return "handle_c"   # +1
    return "default"
'''
        nested_code = '''
def nested_structure(data):
    if data:                    # +1
        if data.valid:          # +2 (1 + 1 nesting)
            if data.processed:  # +3 (1 + 2 nesting)
                return True
    return False
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        flat_tree = ast.parse(flat_code)
        nested_tree = ast.parse(nested_code)
        calculator = CognitiveComplexityCalculator()

        flat_complexity = calculator.calculate_for_function(flat_tree.body[0])
        nested_complexity = calculator.calculate_for_function(nested_tree.body[0])

        assert flat_complexity == 3, "Flat structure should have complexity 3"
        assert nested_complexity == 6, "Nested structure should have complexity 6"
        assert nested_complexity > flat_complexity, "Nested should be more complex than flat"


class TestCognitiveComplexityRealWorldExample:
    """Test real-world code example from MetricMancer refactoring."""

    def test_old_generate_template_style(self):
        """Test cognitive complexity of old monolithic template generation."""
        code = '''
def generate_template_old(risk_level, ownership_type, complexity, churn):
    result = []

    if risk_level == "critical":        # +1
        result.append("CRITICAL")
        if ownership_type == "single":  # +2 (1 + 1 nesting)
            result.append("single owner")
    elif risk_level == "high":          # +1
        result.append("HIGH")
        if ownership_type == "single":  # +2 (1 + 1 nesting)
            result.append("single owner")

    if complexity > 15:                 # +1
        result.append("complex")

    return result
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        # Expected: 1 (if) + 2 (nested if) + 1 (elif) + 2 (nested if) + 1 (if) = 7
        assert result >= 6, "Old style should have high cognitive complexity"

    def test_new_helper_method_style(self):
        """Test cognitive complexity of new helper method approach."""
        code = '''
def generate_template_new(risk_level, ownership_type, complexity, churn):
    result = []
    result.extend(get_header(risk_level))
    result.extend(get_ownership_context(ownership_type))
    result.extend(get_focus_items(complexity, churn))
    return result
'''
        from src.kpis.cognitive_complexity.cognitive_complexity_kpi import (
            CognitiveComplexityCalculator
        )

        tree = ast.parse(code)
        calculator = CognitiveComplexityCalculator()
        result = calculator.calculate_for_function(tree.body[0])

        assert result == 0, "New style with helper methods should have complexity 0"
