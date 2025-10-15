"""
Tests for KPICalculator and KPI strategies.

Tests the Strategy pattern implementation for KPI calculation,
ensuring proper separation of concerns and extensibility.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.app.kpi_calculator import (
    KPICalculator,
    ComplexityKPIStrategy,
    ChurnKPIStrategy,
    HotspotKPIStrategy,
    OwnershipKPIStrategy,
    SharedOwnershipKPIStrategy
)
from src.kpis.base_kpi import BaseKPI


class TestComplexityKPIStrategy(unittest.TestCase):
    """Test ComplexityKPIStrategy."""
    
    def setUp(self):
        self.mock_analyzer = Mock()
        self.strategy = ComplexityKPIStrategy(self.mock_analyzer)
    
    def test_calculate_with_functions(self):
        """Should calculate total complexity from functions."""
        file_info = {'path': 'test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        functions_data = [
            {'name': 'func1', 'complexity': 5},
            {'name': 'func2', 'complexity': 3},
            {'name': 'func3', 'complexity': 7}
        ]
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root,
            functions_data=functions_data
        )
        
        self.assertEqual(result.name, 'complexity')
        self.assertEqual(result.value, 15)  # 5 + 3 + 7
        self.assertEqual(result.calculation_values['function_count'], 3)
    
    def test_calculate_with_empty_functions(self):
        """Should handle empty functions list."""
        file_info = {'path': 'test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        functions_data = []
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root,
            functions_data=functions_data
        )
        
        self.assertEqual(result.value, 0)
        self.assertEqual(result.calculation_values['function_count'], 0)
    
    def test_calculate_with_none_functions(self):
        """Should handle None functions list."""
        file_info = {'path': 'test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root,
            functions_data=None
        )
        
        self.assertEqual(result.value, 0)
    
    def test_calculate_ignores_missing_complexity(self):
        """Should handle functions without complexity field."""
        file_info = {'path': 'test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        functions_data = [
            {'name': 'func1', 'complexity': 5},
            {'name': 'func2'},  # Missing complexity
            {'name': 'func3', 'complexity': 3}
        ]
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root,
            functions_data=functions_data
        )
        
        self.assertEqual(result.value, 8)  # 5 + 0 + 3


class TestChurnKPIStrategy(unittest.TestCase):
    """Test ChurnKPIStrategy."""
    
    def setUp(self):
        self.strategy = ChurnKPIStrategy()
    
    @patch('src.kpis.codechurn.ChurnKPI')
    def test_calculate_calls_churn_kpi(self, mock_churn_class):
        """Should call ChurnKPI.calculate with correct parameters."""
        mock_kpi = Mock()
        mock_churn_class.return_value.calculate.return_value = mock_kpi
        
        file_info = {'path': '/repo/test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root
        )
        
        # Verify ChurnKPI was called
        mock_churn_class.return_value.calculate.assert_called_once()
        call_kwargs = mock_churn_class.return_value.calculate.call_args[1]
        self.assertEqual(call_kwargs['file_path'], '/repo/test.py')
        self.assertIn('/repo', call_kwargs['repo_root'])


class TestHotspotKPIStrategy(unittest.TestCase):
    """Test HotspotKPIStrategy."""
    
    def setUp(self):
        self.strategy = HotspotKPIStrategy()
    
    def test_calculate_with_both_kpis(self):
        """Should calculate hotspot from complexity and churn."""
        file_info = {'path': 'test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        
        complexity_kpi = Mock()
        complexity_kpi.value = 10
        
        churn_kpi = Mock()
        churn_kpi.value = 5
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root,
            complexity_kpi=complexity_kpi,
            churn_kpi=churn_kpi
        )
        
        self.assertEqual(result.name, 'hotspot')
        self.assertEqual(result.value, 50)  # 10 × 5
    
    def test_calculate_with_none_kpis(self):
        """Should handle None KPI values."""
        file_info = {'path': 'test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root,
            complexity_kpi=None,
            churn_kpi=None
        )
        
        self.assertEqual(result.value, 0)  # 0 × 0


class TestOwnershipKPIStrategy(unittest.TestCase):
    """Test OwnershipKPIStrategy."""
    
    def setUp(self):
        self.strategy = OwnershipKPIStrategy()
    
    @patch('src.kpis.codeownership.CodeOwnershipKPI')
    def test_calculate_success(self, mock_ownership_class):
        """Should create CodeOwnershipKPI on success."""
        mock_kpi = Mock()
        mock_ownership_class.return_value = mock_kpi
        
        file_info = {'path': '/repo/test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root
        )
        
        self.assertEqual(result, mock_kpi)
        mock_ownership_class.assert_called_once()
    
    @patch('src.kpis.codeownership.fallback_kpi.FallbackCodeOwnershipKPI')
    @patch('src.kpis.codeownership.CodeOwnershipKPI')
    def test_calculate_fallback_on_error(self, mock_ownership, mock_fallback):
        """Should use FallbackCodeOwnershipKPI on error."""
        mock_ownership.side_effect = Exception("Git error")
        mock_fallback_kpi = Mock()
        mock_fallback.return_value = mock_fallback_kpi
        
        file_info = {'path': '/repo/test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root
        )
        
        self.assertEqual(result, mock_fallback_kpi)
        mock_fallback.assert_called_once_with("Git error")


class TestSharedOwnershipKPIStrategy(unittest.TestCase):
    """Test SharedOwnershipKPIStrategy."""
    
    def setUp(self):
        self.strategy = SharedOwnershipKPIStrategy()
    
    @patch('src.kpis.sharedcodeownership.shared_code_ownership.SharedOwnershipKPI')
    def test_calculate_success(self, mock_shared_class):
        """Should create SharedOwnershipKPI on success."""
        mock_kpi = Mock()
        mock_shared_class.return_value = mock_kpi
        
        file_info = {'path': '/repo/test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root
        )
        
        self.assertEqual(result, mock_kpi)
        mock_shared_class.assert_called_once()
    
    @patch('src.kpis.sharedcodeownership.fallback_kpi.FallbackSharedOwnershipKPI')
    @patch('src.kpis.sharedcodeownership.shared_code_ownership.SharedOwnershipKPI')
    def test_calculate_fallback_on_error(self, mock_shared, mock_fallback):
        """Should use FallbackSharedOwnershipKPI on error."""
        mock_shared.side_effect = Exception("Git error")
        mock_fallback_kpi = Mock()
        mock_fallback.return_value = mock_fallback_kpi
        
        file_info = {'path': '/repo/test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        
        result = self.strategy.calculate(
            file_info=file_info,
            repo_root=repo_root
        )
        
        self.assertEqual(result, mock_fallback_kpi)
        mock_fallback.assert_called_once_with("Git error")


class TestKPICalculator(unittest.TestCase):
    """Test KPICalculator orchestration."""
    
    def setUp(self):
        self.mock_analyzer = Mock()
        self.calculator = KPICalculator(self.mock_analyzer)
    
    def test_initialization(self):
        """Should initialize with default strategies."""
        self.assertIn('complexity', self.calculator.strategies)
        self.assertIn('churn', self.calculator.strategies)
        self.assertIn('hotspot', self.calculator.strategies)
        self.assertIn('ownership', self.calculator.strategies)
        self.assertIn('shared_ownership', self.calculator.strategies)
        
        # Should initialize timing
        self.assertEqual(len(self.calculator.timing), 5)
        self.assertTrue(all(v == 0.0 for v in self.calculator.timing.values()))
    
    def test_register_strategy(self):
        """Should register custom strategy."""
        mock_strategy = Mock()
        
        self.calculator.register_strategy('custom_kpi', mock_strategy)
        
        self.assertIn('custom_kpi', self.calculator.strategies)
        self.assertEqual(self.calculator.strategies['custom_kpi'], mock_strategy)
        self.assertIn('custom_kpi', self.calculator.timing)
    
    @patch('src.app.kpi_calculator.ComplexityKPIStrategy')
    @patch('src.app.kpi_calculator.ChurnKPIStrategy')
    @patch('src.app.kpi_calculator.HotspotKPIStrategy')
    @patch('src.app.kpi_calculator.OwnershipKPIStrategy')
    @patch('src.app.kpi_calculator.SharedOwnershipKPIStrategy')
    def test_calculate_all_orchestration(
        self,
        mock_shared_strategy,
        mock_ownership_strategy,
        mock_hotspot_strategy,
        mock_churn_strategy,
        mock_complexity_strategy
    ):
        """Should orchestrate all KPI calculations in correct order."""
        # Create mock KPIs
        complexity_kpi = Mock()
        complexity_kpi.name = 'complexity'
        complexity_kpi.value = 10
        
        churn_kpi = Mock()
        churn_kpi.name = 'churn'
        churn_kpi.value = 5
        
        hotspot_kpi = Mock()
        hotspot_kpi.name = 'hotspot'
        hotspot_kpi.value = 50
        
        ownership_kpi = Mock()
        ownership_kpi.name = 'Code Ownership'
        
        shared_kpi = Mock()
        shared_kpi.name = 'Shared Ownership'
        
        # Configure strategies
        mock_complexity_strategy.return_value.calculate.return_value = complexity_kpi
        mock_churn_strategy.return_value.calculate.return_value = churn_kpi
        mock_hotspot_strategy.return_value.calculate.return_value = hotspot_kpi
        mock_ownership_strategy.return_value.calculate.return_value = ownership_kpi
        mock_shared_strategy.return_value.calculate.return_value = shared_kpi
        
        # Create calculator with mocked strategies
        calculator = KPICalculator(self.mock_analyzer)
        
        file_info = {'path': 'test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        content = "def test(): pass"
        functions_data = [{'name': 'test', 'complexity': 1}]
        
        result = calculator.calculate_all(
            file_info=file_info,
            repo_root=repo_root,
            content=content,
            functions_data=functions_data
        )
        
        # Verify all KPIs calculated
        self.assertEqual(len(result), 5)
        self.assertIn('complexity', result)
        self.assertIn('churn', result)
        self.assertIn('hotspot', result)
        self.assertIn('Code Ownership', result)
        self.assertIn('Shared Ownership', result)
    
    def test_get_timing_report(self):
        """Should return timing statistics."""
        # Manually set some timing values
        self.calculator.timing['complexity'] = 0.123
        self.calculator.timing['churn'] = 0.456
        
        timing = self.calculator.get_timing_report()
        
        self.assertEqual(timing['complexity'], 0.123)
        self.assertEqual(timing['churn'], 0.456)
        
        # Should return copy, not original
        timing['complexity'] = 999
        self.assertEqual(self.calculator.timing['complexity'], 0.123)
    
    def test_reset_timing(self):
        """Should reset all timing counters."""
        self.calculator.timing['complexity'] = 1.5
        self.calculator.timing['churn'] = 2.3
        
        self.calculator.reset_timing()
        
        self.assertTrue(all(v == 0.0 for v in self.calculator.timing.values()))
    
    @patch('src.app.kpi_calculator.time')
    def test_timing_tracked(self, mock_time):
        """Should track timing for each KPI calculation."""
        # Mock time.perf_counter to return sequential values
        mock_time.perf_counter.side_effect = [
            0.0, 0.1,  # complexity: 0.1s
            0.1, 0.3,  # churn: 0.2s
            0.3, 0.35, # hotspot: 0.05s
            0.35, 0.5, # ownership: 0.15s
            0.5, 0.6   # shared: 0.1s
        ]
        
        file_info = {'path': 'test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        content = "def test(): pass"
        functions_data = [{'name': 'test', 'complexity': 1}]
        
        self.calculator.calculate_all(
            file_info=file_info,
            repo_root=repo_root,
            content=content,
            functions_data=functions_data
        )
        
        # Verify timing was tracked (approximately)
        self.assertAlmostEqual(self.calculator.timing['complexity'], 0.1, places=2)
        self.assertAlmostEqual(self.calculator.timing['churn'], 0.2, places=2)
        self.assertAlmostEqual(self.calculator.timing['hotspot'], 0.05, places=2)
        self.assertAlmostEqual(self.calculator.timing['ownership'], 0.15, places=2)
        self.assertAlmostEqual(self.calculator.timing['shared_ownership'], 0.1, places=2)


class TestKPICalculatorIntegration(unittest.TestCase):
    """Integration tests with real KPI classes."""
    
    def setUp(self):
        from src.kpis.complexity import ComplexityAnalyzer
        self.analyzer = ComplexityAnalyzer()
        self.calculator = KPICalculator(self.analyzer)
    
    @patch('src.utilities.git_cache.get_git_cache')
    def test_calculate_all_integration(self, mock_git_cache):
        """Should calculate all KPIs with real KPI classes."""
        # Mock git cache to return predictable churn
        mock_cache = Mock()
        mock_cache.get_churn_data.return_value = 5
        mock_git_cache.return_value = mock_cache
        
        file_info = {'path': '/repo/test.py', 'ext': 'py'}
        repo_root = Path('/repo')
        content = "def simple_function():\n    return 42"
        functions_data = [{'name': 'simple_function', 'complexity': 1}]
        
        result = self.calculator.calculate_all(
            file_info=file_info,
            repo_root=repo_root,
            content=content,
            functions_data=functions_data
        )
        
        # Verify all KPIs present
        self.assertIn('complexity', result)
        self.assertIn('churn', result)
        self.assertIn('hotspot', result)
        self.assertIn('Code Ownership', result)
        self.assertIn('Shared Ownership', result)
        
        # Verify complexity calculated correctly
        self.assertEqual(result['complexity'].value, 1)
        self.assertEqual(result['complexity'].calculation_values['function_count'], 1)


if __name__ == '__main__':
    unittest.main()
