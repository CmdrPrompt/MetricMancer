"""
Tests for LogicalCouplingKPI.

Tests logical coupling KPI that measures temporal coupling for a file.
"""

import pytest
from src.kpis.coupling.logical_coupling_kpi import LogicalCouplingKPI


class TestLogicalCouplingKPIBasics:
    """Test basic LogicalCouplingKPI functionality."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        kpi = LogicalCouplingKPI()
        assert kpi.name == "logical_coupling"
        assert kpi.value is None
        assert kpi.unit == "coupled_files"
        assert kpi.description == "Number of files with strong coupling (>50%)"
        assert kpi.calculation_values == {}

    def test_init_with_values(self):
        """Test initialization with explicit values."""
        calc_values = {"count": 3, "coupled_files": []}
        kpi = LogicalCouplingKPI(value=3, calculation_values=calc_values)
        assert kpi.value == 3
        assert kpi.calculation_values == calc_values

    def test_calculate_no_coupling(self):
        """Test calculation with no coupling data."""
        kpi = LogicalCouplingKPI()
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=[]
        )
        
        assert result is kpi  # Should return self for chaining
        assert kpi.value == 0
        assert kpi.calculation_values["coupled_files"] == []
        assert kpi.calculation_values["max_coupling"] == 0.0
        assert kpi.calculation_values["avg_coupling"] == 0.0

    def test_calculate_single_weak_coupling(self):
        """Test calculation with single weak coupling (< 0.5)."""
        kpi = LogicalCouplingKPI()
        coupling_data = [("src/other.py", 0.4)]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data
        )
        
        assert kpi.value == 0  # Only count strong couplings (>= 0.5)
        assert kpi.calculation_values["coupled_files"] == coupling_data
        assert kpi.calculation_values["max_coupling"] == 0.4
        assert kpi.calculation_values["avg_coupling"] == 0.4

    def test_calculate_single_strong_coupling(self):
        """Test calculation with single strong coupling (>= 0.5)."""
        kpi = LogicalCouplingKPI()
        coupling_data = [("src/other.py", 0.75)]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data
        )
        
        assert kpi.value == 1  # One strong coupling
        assert kpi.calculation_values["coupled_files"] == coupling_data
        assert kpi.calculation_values["max_coupling"] == 0.75
        assert kpi.calculation_values["avg_coupling"] == 0.75

    def test_calculate_multiple_couplings(self):
        """Test calculation with multiple coupling relationships."""
        kpi = LogicalCouplingKPI()
        coupling_data = [
            ("src/file_a.py", 0.85),
            ("src/file_b.py", 0.65),
            ("src/file_c.py", 0.45),
            ("src/file_d.py", 0.52),
        ]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data
        )
        
        # Should count: 0.85, 0.65, 0.52 (>= 0.5)
        assert kpi.value == 3
        assert kpi.calculation_values["coupled_files"] == coupling_data
        assert kpi.calculation_values["max_coupling"] == 0.85
        assert kpi.calculation_values["avg_coupling"] == pytest.approx(0.6175, rel=1e-4)

    def test_calculate_threshold_edge_case(self):
        """Test threshold edge case (exactly 0.5)."""
        kpi = LogicalCouplingKPI()
        coupling_data = [
            ("src/file_a.py", 0.5),
            ("src/file_b.py", 0.499),
            ("src/file_c.py", 0.501),
        ]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data
        )
        
        # Should count: 0.5, 0.501 (>= 0.5, but < 0.5 is excluded)
        assert kpi.value == 2

    def test_calculate_all_strong_coupling(self):
        """Test when all couplings are strong."""
        kpi = LogicalCouplingKPI()
        coupling_data = [
            ("src/file_a.py", 0.95),
            ("src/file_b.py", 0.87),
            ("src/file_c.py", 0.72),
        ]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data
        )
        
        assert kpi.value == 3
        assert kpi.calculation_values["max_coupling"] == 0.95
        assert kpi.calculation_values["avg_coupling"] == pytest.approx(0.8466, rel=1e-4)

    def test_calculate_returns_self(self):
        """Test that calculate returns self for method chaining."""
        kpi = LogicalCouplingKPI()
        coupling_data = [("src/other.py", 0.75)]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data
        )
        
        assert result is kpi


class TestLogicalCouplingKPIEdgeCases:
    """Test edge cases for LogicalCouplingKPI."""

    def test_calculate_empty_coupling_data(self):
        """Test with empty coupling data list."""
        kpi = LogicalCouplingKPI()
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=[]
        )
        
        assert kpi.value == 0
        assert kpi.calculation_values["max_coupling"] == 0.0
        assert kpi.calculation_values["avg_coupling"] == 0.0

    def test_calculate_none_coupling_data(self):
        """Test with None coupling data."""
        kpi = LogicalCouplingKPI()
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=None
        )
        
        assert kpi.value == 0
        assert kpi.calculation_values["max_coupling"] == 0.0
        assert kpi.calculation_values["avg_coupling"] == 0.0

    def test_calculate_very_high_coupling(self):
        """Test with very high coupling scores (1.0)."""
        kpi = LogicalCouplingKPI()
        coupling_data = [
            ("src/file_a.py", 1.0),
            ("src/file_b.py", 0.99),
            ("src/file_c.py", 0.98),
        ]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data
        )
        
        assert kpi.value == 3
        assert kpi.calculation_values["max_coupling"] == 1.0

    def test_calculate_many_weak_few_strong(self):
        """Test with many weak couplings and few strong ones."""
        kpi = LogicalCouplingKPI()
        coupling_data = [
            ("src/file_{}.py".format(i), 0.2 + i * 0.05)
            for i in range(10)
        ]
        # Scores: 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data
        )
        
        # Strong couplings (>= 0.5): 0.5, 0.55, 0.6, 0.65 = 4
        assert kpi.value == 4


class TestLogicalCouplingKPIDataTypes:
    """Test data type handling and calculations."""

    def test_calculate_with_kwargs(self):
        """Test calculation ignores extra kwargs gracefully."""
        kpi = LogicalCouplingKPI()
        coupling_data = [("src/other.py", 0.75)]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data,
            extra_param="ignored",
            another_param=123
        )
        
        assert kpi.value == 1
        assert result is kpi

    def test_calculation_values_structure(self):
        """Test structure of calculation_values dict."""
        kpi = LogicalCouplingKPI()
        coupling_data = [
            ("src/file_a.py", 0.85),
            ("src/file_b.py", 0.65),
        ]
        
        kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            coupling_data=coupling_data
        )
        
        assert "coupled_files" in kpi.calculation_values
        assert "max_coupling" in kpi.calculation_values
        assert "avg_coupling" in kpi.calculation_values
        
        assert kpi.calculation_values["coupled_files"] == coupling_data
        assert isinstance(kpi.calculation_values["max_coupling"], float)
        assert isinstance(kpi.calculation_values["avg_coupling"], float)
