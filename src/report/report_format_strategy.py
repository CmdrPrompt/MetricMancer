from abc import ABC, abstractmethod

class ReportFormatStrategy(ABC):
    """
    Abstract base class for different report formatting strategies (e.g., HTML, CLI, JSON).
    Subclasses should implement the reporting logic.
    """
    # This class no longer needs an __init__ or any methods,
    # it serves as a common type for all format strategies.
    pass
