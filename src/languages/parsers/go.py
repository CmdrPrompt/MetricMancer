import re
from src.languages.parsers.base import ComplexityParser


class GoComplexityParser(ComplexityParser):
    """
    Complexity parser for Go source code.
    Computes cyclomatic complexity and counts functions using regex patterns.
    """

    def compute_complexity(self, code: str) -> int:
        """
        Compute the cyclomatic complexity of the given Go code string.
        """
        complexity = 1
        for pattern in self.CONTROL_KEYWORDS:
            complexity += len(re.findall(pattern, code))
        return complexity
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bswitch\b', r'\bcase\b',
        r'\bselect\b', r'\bgo\b', r'\bdefer\b', r'\breturn\b', r'&&', r'\|\|'
    ]
    # Matches Go function definitions including:
    # - 'func name()' (standard functions)
    # - 'func (r *Receiver) name()' (methods with receivers)
    # - 'func name() returnType' (with return type)
    # - 'func name() (Type, error)' (multiple return values)
    # Pattern breakdown:
    # - 'func\s+' matches func keyword
    # - '(?:\([^)]*\)\s+)?' optionally matches receiver (r *Type)
    # - '([a-zA-Z_]\w*)' captures function name
    # - '\s*\(' matches opening parenthesis
    # - '[^)]*' matches parameters
    # - '\)' matches closing parenthesis
    # - '(?:\s+[^{]+)?' optionally matches return type(s)
    # - '\s*\{' matches opening brace
    FUNCTION_PATTERN = r'func\s+(?:\([^)]*\)\s+)?([a-zA-Z_]\w*)\s*\([^)]*\)(?:\s+[^{]+)?\s*\{'
