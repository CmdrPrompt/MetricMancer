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
    # Matches C++ function definitions including:
    # - 'int main()' (simple function)
    # - 'void MyClass::method()' (class method)
    # - 'template<typename T> T getValue()' (template function)
    # - 'virtual void process() override' (virtual with override)
    # Pattern breakdown:
    # - '(?:template<[^>]+>\s+)?' optionally matches template declaration
    # - '(?:\b\w+\s+)+' matches return type and modifiers (virtual, static, etc.)
    # - '(?:\w+::)*' optionally matches class scope (MyClass::)
    # - '([a-zA-Z_]\w*)' captures function name
    # - '\s*\(' matches opening parenthesis
    # - '[^)]*' matches parameters
    # - '\)' matches closing parenthesis
    # - '(?:\s+(?:const|override|final|noexcept))*' optionally matches trailing qualifiers
    # - '\s*\{' matches opening brace
    FUNCTION_PATTERN = (
        r'(?:template<[^>]+>\s+)?(?:\b\w+\s+)+(?:\w+::)*([a-zA-Z_]\w*)\s*'
        r'\([^)]*\)(?:\s+(?:const|override|final|noexcept))*\s*\{'
    )
