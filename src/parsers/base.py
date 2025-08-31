
import re
from abc import ABC, abstractmethod


class ComplexityParser(ABC):
    @abstractmethod
    def compute_complexity(self, code: str) -> int:
        pass

    def count_functions(self, code: str) -> int:
        pattern = getattr(self, 'FUNCTION_PATTERN', None)
        if pattern:
            return len(re.findall(pattern, code))
        return 0
