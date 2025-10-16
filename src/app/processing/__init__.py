"""
Processing package - File and data processing operations.

This package contains classes responsible for processing files and data
during the analysis workflow. It follows the Single Responsibility Principle
by focusing solely on data processing and transformation operations.

Components:
-----------
RepositoryGrouper: Groups files by repository root
KPIOrchestrator: Orchestrates KPI calculations (Phase 2)
FileProcessor: Processes individual files (Phase 2)
KPIAggregator: Aggregates KPIs across hierarchy (Phase 2)

Part of the Analyzer refactoring to reduce complexity and improve modularity.
"""

from .repository_grouper import RepositoryGrouper

__all__ = [
    'RepositoryGrouper',
]
