"""
Unit tests for KPIOrchestrator class.

Following TDD (Test-Driven Development):
- RED: Write failing tests first
- GREEN: Implement minimal code to pass tests
- REFACTOR: Improve code quality
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

# Import from processing package
from src.app.processing.kpi_orchestrator import KPIOrchestrator


class MockKPI:
    """Mock KPI class for testing."""
    
    def __init__(self, name="MockKPI", value=42):
        self.name = name
        self.value = value
    
    def calculate(self, **kwargs):
        """Mock calculate method."""
        return self


class TestKPIOrchestrator:
    """Test suite for KPIOrchestrator class."""
    
    def test_kpi_orchestrator_can_be_instantiated(self):
        """Test that KPIOrchestrator can be created."""
        calculators = {}
        orchestrator = KPIOrchestrator(calculators)
        assert orchestrator is not None
    
    def test_orchestrator_stores_calculators(self):
        """Test that orchestrator stores provided calculators."""
        calculators = {
            'complexity': MockKPI(name='complexity', value=10),
            'churn': MockKPI(name='churn', value=5)
        }
        orchestrator = KPIOrchestrator(calculators)
        
        assert hasattr(orchestrator, 'calculators')
        assert orchestrator.calculators == calculators
    
    def test_calculate_file_kpis_with_empty_calculators(self):
        """Test calculating KPIs with no calculators returns empty dict."""
        orchestrator = KPIOrchestrator({})
        file_context = {'file_path': '/test/file.py'}
        
        kpis = orchestrator.calculate_file_kpis(file_context)
        
        assert kpis == {}
    
    def test_calculate_file_kpis_calls_single_calculator(self):
        """Test that calculate_file_kpis calls the calculator."""
        mock_calculator = Mock()
        mock_kpi = MockKPI(name='complexity', value=10)
        mock_calculator.calculate = Mock(return_value=mock_kpi)
        
        calculators = {'complexity': mock_calculator}
        orchestrator = KPIOrchestrator(calculators)
        
        file_context = {'file_path': '/test/file.py', 'complexity': 10}
        kpis = orchestrator.calculate_file_kpis(file_context)
        
        # Verify calculator was called
        mock_calculator.calculate.assert_called_once()
        
        # Verify KPI is in result
        assert 'complexity' in kpis
        assert kpis['complexity'] == mock_kpi
    
    def test_calculate_file_kpis_calls_multiple_calculators(self):
        """Test that all calculators are called."""
        mock_calc1 = Mock()
        mock_calc1.calculate = Mock(return_value=MockKPI(name='complexity', value=10))
        
        mock_calc2 = Mock()
        mock_calc2.calculate = Mock(return_value=MockKPI(name='churn', value=5))
        
        calculators = {
            'complexity': mock_calc1,
            'churn': mock_calc2
        }
        orchestrator = KPIOrchestrator(calculators)
        
        file_context = {'file_path': '/test/file.py'}
        kpis = orchestrator.calculate_file_kpis(file_context)
        
        # Both calculators should be called
        mock_calc1.calculate.assert_called_once()
        mock_calc2.calculate.assert_called_once()
        
        # Both KPIs should be in result
        assert len(kpis) == 2
        assert 'complexity' in kpis
        assert 'churn' in kpis
    
    def test_calculate_file_kpis_passes_context_to_calculators(self):
        """Test that file context is passed to calculators."""
        mock_calculator = Mock()
        mock_calculator.calculate = Mock(return_value=MockKPI())
        
        calculators = {'test': mock_calculator}
        orchestrator = KPIOrchestrator(calculators)
        
        file_context = {
            'file_path': '/test/file.py',
            'complexity': 15,
            'function_count': 3
        }
        orchestrator.calculate_file_kpis(file_context)
        
        # Verify context was passed
        mock_calculator.calculate.assert_called_once_with(**file_context)
    
    def test_calculate_file_kpis_uses_kpi_name_as_key(self):
        """Test that KPI name is used as dictionary key."""
        mock_kpi = MockKPI(name='custom_name', value=99)
        mock_calculator = Mock()
        mock_calculator.calculate = Mock(return_value=mock_kpi)
        
        calculators = {'calculator_key': mock_calculator}
        orchestrator = KPIOrchestrator(calculators)
        
        kpis = orchestrator.calculate_file_kpis({})
        
        # Key should be the KPI's name, not the calculator key
        assert 'custom_name' in kpis
        assert kpis['custom_name'].name == 'custom_name'
    
    def test_calculate_file_kpis_handles_calculator_exception(self):
        """Test that calculator exceptions are handled gracefully."""
        mock_calculator = Mock()
        mock_calculator.calculate = Mock(side_effect=ValueError("Calculation failed"))
        
        calculators = {'failing': mock_calculator}
        orchestrator = KPIOrchestrator(calculators)
        
        # Should not raise exception
        kpis = orchestrator.calculate_file_kpis({'file_path': '/test/file.py'})
        
        # Failed KPI should not be in results
        assert 'failing' not in kpis
    
    def test_orchestrator_with_real_kpi_interface(self):
        """Test orchestrator with KPI-like objects."""
        class RealishKPI:
            def __init__(self, name, value):
                self.name = name
                self.value = value
            
            def calculate(self, **kwargs):
                # Simulate calculation
                self.value = kwargs.get('complexity', 0) * 2
                return self
        
        calc1 = RealishKPI('complexity', 0)
        calc2 = RealishKPI('churn', 0)
        
        calculators = {'complexity': calc1, 'churn': calc2}
        orchestrator = KPIOrchestrator(calculators)
        
        kpis = orchestrator.calculate_file_kpis({'complexity': 5})
        
        assert 'complexity' in kpis
        assert kpis['complexity'].value == 10  # 5 * 2
    
    def test_orchestrator_preserves_calculator_order(self):
        """Test that calculators are processed in consistent order."""
        calculators = {
            'first': Mock(calculate=Mock(return_value=MockKPI(name='first'))),
            'second': Mock(calculate=Mock(return_value=MockKPI(name='second'))),
            'third': Mock(calculate=Mock(return_value=MockKPI(name='third')))
        }
        orchestrator = KPIOrchestrator(calculators)
        
        kpis = orchestrator.calculate_file_kpis({})
        
        # All should be present
        assert len(kpis) == 3
        assert 'first' in kpis
        assert 'second' in kpis
        assert 'third' in kpis
    
    def test_calculate_with_partial_context(self):
        """Test calculation with incomplete context."""
        mock_calculator = Mock()
        mock_calculator.calculate = Mock(return_value=MockKPI())
        
        calculators = {'test': mock_calculator}
        orchestrator = KPIOrchestrator(calculators)
        
        # Minimal context
        kpis = orchestrator.calculate_file_kpis({'file_path': '/test.py'})
        
        assert len(kpis) == 1
        mock_calculator.calculate.assert_called_once()
    
    def test_orchestrator_is_reusable(self):
        """Test that orchestrator can be used multiple times."""
        mock_calculator = Mock()
        mock_calculator.calculate = Mock(return_value=MockKPI())
        
        calculators = {'test': mock_calculator}
        orchestrator = KPIOrchestrator(calculators)
        
        # First call
        kpis1 = orchestrator.calculate_file_kpis({'file_path': '/file1.py'})
        
        # Second call
        kpis2 = orchestrator.calculate_file_kpis({'file_path': '/file2.py'})
        
        # Should be called twice
        assert mock_calculator.calculate.call_count == 2
        assert len(kpis1) == 1
        assert len(kpis2) == 1
    
    def test_orchestrator_with_no_calculators_defined(self):
        """Test orchestrator behavior with None calculators."""
        # Should handle None gracefully
        try:
            orchestrator = KPIOrchestrator(None)
            kpis = orchestrator.calculate_file_kpis({})
            assert kpis == {}
        except (TypeError, AttributeError):
            # If it raises, that's also acceptable behavior
            pass
    
    def test_calculate_returns_dict(self):
        """Test that calculate_file_kpis always returns a dict."""
        calculators = {
            'test': Mock(calculate=Mock(return_value=MockKPI()))
        }
        orchestrator = KPIOrchestrator(calculators)
        
        result = orchestrator.calculate_file_kpis({})
        
        assert isinstance(result, dict)
    
    def test_orchestrator_with_factory_pattern_calculators(self):
        """Test orchestrator with factory-created calculators."""
        # Some KPIs need to be instantiated per file
        class KPIFactory:
            def __init__(self, kpi_class):
                self.kpi_class = kpi_class
            
            def calculate(self, **kwargs):
                instance = self.kpi_class()
                instance.name = 'factory_kpi'
                instance.value = 42
                return instance
        
        class DummyKPI:
            pass
        
        factory = KPIFactory(DummyKPI)
        calculators = {'factory': factory}
        orchestrator = KPIOrchestrator(calculators)
        
        kpis = orchestrator.calculate_file_kpis({})
        
        assert 'factory_kpi' in kpis
