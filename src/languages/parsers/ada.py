import re
from src.languages.parsers.base import ComplexityParser


class AdaComplexityParser(ComplexityParser):
    def compute_complexity(self, code: str) -> int:
        complexity = 1
        for pattern in self.CONTROL_KEYWORDS:
            complexity += len(re.findall(pattern, code))
        return complexity
    CONTROL_KEYWORDS = [
        r'\bif(?!\s*;)\b', r'\belsif\b', r'\bcase\b', r'\bwhen\b',
        r'\bloop\b', r'\bwhile\b', r'\bfor\b', r'\bexit\b', r'\bexception\b'
    ]
    # Matches Ada function definitions including:
    # - 'function Name return Boolean is' (no parameters)
    # - 'function Add (X : Integer; Y : Integer) return Integer is' (with parameters)
    # - 'function Get_Name return String is' (simple return)
    # Pattern breakdown:
    # - '\bfunction\s+' matches function keyword
    # - '([a-zA-Z_]\w*)' captures function name
    # - '(?:\s*\([^)]*\))?' optionally matches parameters (X : Type; Y : Type)
    # - '\s+return\s+' matches return keyword
    # - '\w+' matches return type
    # - '\s+is\b' matches is keyword
    FUNCTION_PATTERN = r'\bfunction\s+([a-zA-Z_]\w*)(?:\s*\([^)]*\))?\s+return\s+\w+\s+is\b'
