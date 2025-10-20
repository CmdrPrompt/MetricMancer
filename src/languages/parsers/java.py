import re
from src.languages.parsers.base import ComplexityParser


class JavaComplexityParser(ComplexityParser):
    """
    Complexity parser for Java source code.
    Computes cyclomatic complexity and counts functions using regex patterns.
    """

    def compute_complexity(self, code: str) -> int:
        """
        Compute the cyclomatic complexity of the given Java code string.
        """
        complexity = 1
        for pattern in self.CONTROL_KEYWORDS:
            complexity += len(re.findall(pattern, code))
        return complexity
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\bswitch\b',
        r'\bcase\b', r'\bcatch\b', r'\bthrow\b', r'\breturn\b',
        r'&&', r'\|\|'
    ]
    # Matches Java method definitions including:
    # - 'public void method()' (with visibility modifier)
    # - 'int calculate()' (without modifier)
    # - 'List<String> getItems()' (generics in return type)
    # - 'void process() throws Exception' (with throws clause)
    # Pattern breakdown:
    # - '(?:public|private|protected|static|final)?' optionally matches modifiers
    # - '\s+(?:\w+(?:<[^>]+>)?)+' matches return type (including generics)
    # - '\s+([a-zA-Z_]\w*)' captures method name
    # - '\s*\(' matches opening parenthesis
    # - '[^)]*' matches parameters
    # - '\)' matches closing parenthesis
    # - '(?:\s+throws\s+[^{]+)?' optionally matches throws clause
    # - '\s*\{' matches opening brace
    FUNCTION_PATTERN = r'(?:(?:public|private|protected|static|final)\s+)*(?:\w+(?:<[^>]+>)?)+\s+([a-zA-Z_]\w*)\s*\([^)]*\)(?:\s+throws\s+[^{]+)?\s*\{'
