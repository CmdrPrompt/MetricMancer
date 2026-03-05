"""
Tests for ChangeCoupledHotspotKPI.

Tests change-coupled hotspot KPI that combines complexity, churn, and coupling.
"""

import pytest
from src.kpis.coupling.change_coupled_hotspot_kpi import ChangeCoupledHotspotKPI


class TestChangeCoupledHotspotKPIBasics:
    """Test basic ChangeCoupledHotspotKPI functionality."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        kpi = ChangeCoupledHotspotKPI()
        assert kpi.name == "change_coupled_hotspot"
        assert kpi.value is None
        assert kpi.unit == "score"
        assert kpi.description == "Coupled hotspot score (complexity × churn × coupling)"
        assert kpi.calculation_values == {}

    def test_init_with_values(self):
        """Test initialization with explicit values."""
        calc_values = {
            "base_hotspot": 100,
            "max_coupling": 0.75,
            "num_strong_couplings": 2,
            "coupling_multiplier": 1.2
        }
        kpi = ChangeCoupledHotspotKPI(value=120, calculation_values=calc_values)
        assert kpi.value == 120
        assert kpi.calculation_values == calc_values

    def test_calculate_no_coupling(self):
        """Test calculation with no coupling."""
        kpi = ChangeCoupledHotspotKPI()
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=10,
            churn=5,
            coupling_data=[]
        )
        
        assert result is kpi  # Should return self for chaining
        # base_hotspot = 10 * 5 = 50
        # No strong couplings, so multiplier = 1.0
        # coupled_hotspot = 50 * 1.0 = 50
        assert kpi.value == 50
        assert kpi.calculation_values["base_hotspot"] == 50
        assert kpi.calculation_values["max_coupling"] == 0.0
        assert kpi.calculation_values["num_strong_couplings"] == 0
        assert kpi.calculation_values["coupling_multiplier"] == 1.0

    def test_calculate_single_strong_coupling(self):
        """Test calculation with single strong coupling."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [("src/other.py", 0.75)]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=10,
            churn=5,
            coupling_data=coupling_data
        )
        
        # base_hotspot = 10 * 5 = 50
        # max_coupling = 0.75
        # num_strong_couplings = 1
        # coupling_multiplier = 1 + (1 * 0.1) = 1.1
        # coupled_hotspot = 50 * 0.75 * 1.1 = 41.25
        assert kpi.value == pytest.approx(41.25)
        assert kpi.calculation_values["base_hotspot"] == 50
        assert kpi.calculation_values["max_coupling"] == 0.75
        assert kpi.calculation_values["num_strong_couplings"] == 1
        assert kpi.calculation_values["coupling_multiplier"] == pytest.approx(1.1)

    def test_calculate_multiple_strong_couplings(self):
        """Test calculation with multiple strong couplings."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [
            ("src/file_a.py", 0.85),
            ("src/file_b.py", 0.65),
            ("src/file_c.py", 0.52),
            ("src/file_d.py", 0.45),  # Weak coupling, not counted
        ]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=15,
            churn=8,
            coupling_data=coupling_data
        )
        
        # base_hotspot = 15 * 8 = 120
        # max_coupling = 0.85
        # num_strong_couplings = 3 (0.85, 0.65, 0.52 are >= 0.5)
        # coupling_multiplier = 1 + (3 * 0.1) = 1.3
        # coupled_hotspot = 120 * 0.85 * 1.3 = 132.6
        assert kpi.value == pytest.approx(132.6)
        assert kpi.calculation_values["base_hotspot"] == 120
        assert kpi.calculation_values["max_coupling"] == 0.85
        assert kpi.calculation_values["num_strong_couplings"] == 3
        assert kpi.calculation_values["coupling_multiplier"] == pytest.approx(1.3)

    def test_formula_accuracy(self):
        """Test the complete formula: base_hotspot × max_coupling × coupling_multiplier."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [
            ("src/a.py", 0.8),
            ("src/b.py", 0.6),
        ]
        
        complexity = 20
        churn = 10
        
        kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=complexity,
            churn=churn,
            coupling_data=coupling_data
        )
        
        base = complexity * churn  # 200
        max_coupling = 0.8
        strong_count = 2  # Both >= 0.5
        multiplier = 1 + (strong_count * 0.1)  # 1.2
        expected = base * max_coupling * multiplier  # 200 * 0.8 * 1.2 = 192
        
        assert kpi.value == pytest.approx(expected)

    def test_calculate_returns_self(self):
        """Test that calculate returns self for method chaining."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [("src/other.py", 0.75)]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=10,
            churn=5,
            coupling_data=coupling_data
        )
        
        assert result is kpi


class TestChangeCoupledHotspotKPIRiskLevels:
    """Test risk level categorization."""

    def test_get_risk_level_critical(self):
        """Test CRITICAL risk level (>= 1000)."""
        kpi = ChangeCoupledHotspotKPI()
        assert kpi.get_risk_level(1000) == "CRITICAL"
        assert kpi.get_risk_level(1500) == "CRITICAL"
        assert kpi.get_risk_level(5000) == "CRITICAL"

    def test_get_risk_level_very_high(self):
        """Test VERY_HIGH risk level (>= 500, < 1000)."""
        kpi = ChangeCoupledHotspotKPI()
        assert kpi.get_risk_level(500) == "VERY_HIGH"
        assert kpi.get_risk_level(750) == "VERY_HIGH"
        assert kpi.get_risk_level(999) == "VERY_HIGH"

    def test_get_risk_level_high(self):
        """Test HIGH risk level (>= 200, < 500)."""
        kpi = ChangeCoupledHotspotKPI()
        assert kpi.get_risk_level(200) == "HIGH"
        assert kpi.get_risk_level(350) == "HIGH"
        assert kpi.get_risk_level(499) == "HIGH"

    def test_get_risk_level_medium(self):
        """Test MEDIUM risk level (>= 100, < 200)."""
        kpi = ChangeCoupledHotspotKPI()
        assert kpi.get_risk_level(100) == "MEDIUM"
        assert kpi.get_risk_level(150) == "MEDIUM"
        assert kpi.get_risk_level(199) == "MEDIUM"

    def test_get_risk_level_low(self):
        """Test LOW risk level (< 100)."""
        kpi = ChangeCoupledHotspotKPI()
        assert kpi.get_risk_level(0) == "LOW"
        assert kpi.get_risk_level(50) == "LOW"
        assert kpi.get_risk_level(99) == "LOW"

    def test_risk_level_edge_cases(self):
        """Test edge cases at risk level boundaries."""
        kpi = ChangeCoupledHotspotKPI()
        
        # Test exact boundaries
        assert kpi.get_risk_level(99.99) == "LOW"
        assert kpi.get_risk_level(100.0) == "MEDIUM"
        assert kpi.get_risk_level(199.99) == "MEDIUM"
        assert kpi.get_risk_level(200.0) == "HIGH"
        assert kpi.get_risk_level(499.99) == "HIGH"
        assert kpi.get_risk_level(500.0) == "VERY_HIGH"
        assert kpi.get_risk_level(999.99) == "VERY_HIGH"
        assert kpi.get_risk_level(1000.0) == "CRITICAL"


class TestChangeCoupledHotspotKPIEdgeCases:
    """Test edge cases for ChangeCoupledHotspotKPI."""

    def test_calculate_zero_complexity_zero_churn(self):
        """Test with zero complexity and churn."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [("src/other.py", 0.75)]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=0,
            churn=0,
            coupling_data=coupling_data
        )
        
        # base_hotspot = 0 * 0 = 0
        # coupled_hotspot = 0 * max_coupling * multiplier = 0
        assert kpi.value == 0
        assert kpi.calculation_values["base_hotspot"] == 0

    def test_calculate_zero_complexity_nonzero_churn(self):
        """Test with zero complexity but nonzero churn."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [("src/other.py", 0.75)]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=0,
            churn=10,
            coupling_data=coupling_data
        )
        
        assert kpi.value == 0
        assert kpi.calculation_values["base_hotspot"] == 0

    def test_calculate_high_complexity_high_churn_no_coupling(self):
        """Test with high complexity and churn but no coupling."""
        kpi = ChangeCoupledHotspotKPI()
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=50,
            churn=50,
            coupling_data=[]
        )
        
        # base_hotspot = 50 * 50 = 2500
        # No coupling: coupling_multiplier = 1.0
        # coupled_hotspot = 2500 * 1.0 = 2500
        assert kpi.value == 2500

    def test_calculate_high_complexity_high_churn_high_coupling(self):
        """Test with high complexity, churn, and coupling."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [
            ("src/a.py", 0.95),
            ("src/b.py", 0.87),
            ("src/c.py", 0.72),
            ("src/d.py", 0.65),
            ("src/e.py", 0.58),
        ]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=50,
            churn=50,
            coupling_data=coupling_data
        )
        
        # base_hotspot = 50 * 50 = 2500
        # max_coupling = 0.95
        # num_strong_couplings = 5 (all >= 0.5)
        # coupling_multiplier = 1 + (5 * 0.1) = 1.5
        # coupled_hotspot = 2500 * 0.95 * 1.5 = 3562.5
        assert kpi.value == pytest.approx(3562.5)
        assert kpi.get_risk_level(kpi.value) == "CRITICAL"

    def test_calculate_empty_coupling_data(self):
        """Test with empty coupling data list."""
        kpi = ChangeCoupledHotspotKPI()
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=10,
            churn=5,
            coupling_data=[]
        )
        
        assert kpi.value == 50
        assert kpi.calculation_values["max_coupling"] == 0.0
        assert kpi.calculation_values["num_strong_couplings"] == 0

    def test_calculate_none_coupling_data(self):
        """Test with None coupling data."""
        kpi = ChangeCoupledHotspotKPI()
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=10,
            churn=5,
            coupling_data=None
        )
        
        assert kpi.value == 50
        assert kpi.calculation_values["max_coupling"] == 0.0
        assert kpi.calculation_values["num_strong_couplings"] == 0

    def test_calculate_all_weak_coupling(self):
        """Test with all weak couplings (< 0.5)."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [
            ("src/a.py", 0.4),
            ("src/b.py", 0.35),
            ("src/c.py", 0.25),
        ]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=10,
            churn=8,
            coupling_data=coupling_data
        )
        
        # base_hotspot = 10 * 8 = 80
        # max_coupling = 0.4
        # num_strong_couplings = 0 (none >= 0.5)
        # coupling_multiplier = 1.0
        # coupled_hotspot = 80 * 0.4 * 1.0 = 32
        assert kpi.value == pytest.approx(32)
        assert kpi.calculation_values["num_strong_couplings"] == 0
        assert kpi.calculation_values["coupling_multiplier"] == 1.0

    def test_calculate_threshold_edge_case(self):
        """Test threshold edge case (exactly 0.5)."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [
            ("src/a.py", 0.5),
            ("src/b.py", 0.499),
        ]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=10,
            churn=10,
            coupling_data=coupling_data
        )
        
        # base_hotspot = 10 * 10 = 100
        # max_coupling = 0.5
        # num_strong_couplings = 1 (only 0.5, not 0.499)
        # coupling_multiplier = 1 + (1 * 0.1) = 1.1
        # coupled_hotspot = 100 * 0.5 * 1.1 = 55
        assert kpi.value == pytest.approx(55)
        assert kpi.calculation_values["num_strong_couplings"] == 1


