
import re
from abc import ABC, abstractmethod

class ComplexityParser(ABC):
    def compute_complexity(self, code: str) -> int:
        complexity = 1
        for pattern in getattr(self, 'CONTROL_KEYWORDS', []):
            complexity += len(re.findall(pattern, code))
        return complexity

    def count_functions(self, code: str) -> int:
        pattern = getattr(self, 'FUNCTION_PATTERN', None)
        if pattern:
            return len(re.findall(pattern, code))
        return 0
