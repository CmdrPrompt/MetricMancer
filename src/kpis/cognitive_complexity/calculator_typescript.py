"""
TypeScript Cognitive Complexity Calculator.

Calculates cognitive complexity for TypeScript code using tree-sitter.
Implements CognitiveComplexityCalculatorBase interface.

Based on SonarSource Cognitive Complexity specification:
https://www.sonarsource.com/docs/CognitiveComplexity.pdf
"""

from typing import Dict, List
from tree_sitter import Node
from tree_sitter_languages import get_parser
from .calculator_base import CognitiveComplexityCalculatorBase


class TypeScriptCognitiveComplexityCalculator(CognitiveComplexityCalculatorBase):
    """
    Calculator for Cognitive Complexity using tree-sitter for TypeScript.

    Implements the SonarSource Cognitive Complexity algorithm for TypeScript code.
    Supports both regular functions and arrow functions, as well as TypeScript-specific features.
    """

    # Control flow structures that increment complexity
    INCREMENTS = {
        'if_statement': 1,
        'for_statement': 1,
        'for_in_statement': 1,
        'while_statement': 1,
        'do_statement': 1,
        'switch_case': 1,  # Each case in switch
        'switch_default': 1,  # Default case in switch
        'catch_clause': 1,
        'ternary_expression': 1,  # Ternary operator (? :)
    }

    # Structures that increase nesting level
    NESTING_INCREMENTS = {
        'function_declaration',
        'function',  # Function expression
        'arrow_function',
        'method_definition',
        'if_statement',
        'for_statement',
        'for_in_statement',
        'while_statement',
        'do_statement',
        # Note: switch_statement does NOT increase nesting per SonarSource spec
        'catch_clause',
        'class_declaration',
    }

    # Logical operators that increment complexity
    LOGICAL_OPERATORS = {'&&', '||'}

    def __init__(self):
        self.parser = get_parser('typescript')
        self.current_function_name = None

    def get_language_name(self) -> str:
        """
        Get the name of the language this calculator supports.

        Returns:
            str: 'TypeScript'
        """
        return 'TypeScript'

    def calculate_for_file(self, file_content: str) -> Dict[str, int]:
        """
        Calculate cognitive complexity for all functions in a TypeScript file.

        Args:
            file_content: TypeScript source code as string

        Returns:
            Dict mapping function names to their complexity values
            Example: {'main': 5, 'helper': 3, 'process': 12}

        Raises:
            SyntaxError: If the TypeScript code cannot be parsed
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

        if node.type in ('function_declaration', 'arrow_function', 'function', 'method_definition'):
            functions.append(node)

        for child in node.children:
            functions.extend(self._find_functions(child))

        return functions

    def _get_function_name(self, node: Node) -> str:
        """Extract function name from node."""
        # For function_declaration, the name is in an 'identifier' child
        if node.type == 'function_declaration':
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf8')

        # For arrow_function, look for variable_declarator parent
        if node.type == 'arrow_function':
            # Look for parent variable_declarator
            parent = node.parent
            while parent:
                if parent.type == 'variable_declarator':
                    # Get the identifier (name) from variable_declarator
                    for child in parent.children:
                        if child.type == 'identifier':
                            return child.text.decode('utf8')
                parent = parent.parent

        # For method_definition
        if node.type == 'method_definition':
            for child in node.children:
                if child.type == 'property_identifier':
                    return child.text.decode('utf8')

        return 'anonymous'

    def _calculate_complexity(self, function_node: Node) -> int:
        """Calculate complexity for a single function."""
        self.current_function_name = self._get_function_name(function_node)

        # Find function body (statement_block or expression)
        body = self._get_function_body(function_node)
        if body is None:
            return 0

        complexity = 0

        def traverse(node: Node, nesting_level: int):
            nonlocal complexity

            # Stop traversal if we encounter a nested function
            # Nested functions should be analyzed separately
            if node != body and node.type in ('function_declaration', 'function', 'arrow_function', 'method_definition'):
                return

            # Check if this node increments complexity
            if node.type in self.INCREMENTS:
                increment = self.INCREMENTS[node.type]
                complexity += increment + nesting_level

            # Handle else clause separately (always adds +1 + nesting)
            # In tree-sitter TypeScript, else is part of if_statement's children
            if node.type == 'if_statement':
                # Check for else clause
                for i, child in enumerate(node.children):
                    if child.type == 'else_clause':
                        # else clause adds +1 + nesting
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
        """Get the body node of a function (statement_block or expression)."""
        # For function_declaration and arrow_function
        for child in node.children:
            if child.type in ('statement_block', 'expression_statement'):
                return child
            # Arrow functions might have a direct expression as body
            if node.type == 'arrow_function' and child.type not in (
                'identifier', 'formal_parameters', '=>', '(', ')', 'const', 'let', 'var',
                'type_annotation', ':'  # TypeScript-specific tokens
            ):
                return child

        return None

    def _get_binary_operator(self, binary_expr: Node) -> str:
        """Get operator from binary expression node."""
        for child in binary_expr.children:
            text = child.text.decode('utf8')
            if text in self.LOGICAL_OPERATORS:
                return text
        return None
