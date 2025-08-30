import re
from .base import ComplexityParser

class CComplexityParser(ComplexityParser):
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b', r'\bdo\b',
        r'\bswitch\b', r'\bcase\b', r'\bdefault\b', r'\bbreak\b', r'\bcontinue\b',
        r'\bgoto\b', r'\breturn\b', r'&&', r'\|\|'
    ]
    FUNCTION_PATTERN = r'\b\w+\s+\w+\s*\(.*?\)\s*\{'

    def compute_complexity(self, code: str) -> int:
        complexity = 1
        for pattern in self.CONTROL_KEYWORDS:
            complexity += len(re.findall(pattern, code))
        return complexity

    def count_functions(self, code: str) -> int:
        return len(re.findall(self.FUNCTION_PATTERN, code))
