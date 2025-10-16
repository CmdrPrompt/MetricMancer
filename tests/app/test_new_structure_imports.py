"""
RED Phase: Test new app structure imports.

These tests will FAIL initially because the new structure doesn't exist yet.
Once we create the new structure and move files, these tests will PASS.

TDD Approach:
1. RED: Write tests expecting new import paths (will fail)
2. GREEN: Create new structure and move files (tests will pass)
3. REFACTOR: Ensure all existing tests still pass
"""

import pytest


class TestCoreModuleImports:
    """Test imports from src.app.core/"""
    
    def test_can_import_analyzer_from_core(self):
        """Should be able to import Analyzer from core module."""
        from src.app.core.analyzer import Analyzer
        assert Analyzer is not None
    
    def test_can_import_file_processor_from_core(self):
        """Should be able to import FileProcessor from core module."""
        from src.app.core.file_processor import FileProcessor
        assert FileProcessor is not None


class TestScanningModuleImports:
    """Test imports from src.app.scanning/"""
    
    def test_can_import_scanner_from_scanning(self):
        """Should be able to import Scanner from scanning module."""
        from src.app.scanning.scanner import Scanner
        assert Scanner is not None


class TestHierarchyModuleImports:
    """Test imports from src.app.hierarchy/"""
    
    def test_can_import_hierarchy_builder(self):
        """Should be able to import HierarchyBuilder from hierarchy module."""
        from src.app.hierarchy.hierarchy_builder import HierarchyBuilder
        assert HierarchyBuilder is not None
    
    def test_can_import_data_converter(self):
        """Should be able to import from data_converter."""
        from src.app.hierarchy import data_converter
        assert data_converter is not None


class TestKPIModuleImports:
    """Test imports from src.app.kpi/"""
    
    def test_can_import_kpi_calculator(self):
        """Should be able to import KPICalculator from kpi module."""
        from src.app.kpi.kpi_calculator import KPICalculator
        assert KPICalculator is not None
    
    def test_can_import_kpi_aggregator(self):
        """Should be able to import KPIAggregator from kpi module."""
        from src.app.kpi.kpi_aggregator import KPIAggregator
        assert KPIAggregator is not None
    
    def test_can_import_file_analyzer(self):
        """Should be able to import from file_analyzer."""
        from src.app.kpi import file_analyzer
        assert file_analyzer is not None


class TestCoordinationModuleImports:
    """Test imports from src.app.coordination/"""
    
    def test_can_import_hotspot_coordinator(self):
        """Should be able to import HotspotCoordinator."""
        from src.app.coordination.hotspot_coordinator import HotspotCoordinator
        assert HotspotCoordinator is not None
    
    def test_can_import_report_coordinator(self):
        """Should be able to import ReportCoordinator."""
        from src.app.coordination.report_coordinator import ReportCoordinator
        assert ReportCoordinator is not None
    
    def test_can_import_review_coordinator(self):
        """Should be able to import ReviewCoordinator."""
        from src.app.coordination.review_coordinator import ReviewCoordinator
        assert ReviewCoordinator is not None


class TestInfrastructureModuleImports:
    """Test imports from src.app.infrastructure/"""
    
    def test_can_import_timing_reporter(self):
        """Should be able to import from timing_reporter."""
        from src.app.infrastructure import timing_reporter
        assert timing_reporter is not None
    
    def test_can_import_collector(self):
        """Should be able to import from collector."""
        from src.app.infrastructure import collector
        assert collector is not None


class TestBackwardCompatibility:
    """Test that old imports still work via __init__.py exports."""
    
    def test_analyzer_accessible_from_app_root(self):
        """Old code should still work: from src.app.analyzer import Analyzer"""
        # This will be maintained via __init__.py exports
        from src.app import Analyzer
        assert Analyzer is not None
    
    def test_file_processor_accessible_from_app_root(self):
        """Old code should still work: from src.app.file_processor import FileProcessor"""
        from src.app import FileProcessor
        assert FileProcessor is not None
    
    def test_scanner_accessible_from_app_root(self):
        """Old code should still work: from src.app.scanner import Scanner"""
        from src.app import Scanner
        assert Scanner is not None
    
    def test_kpi_aggregator_accessible_from_app_root(self):
        """Old code should still work: from src.app.kpi_aggregator import KPIAggregator"""
        from src.app import KPIAggregator
        assert KPIAggregator is not None
