"""
Integration tests for Cognitive Complexity KPI in KPICalculator.

Tests that cognitive complexity is properly integrated into the KPI calculation pipeline.
Following TDD approach: RED → GREEN → REFACTOR
"""
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

from src.app.kpi.kpi_calculator import KPICalculator
from src.kpis.complexity import ComplexityAnalyzer


class TestKPICalculatorCognitiveComplexity(unittest.TestCase):
    """Test cognitive complexity integration in KPICalculator."""

    def setUp(self):
        """Set up test fixtures."""
        self.complexity_analyzer = ComplexityAnalyzer()
        self.calculator = KPICalculator(self.complexity_analyzer)

    def test_cognitive_complexity_strategy_registered(self):
        """Test that cognitive_complexity strategy is registered."""
        self.assertIn('cognitive_complexity', self.calculator.strategies)

    def test_cognitive_complexity_in_timing(self):
        """Test that cognitive_complexity timing tracker exists."""
        self.assertIn('cognitive_complexity', self.calculator.timing)
        self.assertEqual(self.calculator.timing['cognitive_complexity'], 0.0)

    def test_cognitive_complexity_strategy_calculates(self):
        """Test that cognitive complexity strategy can calculate."""
        strategy = self.calculator.strategies['cognitive_complexity']
        
        python_code = '''
def simple_function(x):
    if x > 0:
        return 1
    else:
        return 0
'''
        
        file_info = {
            'path': '/fake/path/test.py',
            'ext': '.py'
        }
        repo_root = Path('/fake/path')
        
        kpi = strategy.calculate(
            file_info=file_info,
            repo_root=repo_root,
            content=python_code
        )
        
        # Assert it returns a KPI object
        from src.kpis.cognitive_complexity import CognitiveComplexityKPI
        self.assertIsInstance(kpi, CognitiveComplexityKPI)
        
        # Assert it has the correct name
        self.assertEqual(kpi.name, 'cognitive_complexity')
        
        # Assert it calculated a value
        self.assertIsNotNone(kpi.value)
        self.assertEqual(kpi.value, 2)  # if + else = 2

    def test_cognitive_complexity_for_non_python_returns_empty(self):
        """Test that cognitive complexity returns empty KPI for non-Python files."""
        strategy = self.calculator.strategies['cognitive_complexity']
        
        javascript_code = '''
function test() {
    if (x > 0) {
        return 1;
    }
}
'''
        
        file_info = {
            'path': '/fake/path/test.js',
            'ext': '.js'
        }
        repo_root = Path('/fake/path')
        
        kpi = strategy.calculate(
            file_info=file_info,
            repo_root=repo_root,
            content=javascript_code
        )
        
        # Should return empty KPI for non-Python
        self.assertIsNone(kpi.value)

    def test_cognitive_complexity_with_nesting(self):
        """Test cognitive complexity calculation with nesting."""
        strategy = self.calculator.strategies['cognitive_complexity']
        
        python_code = '''
def nested_complexity(x, y):
    if x > 0:              # +1
        if y > 0:          # +2 (nesting)
            return x + y
    return 0
'''
        
        file_info = {
            'path': '/fake/path/test.py',
            'ext': '.py'
        }
        repo_root = Path('/fake/path')
        
        kpi = strategy.calculate(
            file_info=file_info,
            repo_root=repo_root,
            content=python_code
        )
        
        # Check cognitive complexity value
        self.assertIsNotNone(kpi.value)
        self.assertEqual(kpi.value, 3)  # 1 + 2 for nesting
        
        # Check calculation values (per-function data)
        self.assertIn('nested_complexity', kpi.calculation_values)
        self.assertEqual(
            kpi.calculation_values['nested_complexity'], 
            3
        )


if __name__ == '__main__':
    unittest.main()
