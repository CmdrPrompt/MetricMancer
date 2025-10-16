"""
KPI Calculator - Strategy Pattern for KPI Calculation

Follows Open/Closed Principle: Add new KPIs without modifying core.
Based on MetricMancer ARCHITECTURE.md design principles.

This module implements the Strategy pattern for calculating KPIs,
allowing easy extension with new KPI types without modifying existing code.
"""
from typing import Dict, List, Protocol
from pathlib import Path
import time

from src.kpis.base_kpi import BaseKPI
from src.utilities.debug import debug_print


class KPIStrategy(Protocol):
    """
    Protocol for KPI calculation strategies.

    Each strategy implements a calculate() method that takes file information
    and returns a calculated KPI object.
    """

    def calculate(
        self,
        file_info: Dict,
        repo_root: Path,
        **kwargs
    ) -> BaseKPI:
        """
        Calculate KPI for a file.

        Args:
            file_info: Dict with 'path' and 'ext' keys
            repo_root: Path to repository root
            **kwargs: Additional context-specific parameters

        Returns:
            Calculated BaseKPI object
        """
        ...


class ComplexityKPIStrategy:
    """Strategy for calculating complexity KPI from function analysis."""

    def __init__(self, complexity_analyzer):
        """
        Initialize with a complexity analyzer.

        Args:
            complexity_analyzer: ComplexityAnalyzer instance
        """
        self.analyzer = complexity_analyzer

    def calculate(
        self,
        file_info: Dict,
        repo_root: Path,
        content: str = None,
        functions_data: List = None,
        **kwargs
    ) -> BaseKPI:
        """
        Calculate complexity from functions data.

        Args:
            file_info: File information dict
            repo_root: Repository root path
            content: File content (unused, for consistency)
            functions_data: List of function dicts with complexity values
            **kwargs: Additional parameters

        Returns:
            ComplexityKPI with aggregated file complexity
        """
        from src.kpis.complexity import ComplexityKPI

        if not functions_data:
            return ComplexityKPI().calculate(complexity=0, function_count=0)

        total_complexity = sum(
            f.get('complexity', 0) for f in functions_data
        )

        return ComplexityKPI().calculate(
            complexity=total_complexity,
            function_count=len(functions_data)
        )


class ChurnKPIStrategy:
    """Strategy for calculating churn KPI using git cache."""

    def calculate(
        self,
        file_info: Dict,
        repo_root: Path,
        **kwargs
    ) -> BaseKPI:
        """
        Calculate churn using git cache.

        Args:
            file_info: File information dict with 'path' key
            repo_root: Repository root path
            **kwargs: Additional parameters

        Returns:
            ChurnKPI with commit frequency value
        """
        from src.kpis.codechurn import ChurnKPI

        file_path = file_info.get('path')

        return ChurnKPI().calculate(
            file_path=str(file_path),
            repo_root=str(repo_root.resolve())
        )


class HotspotKPIStrategy:
    """Strategy for calculating hotspot KPI from complexity and churn."""

    def calculate(
        self,
        file_info: Dict,
        repo_root: Path,
        complexity_kpi: BaseKPI = None,
        churn_kpi: BaseKPI = None,
        **kwargs
    ) -> BaseKPI:
        """
        Calculate hotspot from complexity and churn.

        Hotspot = Complexity × Churn (Adam Tornhill's methodology)

        Args:
            file_info: File information dict
            repo_root: Repository root path
            complexity_kpi: Already calculated ComplexityKPI
            churn_kpi: Already calculated ChurnKPI
            **kwargs: Additional parameters

        Returns:
            HotspotKPI with computed score
        """
        from src.kpis.hotspot import HotspotKPI

        complexity_value = complexity_kpi.value if complexity_kpi else 0
        churn_value = churn_kpi.value if churn_kpi else 0

        return HotspotKPI().calculate(
            complexity=complexity_value,
            churn=churn_value
        )


class OwnershipKPIStrategy:
    """Strategy for calculating code ownership KPI."""

    def calculate(
        self,
        file_info: Dict,
        repo_root: Path,
        **kwargs
    ) -> BaseKPI:
        """
        Calculate code ownership using git blame.

        Args:
            file_info: File information dict with 'path' key
            repo_root: Repository root path
            **kwargs: Additional parameters

        Returns:
            CodeOwnershipKPI or FallbackCodeOwnershipKPI on error
        """
        from src.kpis.codeownership import CodeOwnershipKPI
        from src.kpis.codeownership.fallback_kpi import FallbackCodeOwnershipKPI

        file_path = file_info.get('path')

        try:
            return CodeOwnershipKPI(
                file_path=str(Path(file_path).resolve()),
                repo_root=str(repo_root.resolve())
            )
        except Exception as e:
            debug_print(f"[WARN] Ownership calc failed for {file_path}: {e}")
            return FallbackCodeOwnershipKPI(str(e))


class SharedOwnershipKPIStrategy:
    """Strategy for calculating shared ownership KPI."""

    def calculate(
        self,
        file_info: Dict,
        repo_root: Path,
        **kwargs
    ) -> BaseKPI:
        """
        Calculate shared ownership (number of significant contributors).

        Args:
            file_info: File information dict with 'path' key
            repo_root: Repository root path
            **kwargs: Additional parameters

        Returns:
            SharedOwnershipKPI or FallbackSharedOwnershipKPI on error
        """
        from src.kpis.sharedcodeownership.shared_code_ownership import (
            SharedOwnershipKPI
        )
        from src.kpis.sharedcodeownership.fallback_kpi import (
            FallbackSharedOwnershipKPI
        )

        file_path = file_info.get('path')

        try:
            return SharedOwnershipKPI(
                file_path=str(Path(file_path).resolve()),
                repo_root=str(repo_root.resolve())
            )
        except Exception as e:
            debug_print(f"[WARN] Shared ownership calc failed for {file_path}: {e}")
            return FallbackSharedOwnershipKPI(str(e))


