"""
Coupling analysis module for temporal coupling detection.

This module provides functionality to analyze temporal coupling between files
based on commit history, following Adam Tornhill's methodology from
"Your Code as a Crime Scene".
"""

from .coupling_analyzer import CouplingAnalyzer, CouplingData
from .logical_coupling_kpi import LogicalCouplingKPI
from .change_coupled_hotspot_kpi import ChangeCoupledHotspotKPI

__all__ = [
    'CouplingAnalyzer',
    'CouplingData',
    'LogicalCouplingKPI',
    'ChangeCoupledHotspotKPI'
]
