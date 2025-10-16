"""
KPIOrchestrator - Orchestrates KPI calculations using Strategy Pattern.

This class follows the Strategy Pattern and Dependency Injection principles
by accepting KPI calculators and coordinating their execution. It separates
the orchestration logic from the actual KPI calculations.

Part of the Analyzer refactoring to reduce complexity from 121 to manageable levels.
"""
from typing import Dict, Any, Optional
from src.utilities.debug import debug_print


class KPIOrchestrator:
    """
    Orchestrates KPI calculations with dependency injection.
    
    This class implements the Strategy Pattern where different KPI calculators
    can be injected and executed uniformly. It handles the coordination of
    multiple KPI calculations while keeping the logic clean and testable.
    
    Responsibilities:
    - Store KPI calculator references
    - Execute KPI calculations with provided context
    - Handle calculator exceptions gracefully
    - Return dictionary of calculated KPIs
    
    Design Patterns:
    - Strategy Pattern: KPI calculators are interchangeable strategies
    - Dependency Injection: Calculators injected via constructor
    
    Example:
        >>> from src.kpis.complexity import ComplexityKPI
        >>> from src.kpis.codechurn import ChurnKPI
        >>> 
        >>> calculators = {
        ...     'complexity': ComplexityKPI(),
        ...     'churn': ChurnKPI()
        ... }
        >>> orchestrator = KPIOrchestrator(calculators)
        >>> 
        >>> file_context = {
        ...     'file_path': '/repo/src/file.py',
        ...     'complexity': 15,
        ...     'function_count': 3
        ... }
        >>> kpis = orchestrator.calculate_file_kpis(file_context)
        >>> print(f"Complexity KPI: {kpis['complexity'].value}")
    """
    
    def __init__(self, calculators: Optional[Dict[str, Any]] = None):
        """
        Initialize KPIOrchestrator with KPI calculators.
        
        Args:
            calculators: Dictionary mapping calculator names to calculator instances.
                        Each calculator should have a calculate(**kwargs) method
                        that returns a KPI object with 'name' and 'value' attributes.
                        Can be None, which results in an empty orchestrator.
        
        Example:
            >>> calculators = {
            ...     'complexity': ComplexityKPI(),
            ...     'churn': ChurnKPI()
            ... }
            >>> orchestrator = KPIOrchestrator(calculators)
        """
        self.calculators = calculators if calculators is not None else {}
    
    def calculate_file_kpis(self, file_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all KPIs for a file using provided context.
        
        Iterates through all registered calculators and invokes their calculate()
        method with the file context. Returns a dictionary where keys are KPI names
        (from the KPI object's 'name' attribute) and values are the KPI objects.
        
        Handles exceptions gracefully - if a calculator fails, it logs the error
        and continues with other calculators.
        
        Args:
            file_context: Dictionary containing context for KPI calculation.
                         Typical keys include:
                         - file_path: str - Path to the file
                         - repo_root: str - Repository root path
                         - complexity: int - File complexity
                         - function_count: int - Number of functions
                         - content: str - File content (optional)
        
        Returns:
            Dictionary mapping KPI names to KPI objects.
            Keys are the 'name' attribute from each KPI object.
            Empty dict if no calculators or all calculators fail.
        
        Example:
            >>> file_context = {
            ...     'file_path': '/repo/src/main.py',
            ...     'complexity': 25,
            ...     'function_count': 5
            ... }
            >>> kpis = orchestrator.calculate_file_kpis(file_context)
            >>> for name, kpi in kpis.items():
            ...     print(f"{name}: {kpi.value}")
        """
        kpis = {}
        
        for calculator_name, calculator in self.calculators.items():
            try:
                # Call the calculator's calculate method with the file context
                kpi = calculator.calculate(**file_context)
                
                # Use the KPI's name attribute as the key
                # This allows for flexible naming (calculator key != KPI name)
                kpis[kpi.name] = kpi
                
                debug_print(f"[KPIOrchestrator] Calculated {kpi.name}: {kpi.value}")
                
            except Exception as e:
                # Log error but continue with other calculators
                # This makes the orchestrator resilient to individual calculator failures
                debug_print(
                    f"[KPIOrchestrator] Error calculating KPI '{calculator_name}': {e}"
                )
                # Don't add failed KPI to results
                continue
        
        return kpis
