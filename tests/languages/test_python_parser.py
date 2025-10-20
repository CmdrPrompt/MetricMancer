"""
Unit tests for Python complexity parser.
Tests function pattern matching with type hints and complexity calculation.
"""
import unittest
from src.languages.parsers.python import PythonComplexityParser


class TestPythonComplexityParser(unittest.TestCase):
    """Test cases for Python complexity parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = PythonComplexityParser()

    def test_empty_file(self):
        """Test that empty Python file has base complexity of 1."""
        code = ""
        complexity = self.parser.compute_complexity(code)
        self.assertEqual(complexity, 1)

    def test_simple_function_no_type_hints(self):
        """Test function without type hints is detected."""
        code = """
def simple():
    return 42
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'simple')

    def test_function_with_parameters_no_hints(self):
        """Test function with parameters but no type hints."""
        code = """
def add(x, y):
    return x + y
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'add')

    def test_function_with_type_hints_parameters(self):
        """Test function with type hints on parameters."""
        code = """
def add(x: int, y: int):
    return x + y
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'add')

    def test_function_with_return_type_hint(self):
        """Test function with return type hint."""
        code = """
def get_name() -> str:
    return "Alice"
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'get_name')

    def test_function_with_full_type_hints(self):
        """Test function with both parameter and return type hints."""
        code = """
def add(x: int, y: int) -> int:
    return x + y
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'add')

    def test_method_with_self_and_type_hints(self):
        """Test class method with self and type hints."""
        code = """
class MyClass:
    def format(self, delta: DeltaDiff) -> str:
        return str(delta)
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'format')

    def test_complex_return_type_hints(self):
        """Test function with complex return type hints (Dict, List, Tuple, etc.)."""
        code = """
from typing import Dict, List, Tuple

def get_data() -> Dict[str, Any]:
    return {}

def get_list() -> List[str]:
    return []

def get_tuple() -> Tuple[int, str]:
    return (1, "a")
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 3)
        function_names = [f['name'] for f in functions]
        self.assertIn('get_data', function_names)
        self.assertIn('get_list', function_names)
        self.assertIn('get_tuple', function_names)

    def test_optional_return_type(self):
        """Test function with Optional return type."""
        code = """
def find_user(id: int) -> Optional[User]:
    return None
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'find_user')

    def test_multiple_functions_with_mixed_hints(self):
        """Test file with multiple functions, some with hints and some without."""
        code = """
def no_hints():
    return 1

def with_params(x: int, y: str):
    return x

def with_return() -> bool:
    return True

def full_hints(x: int) -> str:
    return str(x)
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 4)
        function_names = [f['name'] for f in functions]
        self.assertIn('no_hints', function_names)
        self.assertIn('with_params', function_names)
        self.assertIn('with_return', function_names)
        self.assertIn('full_hints', function_names)

    def test_count_functions_with_type_hints(self):
        """Test counting functions with type hints."""
        code = """
def func1() -> str:
    return "a"

def func2(x: int) -> int:
    return x

def func3():
    pass
"""
        count = self.parser.count_functions(code)
        self.assertEqual(count, 3)

    def test_indented_methods(self):
        """Test detecting indented methods in classes."""
        code = """
class DeltaReviewStrategyFormat:
    def _format_header(self, delta: DeltaDiff) -> str:
        return f"# Header"

    def _format_overview(self, delta: DeltaDiff) -> str:
        return "Overview"
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 2)
        function_names = [f['name'] for f in functions]
        self.assertIn('_format_header', function_names)
        self.assertIn('_format_overview', function_names)

    def test_complexity_calculation_simple(self):
        """Test complexity calculation for simple function."""
        code = """
def simple():
    return 42
"""
        complexity = self.parser.compute_complexity(code)
        # 1 base + 1 return
        self.assertEqual(complexity, 2)

    def test_complexity_calculation_with_if(self):
        """Test complexity calculation with if statement."""
        code = """
def check(x: int) -> bool:
    if x > 0:
        return True
    return False
"""
        complexity = self.parser.compute_complexity(code)
        # 1 base + 1 if + 2 return
        self.assertEqual(complexity, 4)

    def test_complexity_calculation_with_elif(self):
        """Test complexity calculation with elif."""
        code = """
def categorize(x: int) -> str:
    if x < 0:
        return "negative"
    elif x == 0:
        return "zero"
    else:
        return "positive"
"""
        complexity = self.parser.compute_complexity(code)
        # 1 base + 1 if + 1 elif + 3 return
        self.assertEqual(complexity, 6)

    def test_complexity_calculation_with_loops(self):
        """Test complexity calculation with loops."""
        code = """
def process(items: List[str]) -> int:
    count = 0
    for item in items:
        if item:
            count += 1
    return count
"""
        complexity = self.parser.compute_complexity(code)
        # 1 base + 1 for + 1 if + 1 return
        self.assertEqual(complexity, 4)

    def test_complexity_calculation_with_try_except(self):
        """Test complexity calculation with try-except."""
        code = """
def safe_divide(x: int, y: int) -> float:
    try:
        return x / y
    except ZeroDivisionError:
        return 0.0
"""
        complexity = self.parser.compute_complexity(code)
        # 1 base + 1 try + 1 except + 2 return
        self.assertEqual(complexity, 5)

    def test_complexity_calculation_with_boolean_operators(self):
        """Test complexity calculation with and/or operators."""
        code = """
def check(x: int, y: int) -> bool:
    if x > 0 and y > 0:
        return True
    if x < 0 or y < 0:
        return False
    return None
"""
        complexity = self.parser.compute_complexity(code)
        # 1 base + 2 if + 1 and + 1 or + 3 return
        self.assertEqual(complexity, 8)

    def test_real_world_example_delta_review_format(self):
        """Test with real-world example from delta_review_format.py."""
        code = """
def _format_function_change(
    self,
    change: FunctionChange,
    include_guidance: bool = False,
    brief: bool = False
) -> List[str]:
    lines = []

    if change.change_type == ChangeType.ADDED:
        icon = "➕"
    elif change.complexity_delta > 0:
        icon = "🔴" if change.complexity_delta > 10 else "🟡"
    else:
        icon = "🟢"

    if brief:
        complexity_info = ""
        if change.complexity_before is not None and change.complexity_after is not None:
            complexity_info = f" ({change.complexity_before} → {change.complexity_after})"
        elif change.complexity_after is not None:
            complexity_info = f" (complexity: {change.complexity_after})"

        lines.append(
            f"- {icon} `{change.function_name}()` in {change.file_path}{complexity_info}"
        )
    return lines
"""
        functions = self.parser.analyze_functions(code)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], '_format_function_change')
        # Verify it has reasonable complexity
        self.assertGreater(functions[0]['complexity'], 1)


if __name__ == '__main__':
    unittest.main()