class KPICalculator:
    """
    Orchestrates KPI calculation using registered strategies.

    Follows Open/Closed Principle:
    - Open for extension: Register new strategies via register_strategy()
    - Closed for modification: Core logic (calculate_all) unchanged

    Usage:
        calculator = KPICalculator(complexity_analyzer)
        kpis = calculator.calculate_all(file_info, repo_root, content, functions_data)

        # Add custom KPI
        calculator.register_strategy('my_kpi', MyKPIStrategy())
    """

    def __init__(self, complexity_analyzer):
        """
        Initialize with default KPI strategies.

        Args:
            complexity_analyzer: ComplexityAnalyzer instance for parsing code
        """
        self.complexity_analyzer = complexity_analyzer

        # Register default strategies
        self.strategies = {
            'complexity': ComplexityKPIStrategy(complexity_analyzer),
            'churn': ChurnKPIStrategy(),
            'hotspot': HotspotKPIStrategy(),
            'ownership': OwnershipKPIStrategy(),
            'shared_ownership': SharedOwnershipKPIStrategy()
        }

        # Timing tracker for performance profiling
        self.timing = {name: 0.0 for name in self.strategies.keys()}

    def register_strategy(self, name: str, strategy: KPIStrategy):
        """
        Register a new KPI calculation strategy.

        This allows extending the calculator with new KPI types
        without modifying the core calculate_all() logic.

        Args:
            name: Identifier for the strategy (e.g., 'my_custom_kpi')
            strategy: Strategy object implementing calculate() method

        Example:
            calculator.register_strategy('technical_debt', TechnicalDebtStrategy())
        """
        self.strategies[name] = strategy
        self.timing[name] = 0.0
        debug_print(f"[KPICalculator] Registered strategy: {name}")

    def calculate_all(
        self,
        file_info: Dict,
        repo_root: Path,
        content: str,
        functions_data: List
    ) -> Dict[str, BaseKPI]:
        """
        Calculate all registered KPIs for a file.

        This method orchestrates the calculation of all KPIs in the correct order,
        handling dependencies between KPIs (e.g., hotspot needs complexity + churn).

        Args:
            file_info: Dict with 'path' and 'ext' keys
            repo_root: Path to repository root
            content: File content as string
            functions_data: List of function dicts from complexity analysis

        Returns:
            Dict mapping KPI names to calculated KPI objects

        Example:
            kpis = calculator.calculate_all(
                file_info={'path': 'src/main.py', 'ext': 'py'},
                repo_root=Path('/repo'),
                content=file_content,
                functions_data=[{'name': 'main', 'complexity': 5}]
            )
            # kpis = {
            #     'complexity': ComplexityKPI(value=5),
            #     'churn': ChurnKPI(value=12),
            #     'hotspot': HotspotKPI(value=60),
            #     ...
            # }
        """
        kpis = {}

        # 1. Complexity (independent - needs only functions_data)
        t_start = time.perf_counter()
        complexity_kpi = self.strategies['complexity'].calculate(
            file_info=file_info,
            repo_root=repo_root,
            content=content,
            functions_data=functions_data
        )
        kpis[complexity_kpi.name] = complexity_kpi
        self.timing['complexity'] += time.perf_counter() - t_start

        # 2. Churn (independent - queries git)
        t_start = time.perf_counter()
        churn_kpi = self.strategies['churn'].calculate(
            file_info=file_info,
            repo_root=repo_root
        )
        kpis[churn_kpi.name] = churn_kpi
        self.timing['churn'] += time.perf_counter() - t_start

        # 3. Hotspot (depends on complexity + churn)
        t_start = time.perf_counter()
        hotspot_kpi = self.strategies['hotspot'].calculate(
            file_info=file_info,
            repo_root=repo_root,
            complexity_kpi=complexity_kpi,
            churn_kpi=churn_kpi
        )
        kpis[hotspot_kpi.name] = hotspot_kpi
        self.timing['hotspot'] += time.perf_counter() - t_start

        # 4. Ownership (independent - queries git blame)
        t_start = time.perf_counter()
        ownership_kpi = self.strategies['ownership'].calculate(
            file_info=file_info,
            repo_root=repo_root
        )
        kpis[ownership_kpi.name] = ownership_kpi
        self.timing['ownership'] += time.perf_counter() - t_start

        # 5. Shared Ownership (independent - queries git)
        t_start = time.perf_counter()
        shared_kpi = self.strategies['shared_ownership'].calculate(
            file_info=file_info,
            repo_root=repo_root
        )
        kpis[shared_kpi.name] = shared_kpi
        self.timing['shared_ownership'] += time.perf_counter() - t_start

        return kpis

    def get_timing_report(self) -> Dict[str, float]:
        """
        Get timing statistics for KPI calculations.

        Useful for performance profiling and identifying slow KPIs.

        Returns:
            Dict mapping KPI names to cumulative time in seconds

        Example:
            timing = calculator.get_timing_report()
            # {'complexity': 0.123, 'churn': 2.456, 'hotspot': 0.001, ...}
        """
        return self.timing.copy()

    def reset_timing(self):
        """Reset all timing counters to zero."""
        for key in self.timing:
            self.timing[key] = 0.0
