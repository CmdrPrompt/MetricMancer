from typing import Any, Optional, Dict
from abc import ABC, abstractmethod


class BaseKPI(ABC):
    """
    Base class for all KPIs. Contains metadata, result, and calculation logic.
    """
    name: str
    value: Any
    unit: Optional[str]
    description: Optional[str]
    calculation_values: Optional[Dict[str, Any]]

    def __init__(self, name: str, value: Any = None, unit: Optional[str] = None, description: Optional[str] = None, calculation_values: Optional[Dict[str, Any]] = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.description = description
        self.calculation_values = calculation_values or {}

    @abstractmethod
    def calculate(self, *args, **kwargs):
        """
        To be implemented in subclass: Calculates and sets self.value and possibly self.calculation_values.
        """
        pass