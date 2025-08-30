import re
from .base import ComplexityParser

class PythonComplexityParser(ComplexityParser):
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
        r'\btry\b', r'\bexcept\b', r'\breturn\b', r'\band\b', r'\bor\b'
    ]
    FUNCTION_PATTERN = r'def\s+\w+\s*\(.*?\)\s*:'

    def compute_complexity(self, code: str) -> int:
        complexity = 1
        for pattern in self.CONTROL_KEYWORDS:
            complexity += len(re.findall(pattern, code))
        return complexity

    def count_functions(self, code: str) -> int:
        return len(re.findall(self.FUNCTION_PATTERN, code))
