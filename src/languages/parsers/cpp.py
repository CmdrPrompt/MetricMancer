import re
from src.languages.parsers.base import ComplexityParser

class CppComplexityParser(ComplexityParser):
    """
    Complexity parser for C++ source code.
    Computes cyclomatic complexity and counts functions using regex patterns.
    """
    def compute_complexity(self, code: str) -> int:
        """
        Compute the cyclomatic complexity of the given C++ code string.
        """
        complexity = 1
        for pattern in self.CONTROL_KEYWORDS:
            complexity += len(re.findall(pattern, code))
        return complexity
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b', r'\bdo\b',
        r'\bswitch\b', r'\bcase\b', r'\bdefault\b', r'\bbreak\b', r'\bcontinue\b',
        r'\bgoto\b', r'\breturn\b', r'&&', r'\|\|'
    ]
	FUNCTION_PATTERN = r'(?:\b\w+\s+)+([a-zA-Z_]\w*)\s*\(.*?\)\s*\{'