class TestChangeCoupledHotspotKPIDataTypes:
    """Test data type handling and calculations."""

    def test_calculation_values_structure(self):
        """Test structure of calculation_values dict."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [("src/other.py", 0.75)]
        
        kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=10,
            churn=5,
            coupling_data=coupling_data
        )
        
        assert "base_hotspot" in kpi.calculation_values
        assert "max_coupling" in kpi.calculation_values
        assert "num_strong_couplings" in kpi.calculation_values
        assert "coupling_multiplier" in kpi.calculation_values
        
        assert isinstance(kpi.calculation_values["base_hotspot"], (int, float))
        assert isinstance(kpi.calculation_values["max_coupling"], float)
        assert isinstance(kpi.calculation_values["num_strong_couplings"], int)
        assert isinstance(kpi.calculation_values["coupling_multiplier"], float)

    def test_calculate_with_extra_kwargs(self):
        """Test calculation ignores extra kwargs gracefully."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [("src/other.py", 0.75)]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=10,
            churn=5,
            coupling_data=coupling_data,
            extra_param="ignored",
            another_param=123
        )
        
        assert kpi.value == pytest.approx(41.25)
        assert result is kpi

    def test_float_precision(self):
        """Test floating-point precision in calculations."""
        kpi = ChangeCoupledHotspotKPI()
        coupling_data = [
            ("src/a.py", 0.333),
            ("src/b.py", 0.777),
        ]
        
        result = kpi.calculate(
            file_path="src/file.py",
            repo_root="/repo",
            complexity=7,
            churn=3,
            coupling_data=coupling_data
        )
        
        # base_hotspot = 7 * 3 = 21
        # max_coupling = 0.777
        # num_strong_couplings = 1 (0.777 >= 0.5, 0.333 < 0.5)
        # coupling_multiplier = 1.1
        # coupled_hotspot = 21 * 0.777 * 1.1 ≈ 17.99
        expected = 21 * 0.777 * 1.1
        assert kpi.value == pytest.approx(expected, rel=1e-5)
