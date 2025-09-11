from abc import ABC, abstractmethod

class ReportFormatStrategy(ABC):
    @abstractmethod
    def print_report(self, repo_info, debug_print):
        pass
