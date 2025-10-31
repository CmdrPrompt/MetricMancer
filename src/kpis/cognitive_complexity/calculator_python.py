"""
Python Cognitive Complexity Calculator.

Calculates cognitive complexity for Python code using the ast module.
Implements CognitiveComplexityCalculatorBase interface.

Based on SonarSource Cognitive Complexity specification:
https://www.sonarsource.com/docs/CognitiveComplexity.pdf
"""

import ast
from typing import Dict
from .calculator_base import CognitiveComplexityCalculatorBase


class PythonCognitiveComplexityCalculator(CognitiveComplexityCalculatorBase):
    """
    Calculator for Cognitive Complexity using Python AST.

    Implements the SonarSource Cognitive Complexity algorithm for Python code.
    """

    def __init__(self):
        self.current_function_name = None

    def get_language_name(self) -> str:
        """
        Get the name of the language this calculator supports.

        Returns:
            str: 'Python'
        """
        return 'Python'

    def calculate_for_file(self, file_content: str) -> Dict[str, int]:
        """
        Calculate cognitive complexity for all functions in a Python file.

        Args:
            file_content: Python source code as string

        Returns:
            Dict mapping function names to their complexity values
            Example: {'main': 5, 'helper': 3, 'process_data': 12}

        Raises:
            SyntaxError: If the Python code cannot be parsed
        """
        tree = ast.parse(file_content)
        function_complexities = {}

        # Calculate for each function in the file
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_complexity = self.calculate_for_function(node)
                function_complexities[node.name] = func_complexity

        return function_complexities

    def calculate_for_function(self, function_node: ast.FunctionDef) -> int:
        """
        Calculate cognitive complexity for a single function.

        Algorithm:
        - Basic control structures (if/for/while/except): +1 + nesting
        - else/elif: +1 + nesting
        - Boolean operator sequences: +1 (not per operator)
        - Ternary operators: +1 + nesting
        - Recursion: +1
        - Nesting: Each level increases penalty

        Args:
            function_node: AST FunctionDef node

        Returns:
            int: Cognitive complexity score

        Example:
            def flat_code(x):      # Complexity: 4
                if x > 0:          # +1
                    return 1
                elif x < 0:        # +1
                    return -1
                elif x == 0:       # +1
                    return 0
                else:              # +1
                    return None

            def nested_code(x):    # Complexity: 6
                if x > 0:          # +1 (nesting 0)
                    if x > 10:     # +2 (nesting 1)
                        if x > 20: # +3 (nesting 2)
                            return 1
        """
        self.current_function_name = function_node.name

        # Use nesting-aware calculation starting at nesting level 0
        complexity = 0
        for node in function_node.body:
            complexity += self.calculate_with_nesting(node, nesting=0)

        return complexity

    def _check_boolean_operators(self, node: ast.AST) -> int:
        """
        Check for boolean operators and add +1 per sequence.

        Multiple 'and' or 'or' in the same sequence count as 1.
        Returns the increment (1 for a boolean operator sequence, 0 otherwise).
        """
        if isinstance(node, ast.BoolOp):
            # Count operator type changes (and -> or or or -> and)
            # For now, simplify: +1 per BoolOp node (sequence of same operator)
            return 1

        # Recursively check children for boolean operators
        complexity = 0
        for child in ast.iter_child_nodes(node):
            complexity += self._check_boolean_operators(child)

        return complexity

    def _is_recursive_call(self, node: ast.Call) -> bool:
        """Check if a call node is a recursive call to current function."""
        if self.current_function_name is None:
            return False

        # Check if calling function with same name
        if isinstance(node.func, ast.Name):
            return node.func.id == self.current_function_name

        return False

    def calculate_with_nesting(self, node: ast.AST, nesting: int = 0) -> int:
        """
        Calculate cognitive complexity with nesting awareness.

        Args:
            node: AST node to analyze
            nesting: Current nesting level (0 = top level)

        Returns:
            Total cognitive complexity score
        """
        complexity = 0

        # Special handling for If nodes with else/elif
        if isinstance(node, ast.If):
            # +1 + nesting for 'if' keyword
            complexity += 1 + nesting

            # Check for boolean operators in condition
            complexity += self._check_boolean_operators(node.test)

            # Process 'if' body with increased nesting
            for child in node.body:
                complexity += self.calculate_with_nesting(child, nesting + 1)

            # Process 'else' clause (orelse)
            if node.orelse:
                # Check if it's elif (another If node) or else
                if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                    # It's an elif - process as separate If (+1 + nesting)
                    complexity += self.calculate_with_nesting(node.orelse[0], nesting)
                else:
                    # It's an else - +1 + nesting for else keyword
                    complexity += 1 + nesting
                    for child in node.orelse:
                        complexity += self.calculate_with_nesting(child, nesting + 1)

        # Handle other nesting structures
        elif isinstance(node, (ast.For, ast.While)):
            complexity += 1 + nesting
            # Process body with increased nesting
            for child in node.body:
                complexity += self.calculate_with_nesting(child, nesting + 1)

        # Try-except blocks
        elif isinstance(node, ast.Try):
            # Process handlers (each except adds +1 + nesting)
            for handler in node.handlers:
                complexity += 1 + nesting
                for child in handler.body:
                    complexity += self.calculate_with_nesting(child, nesting + 1)

        # Ternary operator
        elif isinstance(node, ast.IfExp):
            complexity += 1 + nesting
            # Process all parts with increased nesting
            complexity += self.calculate_with_nesting(node.body, nesting + 1)
            complexity += self.calculate_with_nesting(node.test, nesting + 1)
            complexity += self.calculate_with_nesting(node.orelse, nesting + 1)

        # Boolean operators (and/or)
        elif isinstance(node, ast.BoolOp):
            complexity += self._check_boolean_operators(node)
            # Process operands at same nesting
            for operand in node.values:
                complexity += self.calculate_with_nesting(operand, nesting)

        # Recursion
        elif isinstance(node, ast.Call) and self._is_recursive_call(node):
            complexity += 1

        # For all other nodes, recursively process children
        for child in ast.iter_child_nodes(node):
            if not isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.IfExp, ast.BoolOp)):
                complexity += self.calculate_with_nesting(child, nesting)

        return complexity
