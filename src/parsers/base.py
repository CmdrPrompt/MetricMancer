from abc import ABC, abstractmethod

class ComplexityParser(ABC):
    @abstractmethod
    def compute_complexity(self, code: str) -> int:
        pass
