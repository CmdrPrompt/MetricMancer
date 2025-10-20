import re
from src.languages.parsers.base import ComplexityParser


class JavaScriptComplexityParser(ComplexityParser):
    """
    Complexity parser for JavaScript source code.
    Computes cyclomatic complexity and counts functions using regex patterns.
    """

    def compute_complexity(self, code: str) -> int:
        """
        Compute the cyclomatic complexity of the given JavaScript code string.
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
    # Matches JavaScript function definitions including:
    # - 'async function' (async keyword)
    # - 'function name()' (standard functions)
    # Pattern breakdown:
    # - '(?:async\s+)?' optionally matches async keyword
    # - 'function\s+' matches function keyword
    # - '([a-zA-Z_]\w*)' captures function name
    # - '\s*\(' matches opening parenthesis
    # - '[^)]*' matches parameters (stops at ))
    # - '\)\s*\{' matches closing parenthesis and opening brace
    FUNCTION_PATTERN = r'(?:async\s+)?function\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{'
