import re
from .base import ComplexityParser

class JavaScriptComplexityParser(ComplexityParser):
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b',
        r'\bswitch\b', r'\bcase\b', r'\bcatch\b', r'\bthrow\b',
        r'\breturn\b', r'&&', r'\|\|'
    ]
    FUNCTION_PATTERN = r'function\s+\w+\s*\(.*?\)\s*\{'

    def compute_complexity(self, code: str) -> int:
        complexity = 1
        for pattern in self.CONTROL_KEYWORDS:
            complexity += len(re.findall(pattern, code))
        return complexity

    def count_functions(self, code: str) -> int:
        return len(re.findall(self.FUNCTION_PATTERN, code))
