"""
Go Cognitive Complexity Calculator.

Calculates cognitive complexity for Go code using tree-sitter.
Implements CognitiveComplexityCalculatorBase interface.

Based on SonarSource Cognitive Complexity specification:
https://www.sonarsource.com/docs/CognitiveComplexity.pdf
"""

from typing import Dict, List
from tree_sitter import Node
from tree_sitter_language_pack import get_parser
from .calculator_base import CognitiveComplexityCalculatorBase


class GoCognitiveComplexityCalculator(CognitiveComplexityCalculatorBase):
    """
    Calculator for Cognitive Complexity using tree-sitter for Go.

    Implements the SonarSource Cognitive Complexity algorithm for Go code.
    """

    # Control flow structures that increment complexity
    INCREMENTS = {
        'if_statement': 1,
        'for_statement': 1,  # Go's only loop type
        'expression_case': 1,  # case in switch
        'default_case': 1,  # default in switch
        'communication_case': 1,  # case in select
        'defer_statement': 1,  # Go-specific: defer
        'go_statement': 1,  # Go-specific: goroutine launch
        # Note: switch_statement and select_statement themselves don't increment,
        # only their cases do (per SonarSource spec)
    }

    # Structures that increase nesting level
    NESTING_INCREMENTS = {
        'function_declaration',
        'method_declaration',
        'func_literal',  # Anonymous functions
        'if_statement',
        'for_statement',
        # Note: switch and select do NOT increase nesting per SonarSource spec
        # Only if/for/while/try increase nesting
    }

    # Logical operators that increment complexity
    LOGICAL_OPERATORS = {'&&', '||'}

    def __init__(self):
        self.parser = get_parser('go')
        self.current_function_name = None

    def get_language_name(self) -> str:
        """
        Get the name of the language this calculator supports.

        Returns:
            str: 'Go'
        """
        return 'Go'

    def calculate_for_file(self, file_content: str) -> Dict[str, int]:
        """
        Calculate cognitive complexity for all functions in a Go file.

        Args:
            file_content: Go source code as string

        Returns:
            Dict mapping function names to their complexity values
            Example: {'main': 5, 'helper': 3, 'Process': 12}

        Raises:
            SyntaxError: If the Go code cannot be parsed
        """
        tree = self.parser.parse(bytes(file_content, 'utf8'))
        functions = self._find_functions(tree.root_node)

        function_complexities = {}
        for func_node in functions:
            name = self._get_function_name(func_node)
            complexity = self._calculate_complexity(func_node)
            function_complexities[name] = complexity

        return function_complexities

    def _find_functions(self, node: Node) -> List[Node]:
        """Find all function declarations in the tree."""
        functions = []

        if node.type in ('function_declaration', 'method_declaration'):
            functions.append(node)

        for child in node.children:
            functions.extend(self._find_functions(child))

        return functions

    def _get_function_name(self, node: Node) -> str:
        """Extract function name from node."""
        # For function_declaration and method_declaration,
        # the name is in an 'identifier' child node
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode('utf8')

        return 'anonymous'

    def _calculate_complexity(self, function_node: Node) -> int:
        """Calculate complexity for a single function."""
        self.current_function_name = self._get_function_name(function_node)

        body = self._get_function_body(function_node)
        if body is None:
            return 0

        return self._traverse_for_complexity(body)

    def _traverse_for_complexity(self, body: Node) -> int:
        """Traverse the AST and calculate total complexity."""
        complexity = [0]  # Use list to allow modification in nested function

        def traverse(node: Node, nesting_level: int):
            complexity[0] += self._get_node_complexity(node, nesting_level)
            new_nesting = self._get_new_nesting_level(node, nesting_level)

            for child in node.children:
                traverse(child, new_nesting)

        traverse(body, nesting_level=0)
        return complexity[0]

    def _get_node_complexity(self, node: Node, nesting_level: int) -> int:
        """Calculate complexity contribution of a single node."""
        complexity = 0
        complexity += self._get_control_flow_complexity(node, nesting_level)
        complexity += self._get_else_clause_complexity(node, nesting_level)
        complexity += self._get_logical_operator_complexity(node)
        return complexity

    def _get_control_flow_complexity(self, node: Node, nesting_level: int) -> int:
        """Calculate complexity for control flow structures."""
        if node.type not in self.INCREMENTS:
            return 0
        return self.INCREMENTS[node.type] + nesting_level

    def _get_else_clause_complexity(self, node: Node, nesting_level: int) -> int:
        """Calculate complexity for else clauses in if statements."""
        if node.type != 'if_statement':
            return 0
        for child in node.children:
            if child.type == 'else':
                return 1 + nesting_level
        return 0

    def _get_logical_operator_complexity(self, node: Node) -> int:
        """Calculate complexity for logical operators (&&, ||)."""
        if node.type != 'binary_expression':
            return 0
        operator = self._get_binary_operator(node)
        if operator in self.LOGICAL_OPERATORS:
            return 1
        return 0

    def _get_new_nesting_level(self, node: Node, current_level: int) -> int:
        """Calculate new nesting level for children."""
        if node.type in self.NESTING_INCREMENTS:
            return current_level + 1
        return current_level

    def _get_function_body(self, node: Node) -> Node:
        """Get the body node of a function (block)."""
        for child in node.children:
            if child.type == 'block':
                return child
        return None

    def _get_binary_operator(self, binary_expr: Node) -> str:
        """Get operator from binary expression node."""
        for child in binary_expr.children:
            text = child.text.decode('utf8')
            if text in self.LOGICAL_OPERATORS:
                return text
        return None
