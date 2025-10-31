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
    # Matches C# method definitions including:
    # - 'public void Method()' (with visibility modifier)
    # - 'async Task<int> ProcessAsync()' (async with generics)
    # - 'List<string> GetItems()' (generics in return type)
    # - 'void Process() where T : class' (with constraints)
    # Pattern breakdown:
    # - '(?:(?:public|private|protected|static|async|virtual|override)\s+)*' matches modifiers
    # - '(?:\w+(?:<[^>]+>)?)+' matches return type (including generics like Task<T>)
    # - '\s+([a-zA-Z_]\w*)' captures method name
    # - '\s*\(' matches opening parenthesis
    # - '[^)]*' matches parameters
    # - '\)' matches closing parenthesis
    # - '(?:\s+where\s+[^{]+)?' optionally matches generic constraints
    # - '\s*\{' matches opening brace
    FUNCTION_PATTERN = (
        r'(?:(?:public|private|protected|static|async|virtual|override)\s+)*'
        r'(?:\w+(?:<[^>]+>)?)+\s+([a-zA-Z_]\w*)\s*\([^)]*\)'
        r'(?:\s+where\s+[^{]+)?\s*\{'
    )
