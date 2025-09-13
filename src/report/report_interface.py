from abc import ABC, abstractmethod

class ReportInterface(ABC):
    """
    Abstract base class for all report generators.
    Defines the interface for generating reports from analysis results.
    """
    @abstractmethod
    def generate(self, results, **kwargs):
        """
        Generate a report from results. Should be implemented by all report generators.
        Args:
            results: The analysis results or data model to report on.
            **kwargs: Additional arguments for report generation.
        """
        pass
