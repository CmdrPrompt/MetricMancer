"""
Cognitive Complexity KPI - Measures code understandability.

Based on SonarSource Cognitive Complexity specification:
https://www.sonarsource.com/docs/CognitiveComplexity.pdf

Cognitive Complexity measures how difficult code is to understand, accounting
for nesting depth and control flow structures.

Key principles:
1. Basic control structures (if, for, while, except) add +1
2. Nesting increases the penalty (+1 per nesting level)
3. Boolean operator sequences count as +1 (not per operator)
4. Recursion adds +1
"""

import ast
from typing import Any, Dict, List, Optional
from ..base_kpi import BaseKPI


class CognitiveComplexityCalculator:
    """
    Calculator for Cognitive Complexity using Python AST.
    
    Implements the SonarSource Cognitive Complexity algorithm.
    """
    
    def __init__(self):
        self.current_function_name = None
    
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
class CognitiveComplexityKPI(BaseKPI):
    """
    Cognitive Complexity KPI.
    
    Measures how difficult code is to understand, accounting for
    nesting depth and control flow structures.
    
    Based on: https://www.sonarsource.com/docs/CognitiveComplexity.pdf
    
    Thresholds (SonarQube recommendations):
    - 0-5: Low (Excellent)
    - 6-10: Medium (Good)
    - 11-15: High (Consider refactoring)
    - 16-25: Critical (Refactor soon)
    - 25+: Severe (Refactor immediately)
    """
    
    def __init__(self, value: int = 0, functions: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            value=value,
            name="Cognitive Complexity",
            unit="points",
            description="Measure of how difficult code is to understand"
        )
        self.functions = functions or []
    
    def calculate(self, file_path: str, file_content: str) -> int:
        """
        Calculate cognitive complexity from Python source code.
        
        Args:
            file_path: Path to the file (for context)
            file_content: Source code content
            
        Returns:
            int: Total cognitive complexity for the file
        """
        try:
            tree = ast.parse(file_content)
            calculator = CognitiveComplexityCalculator()
            
            total_complexity = 0
            function_complexities = []
            
            # Calculate for each function in the file
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_complexity = calculator.calculate_for_function(node)
                    total_complexity += func_complexity
                    
                    function_complexities.append({
                        'name': node.name,
                        'cognitive_complexity': func_complexity,
                        'line_start': node.lineno,
                        'line_end': node.end_lineno if hasattr(node, 'end_lineno') else None
                    })
            
            self.value = total_complexity
            self.functions = function_complexities
            
            return total_complexity
            
        except SyntaxError:
            # If file has syntax errors, return 0
            return 0
