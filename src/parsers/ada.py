import re
from .base import ComplexityParser

class AdaComplexityParser(ComplexityParser):
    CONTROL_KEYWORDS = [
        r'\bif(?!\s*;)\b', r'\belsif\b', r'\bcase\b', r'\bwhen\b',
        r'\bloop\b', r'\bwhile\b', r'\bfor\b', r'\bexit\b', r'\bexception\b'
    ]

    def compute_complexity(self, code: str) -> int:
        complexity = 1
        code = re.sub(r'end if;', '', code, flags=re.IGNORECASE)  # Remove 'end if;' before matching
        for pattern in self.CONTROL_KEYWORDS:
            matches = re.findall(pattern, code, re.IGNORECASE)
            complexity += len(matches)
        return complexity
