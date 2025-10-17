import re
from src.languages.parsers.base import ComplexityParser


class TypeScriptComplexityParser(ComplexityParser):
    """
    Complexity parser for TypeScript source code.
    Computes cyclomatic complexity and counts functions using regex patterns.
    """

    def compute_complexity(self, code: str) -> int:
        """
        Compute the cyclomatic complexity of the given TypeScript code string.
        """
        complexity = 1
        for pattern in self.CONTROL_KEYWORDS:
            complexity += len(re.findall(pattern, code))
        return complexity
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b',
        r'\bswitch\b', r'\bcase\b', r'\bcatch\b', r'\bthrow\b',
        r'\breturn\b', r'&&', r'\|\|'
    ]
    FUNCTION_PATTERN = r'function\s+([a-zA-Z_]\w*)\s*\(.*?\)\s*\{'
