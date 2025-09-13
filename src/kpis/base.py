from typing import Any, Optional, Dict

class KPI:
    """
    Bas-klass för alla KPI:er. Innehåller metadata, resultat och beräkningslogik.
    """
    name: str
    value: Any
    unit: Optional[str]
    description: Optional[str]
    meta: Optional[Dict[str, Any]]

    def __init__(self, name: str, value: Any = None, unit: Optional[str] = None, description: Optional[str] = None, meta: Optional[Dict[str, Any]] = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.description = description
        self.meta = meta or {}

    def calculate(self, *args, **kwargs):
        """Implementeras i subklass: Beräknar och sätter self.value och ev. self.meta."""
        raise NotImplementedError
