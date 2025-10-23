"""
C Cognitive Complexity Calculator.

Calculates cognitive complexity for C code using tree-sitter.
Implements CognitiveComplexityCalculatorBase interface.

Based on SonarSource Cognitive Complexity specification:
https://www.sonarsource.com/docs/CognitiveComplexity.pdf
"""

from typing import Dict, List
from tree_sitter import Node
from tree_sitter_languages import get_parser
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

        # Find function body (compound_statement)
        body = self._get_function_body(function_node)
        if body is None:
            return 0

        complexity = 0

        def traverse(node: Node, nesting_level: int):
            nonlocal complexity

            # Stop traversal if we encounter a nested function
            # (though nested functions are rare in C)
            if node != body and node.type == 'function_definition':
                return

            # Check if this node increments complexity
            if node.type in self.INCREMENTS:
                increment = self.INCREMENTS[node.type]
                # Goto statements don't get nesting bonus according to cognitive complexity rules
                if node.type == 'goto_statement':
                    complexity += increment
                else:
                    complexity += increment + nesting_level

            # Handle else clause separately (always adds +1 + nesting)
            # In tree-sitter C, else is part of if_statement's children as 'else_clause'
            if node.type == 'if_statement':
                # Check for else clause
                has_else = False
                for i, child in enumerate(node.children):
                    if child.type == 'else_clause':
                        has_else = True
                        # else keyword adds +1 + nesting
                        complexity += 1 + nesting_level

            # Handle binary expressions (&&, ||)
            # According to SonarSource: each operator sequence adds +1
            if node.type == 'binary_expression':
                operator = self._get_binary_operator(node)
                if operator in self.LOGICAL_OPERATORS:
                    complexity += 1

            # Calculate new nesting level for children
            new_nesting = nesting_level
            if node.type in self.NESTING_INCREMENTS:
                new_nesting += 1

            # Recursively process children
            for child in node.children:
                traverse(child, new_nesting)

        # Start traversal from function body
        traverse(body, nesting_level=0)

        return complexity

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
