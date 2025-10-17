"""
Complexity parsers for structured data files (JSON, YAML).

Measures structural complexity rather than cyclomatic complexity:
- Nesting depth
- Number of keys/objects
- Array complexity
- Configuration patterns
"""

import json
import yaml
import re
from typing import Any, Dict, List
from pathlib import Path


class JSONComplexityParser:
    """
    Parse and calculate structural complexity for JSON files.

    Complexity factors:
    - Max nesting depth (weight: 2)
    - Number of objects (weight: 1)
    - Number of arrays (weight: 1)
    - Total keys (weight: 0.1)
    - Array size variability
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None
        self._load_file()

    def _load_file(self):
        """Load and parse JSON file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {self.file_path}: {e}")
            self.data = {}

    def calculate_complexity(self) -> int:
        """Calculate overall complexity score."""
        if not self.data:
            return 0

        complexity = 0
        complexity += self._get_max_depth(self.data) * 2
        complexity += self._count_objects(self.data)
        complexity += self._count_arrays(self.data)
        complexity += self._count_keys(self.data) // 10

        return max(1, complexity)  # Minimum complexity of 1

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


class YAMLComplexityParser:
    """
    Parse and calculate structural complexity for YAML files.

    Similar to JSON but includes YAML-specific features:
    - Anchors and aliases
    - Multi-line strings
    - Document separators
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None
        self.raw_content = ""
        self._load_file()

    def _load_file(self):
        """Load and parse YAML file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.raw_content = f.read()
                f.seek(0)
                self.data = yaml.safe_load(f)
        except (yaml.YAMLError, FileNotFoundError) as e:
            print(f"Error loading {self.file_path}: {e}")
            self.data = {}

    def calculate_complexity(self) -> int:
        """Calculate overall complexity score."""
        if not self.data and not self.raw_content:
            return 0

        complexity = 0

        # Structural complexity (like JSON)
        if self.data:
            complexity += self._get_max_depth(self.data) * 2
            complexity += self._count_objects(self.data)
            complexity += self._count_arrays(self.data)
            complexity += self._count_keys(self.data) // 10

        # YAML-specific features
        complexity += self._count_anchors_and_aliases()
        complexity += self._count_multiline_strings()
        complexity += self._count_documents()

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

    def _count_anchors_and_aliases(self) -> int:
        """Count YAML anchors (&) and aliases (*)."""
        anchors = len(re.findall(r'&\w+', self.raw_content))
        aliases = len(re.findall(r'\*\w+', self.raw_content))
        return anchors + aliases

    def _count_multiline_strings(self) -> int:
        """Count multi-line string blocks (|, >)."""
        return len(re.findall(r'[|>][-+]?\n', self.raw_content))

    def _count_documents(self) -> int:
        """Count YAML document separators (---)."""
        return max(1, self.raw_content.count('---'))


class ShellComplexityParser:
    """
    Parse and calculate cyclomatic complexity for shell scripts.

    Measures actual code complexity similar to McCabe:
    - Conditional statements (if, case)
    - Loops (for, while, until)
    - Functions
    - Logical operators (&&, ||)
    - Command chaining
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self._load_file()

    def _load_file(self):
        """Load shell script content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
        except FileNotFoundError as e:
            print(f"Error loading {self.file_path}: {e}")
            self.content = ""

    def calculate_complexity(self) -> int:
        """Calculate cyclomatic complexity for shell script."""
        if not self.content:
            return 0

        complexity = 1  # Base complexity

        # Control flow statements
        complexity += self._count_pattern(r'\bif\b')
        complexity += self._count_pattern(r'\belif\b')
        complexity += self._count_pattern(r'\bcase\b')

        # Loops
        complexity += self._count_pattern(r'\bfor\b')
        complexity += self._count_pattern(r'\bwhile\b')
        complexity += self._count_pattern(r'\buntil\b')

        # Logical operators (short-circuit evaluation)
        complexity += self._count_pattern(r'&&')
        complexity += self._count_pattern(r'\|\|')

        # Functions
        complexity += self._count_functions()

        # Test operators with multiple conditions
        complexity += self._count_pattern(r'-a\b')  # AND in test
        complexity += self._count_pattern(r'-o\b')  # OR in test

        return complexity

    def _count_pattern(self, pattern: str) -> int:
        """Count occurrences of a regex pattern."""
        return len(re.findall(pattern, self.content))

    def _count_functions(self) -> int:
        """Count function definitions."""
        # Match: function name() { ... } or name() { ... }
        function_pattern = r'(?:function\s+)?(\w+)\s*\(\s*\)\s*\{'
        return len(re.findall(function_pattern, self.content))

    def get_functions(self) -> List[str]:
        """Extract function names."""
        function_pattern = r'(?:function\s+)?(\w+)\s*\(\s*\)\s*\{'
        return re.findall(function_pattern, self.content)
