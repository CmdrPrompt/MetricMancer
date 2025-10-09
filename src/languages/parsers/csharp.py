import re
from src.languages.parsers.base import ComplexityParser

class CSharpComplexityParser(ComplexityParser):
    """
    Complexity parser for C# source code.
    Computes cyclomatic complexity and counts functions using regex patterns.
    """
    def compute_complexity(self, code: str) -> int:
        """
        Compute the cyclomatic complexity of the given C# code string.
        """
        complexity = 1
        for pattern in self.CONTROL_KEYWORDS:
            complexity += len(re.findall(pattern, code))
        return complexity
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\bswitch\b',
        r'\bcase\b', r'\bcatch\b', r'\bthrow\b', r'\breturn\b',
        r'&&', r'\|\|'
    ]
	FUNCTION_PATTERN = r'(?:public|private|protected)?\s+\w+\s+([a-zA-Z_]\w*)\s*\(.*?\)\s*\{'
