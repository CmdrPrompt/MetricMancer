"""
MetricMancer application module.

This module provides backward compatibility exports for the restructured codebase.
All imports that previously worked from src.app.* will continue to work.

New structure (2024-10-16):
- core/: Analysis engine (Analyzer)
- scanning/: File system scanning (Scanner)
- hierarchy/: Data modeling (HierarchyBuilder, DataConverter)
- kpi/: KPI operations (KPICalculator, KPIAggregator, FileAnalyzer)
- coordination/: Cross-cutting coordination (Hotspot, Report, Review)
- infrastructure/: Infrastructure (TimingReporter, Collector)

Backward compatibility: All old imports still work via these exports.
"""

# Core modules
from src.app.core.analyzer import Analyzer, AggregatedSharedOwnershipKPI

# Scanning
from src.app.scanning.scanner import Scanner

# Hierarchy
from src.app.hierarchy.hierarchy_builder import HierarchyBuilder
from src.app.hierarchy.data_converter import DataConverter

# KPI
from src.app.kpi.kpi_calculator import KPICalculator
from src.app.kpi.kpi_aggregator import KPIAggregator
from src.app.kpi.file_analyzer import FileAnalyzer

# Coordination
from src.app.coordination.hotspot_coordinator import HotspotCoordinator
from src.app.coordination.report_coordinator import ReportCoordinator
from src.app.coordination.review_coordinator import ReviewCoordinator

# Infrastructure
# timing_reporter and collector are modules, not classes

# Main app
from src.app.metric_mancer_app import MetricMancerApp

__all__ = [
    # Core
    'Analyzer',
    'AggregatedSharedOwnershipKPI',
    # Scanning
    'Scanner',
    # Hierarchy
    'HierarchyBuilder',
    'DataConverter',
    # KPI
    'KPICalculator',
    'KPIAggregator',
    'FileAnalyzer',
    # Coordination
    'HotspotCoordinator',
    'ReportCoordinator',
    'ReviewCoordinator',
    # Main
    'MetricMancerApp',
]
