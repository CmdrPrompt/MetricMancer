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
    # Matches TypeScript function definitions including:
    # - 'async function' (async keyword)
    # - 'function name<T>' (generics)
    # - 'function name(x: Type)' (parameter type hints)
    # - 'function name(): ReturnType' (return type hints)
    # Pattern breakdown:
    # - '(?:async\s+)?' optionally matches async keyword
    # - 'function\s+' matches function keyword
    # - '([a-zA-Z_]\w*)' captures function name
    # - '(?:<[^>]+>)?' optionally matches generics <T>
    # - '\s*\(' matches opening parenthesis
    # - '[^)]*' matches parameters (non-greedy, stops at ))
    # - '\)' matches closing parenthesis
    # - '(?:\s*:\s*[^{]+)?' optionally matches return type hint ': Type'
    # - '\s*\{' matches opening brace
    FUNCTION_PATTERN = r'(?:async\s+)?function\s+([a-zA-Z_]\w*)(?:<[^>]+>)?\s*\([^)]*\)(?:\s*:\s*[^{]+)?\s*\{'
