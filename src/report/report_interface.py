from abc import ABC, abstractmethod

class ReportInterface(ABC):
    @abstractmethod
    def generate(self, results, **kwargs):
        """Generate a report from results. Should be implemented by all report generators."""
        pass
