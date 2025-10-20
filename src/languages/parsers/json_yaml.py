"""
Complexity parsers for structured data files (JSON, YAML, Shell).

Follows the ComplexityParser base class pattern for consistency.
"""

import json
import yaml
import re
from typing import Any
from src.languages.parsers.base import ComplexityParser


class JSONComplexityParser(ComplexityParser):
    """
    Parse and calculate structural complexity for JSON files.

    Complexity factors:
    - Max nesting depth (weight: 2)
    - Number of objects (weight: 1)
    - Number of arrays (weight: 1)
    - Total keys (weight: 0.1)
    """

    def compute_complexity(self, code: str) -> int:
        """Calculate structural complexity from JSON string."""
        try:
            data = json.loads(code)
        except json.JSONDecodeError:
            return 1  # Invalid JSON has base complexity

        if not data:
            return 1

        complexity = 0
        complexity += self._get_max_depth(data) * 2
        complexity += self._count_objects(data)
        complexity += self._count_arrays(data)
        complexity += self._count_keys(data) // 10

        return max(1, complexity)

    def _get_max_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._get_max_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._get_max_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth

    def _count_objects(self, obj: Any) -> int:
        """Count total number of objects (dicts)."""
        count = 0
        if isinstance(obj, dict):
            count = 1
            for value in obj.values():
                count += self._count_objects(value)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_objects(item)
        return count

    def _count_arrays(self, obj: Any) -> int:
        """Count total number of arrays (lists)."""
        count = 0
        if isinstance(obj, list):
            count = 1
            for item in obj:
                count += self._count_arrays(item)
        elif isinstance(obj, dict):
            for value in obj.values():
                count += self._count_arrays(value)
        return count

    def _count_keys(self, obj: Any) -> int:
        """Count total number of keys."""
        count = 0
        if isinstance(obj, dict):
            count = len(obj)
            for value in obj.values():
                count += self._count_keys(value)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_keys(item)
        return count


class YAMLComplexityParser(ComplexityParser):
    """
    Parse and calculate structural complexity for YAML files.

    Similar to JSON but includes YAML-specific features:
    - Anchors and aliases
    - Multi-line strings
    - Document separators
    """

    def compute_complexity(self, code: str) -> int:
        """Calculate structural complexity from YAML string."""
        try:
            data = yaml.safe_load(code)
        except yaml.YAMLError:
            return 1  # Invalid YAML has base complexity

        if not data and not code.strip():
            return 1

        complexity = 0

        # Structural complexity (like JSON)
        if data:
            complexity += self._get_max_depth(data) * 2
            complexity += self._count_objects(data)
            complexity += self._count_arrays(data)
            complexity += self._count_keys(data) // 10

        # YAML-specific features
        complexity += self._count_anchors_and_aliases(code)
        complexity += self._count_multiline_strings(code)
        complexity += self._count_documents(code)

        return max(1, complexity)

    def _get_max_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._get_max_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._get_max_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth

    def _count_objects(self, obj: Any) -> int:
        """Count total number of objects (dicts)."""
        count = 0
        if isinstance(obj, dict):
            count = 1
            for value in obj.values():
                count += self._count_objects(value)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_objects(item)
        return count

    def _count_arrays(self, obj: Any) -> int:
        """Count total number of arrays (lists)."""
        count = 0
        if isinstance(obj, list):
            count = 1
            for item in obj:
                count += self._count_arrays(item)
        elif isinstance(obj, dict):
            for value in obj.values():
                count += self._count_arrays(value)
        return count

    def _count_keys(self, obj: Any) -> int:
        """Count total number of keys."""
        count = 0
        if isinstance(obj, dict):
            count = len(obj)
            for value in obj.values():
                count += self._count_keys(value)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_keys(item)
        return count

    def _count_anchors_and_aliases(self, code: str) -> int:
        """Count YAML anchors (&) and aliases (*)."""
        anchors = len(re.findall(r'&\w+', code))
        aliases = len(re.findall(r'\*\w+', code))
        return anchors + aliases

    def _count_multiline_strings(self, code: str) -> int:
        """Count multi-line string blocks (|, >)."""
        return len(re.findall(r'[|>][-+]?\n', code))

    def _count_documents(self, code: str) -> int:
        """Count YAML document separators (---)."""
        return max(1, code.count('---'))


class ShellComplexityParser(ComplexityParser):
    """
    Parse and calculate cyclomatic complexity for shell scripts.

    Measures actual code complexity similar to McCabe:
    - Conditional statements (if, case)
    - Loops (for, while, until)
    - Functions
    - Logical operators (&&, ||)
    """

    def compute_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity for shell script."""
        if not code.strip():
            return 1

        complexity = 1  # Base complexity

        # Control flow statements
        complexity += len(re.findall(r'\bif\b', code))
        complexity += len(re.findall(r'\belif\b', code))
        complexity += len(re.findall(r'\bcase\b', code))

        # Loops
        complexity += len(re.findall(r'\bfor\b', code))
        complexity += len(re.findall(r'\bwhile\b', code))
        complexity += len(re.findall(r'\buntil\b', code))

        # Logical operators (short-circuit evaluation)
        complexity += len(re.findall(r'&&', code))
        complexity += len(re.findall(r'\|\|', code))

        # Test operators with multiple conditions
        complexity += len(re.findall(r'-a\b', code))  # AND in test
        complexity += len(re.findall(r'-o\b', code))  # OR in test

        return complexity

    def count_functions(self, code: str) -> int:
        """Count function definitions."""
        # Match: function name() { ... } or name() { ... }
        function_pattern = r'(?:function\s+)?(\w+)\s*\(\s*\)\s*\{'
        return len(re.findall(function_pattern, code))

    def analyze_functions(self, code: str) -> list[dict[str, any]]:
        """Analyze individual functions in shell script."""
        # For shell scripts, we don't have good function-level analysis yet
        # Just return basic function list
        function_pattern = r'(?:function\s+)?(\w+)\s*\(\s*\)\s*\{'
        functions = []
        for match in re.finditer(function_pattern, code):
            func_name = match.group(1)
            # Approximate complexity as 1 for now
            functions.append({'name': func_name, 'complexity': 1})
        return functions
