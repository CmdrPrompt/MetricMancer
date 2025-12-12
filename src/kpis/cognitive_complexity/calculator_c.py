"""
C Cognitive Complexity Calculator.

Calculates cognitive complexity for C code using tree-sitter.
Implements CognitiveComplexityCalculatorBase interface.

Based on SonarSource Cognitive Complexity specification:
https://www.sonarsource.com/docs/CognitiveComplexity.pdf
"""

from typing import Dict, List
from tree_sitter import Node
from tree_sitter_language_pack import get_parser
from .calculator_base import CognitiveComplexityCalculatorBase


class CCognitiveComplexityCalculator(CognitiveComplexityCalculatorBase):
    """
    Calculator for Cognitive Complexity using tree-sitter for C.

    Implements the SonarSource Cognitive Complexity algorithm for C code.
    """

    # Control flow structures that increment complexity
    INCREMENTS = {
        'if_statement': 1,
        'for_statement': 1,
        'while_statement': 1,
        'do_statement': 1,  # do-while loop
        'case_statement': 1,  # Each case in switch (including default)
        'conditional_expression': 1,  # Ternary operator (? :)
        'goto_statement': 1,  # Goto statement
    }

    # Structures that increase nesting level
    NESTING_INCREMENTS = {
        'function_definition',
        'if_statement',
        'for_statement',
        'while_statement',
        'do_statement',
        # Note: switch_statement does NOT increase nesting per SonarSource spec
    }

    # Logical operators that increment complexity
    LOGICAL_OPERATORS = {'&&', '||'}

    def __init__(self):
        self.parser = get_parser('c')
        self.current_function_name = None

    def get_language_name(self) -> str:
        """
        Get the name of the language this calculator supports.

        Returns:
            str: 'C'
        """
        return 'C'

    def calculate_for_file(self, file_content: str) -> Dict[str, int]:
        """
        Calculate cognitive complexity for all functions in a C file.

        Args:
            file_content: C source code as string

        Returns:
            Dict mapping function names to their complexity values
            Example: {'main': 5, 'helper': 3, 'process': 12}

        Raises:
            SyntaxError: If the C code cannot be parsed
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
        """Find all function definitions in the tree."""
        functions = []

        if node.type == 'function_definition':
            functions.append(node)
        for child in node.children:
            functions.extend(self._find_functions(child))

        return functions

    def _get_function_name(self, node: Node) -> str:
        """Extract function name from function_definition node."""
        # In C tree-sitter, function_definition has a function_declarator child
        for child in node.children:
            if child.type == 'function_declarator':
                # The identifier is the first child of function_declarator
                for declarator_child in child.children:
                    if declarator_child.type == 'identifier':
                        return declarator_child.text.decode('utf8')

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
            if self._should_skip_node(node, body):
                return

            complexity[0] += self._get_node_complexity(node, nesting_level)
            new_nesting = self._get_new_nesting_level(node, nesting_level)

            for child in node.children:
                traverse(child, new_nesting)

        traverse(body, nesting_level=0)
        return complexity[0]

    def _should_skip_node(self, node: Node, body: Node) -> bool:
        """Check if node should be skipped during traversal."""
        # Stop traversal if we encounter a nested function
        return node != body and node.type == 'function_definition'

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
        increment = self.INCREMENTS[node.type]
        # Goto statements don't get nesting bonus per cognitive complexity rules
        if node.type == 'goto_statement':
            return increment
        return increment + nesting_level

    def _get_else_clause_complexity(self, node: Node, nesting_level: int) -> int:
        """Calculate complexity for else clauses in if statements."""
        if node.type != 'if_statement':
            return 0
        for child in node.children:
            if child.type == 'else_clause':
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
        """Get the body node of a function (compound_statement)."""
        for child in node.children:
            if child.type == 'compound_statement':
                return child
        return None

    def _get_binary_operator(self, binary_expr: Node) -> str:
        """Get operator from binary expression node."""
        for child in binary_expr.children:
            text = child.text.decode('utf8')
            if text in self.LOGICAL_OPERATORS:
                return text
        return None
