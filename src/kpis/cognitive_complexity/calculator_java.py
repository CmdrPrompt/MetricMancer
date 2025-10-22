"""
Java Cognitive Complexity Calculator.

Calculates cognitive complexity for Java code using tree-sitter.
Implements CognitiveComplexityCalculatorBase interface.

Based on SonarSource Cognitive Complexity specification:
https://www.sonarsource.com/docs/CognitiveComplexity.pdf
"""

from typing import Dict, List
from tree_sitter import Node
from tree_sitter_languages import get_parser
from .calculator_base import CognitiveComplexityCalculatorBase


class JavaCognitiveComplexityCalculator(CognitiveComplexityCalculatorBase):
    """
    Calculator for Cognitive Complexity using tree-sitter for Java.

    Implements the SonarSource Cognitive Complexity algorithm for Java code.
    """

    # Control flow structures that increment complexity
    INCREMENTS = {
        'if_statement': 1,
        'for_statement': 1,
        'enhanced_for_statement': 1,  # for-each loop
        'while_statement': 1,
        'do_statement': 1,
        'switch_label': 1,  # Each case/default in switch
        'catch_clause': 1,
        'ternary_expression': 1,  # Ternary operator (? :)
    }

    # Structures that increase nesting level
    NESTING_INCREMENTS = {
        'method_declaration',
        'constructor_declaration',
        'if_statement',
        'for_statement',
        'enhanced_for_statement',
        'while_statement',
        'do_statement',
        'switch_statement',
        'catch_clause',
        'lambda_expression',
        'class_declaration',
    }

    # Logical operators that increment complexity
    LOGICAL_OPERATORS = {'&&', '||'}

    def __init__(self):
        self.parser = get_parser('java')
        self.current_method_name = None

    def get_language_name(self) -> str:
        """
        Get the name of the language this calculator supports.

        Returns:
            str: 'Java'
        """
        return 'Java'

    def calculate_for_file(self, file_content: str) -> Dict[str, int]:
        """
        Calculate cognitive complexity for all methods in a Java file.

        Args:
            file_content: Java source code as string

        Returns:
            Dict mapping method names to their complexity values
            Example: {'main': 5, 'helper': 3, 'process': 12}

        Raises:
            SyntaxError: If the Java code cannot be parsed
        """
        tree = self.parser.parse(bytes(file_content, 'utf8'))
        methods = self._find_methods(tree.root_node)

        method_complexities = {}
        for method_node in methods:
            name = self._get_method_name(method_node)
            complexity = self._calculate_complexity(method_node)
            method_complexities[name] = complexity

        return method_complexities

    def _find_methods(self, node: Node) -> List[Node]:
        """Find all method declarations in the tree."""
        methods = []

        if node.type in ('method_declaration', 'constructor_declaration'):
            methods.append(node)

        for child in node.children:
            methods.extend(self._find_methods(child))

        return methods

    def _get_method_name(self, node: Node) -> str:
        """Extract method name from node."""
        # For method_declaration and constructor_declaration,
        # the name is in an 'identifier' child node
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode('utf8')

        return 'anonymous'

    def _calculate_complexity(self, method_node: Node) -> int:
        """Calculate complexity for a single method."""
        self.current_method_name = self._get_method_name(method_node)

        # Find method body (block node)
        body = self._get_method_body(method_node)
        if body is None:
            return 0

        complexity = 0

        def traverse(node: Node, nesting_level: int):
            nonlocal complexity

            # Check if this node increments complexity
            if node.type in self.INCREMENTS:
                increment = self.INCREMENTS[node.type]
                complexity += increment + nesting_level

            # Handle else clause separately (always adds +1 + nesting)
            # In tree-sitter Java, else is part of if_statement's children
            if node.type == 'if_statement':
                # Check for else clause
                for i, child in enumerate(node.children):
                    if child.type == 'else':
                        # Next node after 'else' keyword is the else body
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

        # Start traversal from method body
        traverse(body, nesting_level=0)

        return complexity

    def _get_method_body(self, node: Node) -> Node:
        """Get the body node of a method (block)."""
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
