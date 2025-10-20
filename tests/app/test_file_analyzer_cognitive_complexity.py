"""
End-to-end tests for Cognitive Complexity integration in FileAnalyzer.

Verifies that cognitive complexity flows through the entire pipeline:
1. KPICalculator calculates cognitive_complexity
2. FileAnalyzer receives it in file_kpis
3. File object includes cognitive_complexity in kpis dict
4. Function objects include per-function cognitive_complexity
"""
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import os

from src.app.kpi.file_analyzer import FileAnalyzer
from src.app.kpi.kpi_calculator import KPICalculator
from src.kpis.complexity import ComplexityAnalyzer
from src.kpis.cognitive_complexity import CognitiveComplexityKPI
from src.languages.config import Config


class TestFileAnalyzerCognitiveComplexityEndToEnd(unittest.TestCase):
    """End-to-end tests for cognitive complexity integration."""

    def setUp(self):
        """Set up test fixtures."""
        # Use real Config to get proper parser classes
        config = Config()
        self.languages_config = config.languages

        # Real components (not mocked)
        complexity_analyzer = ComplexityAnalyzer()
        self.kpi_calculator = KPICalculator(complexity_analyzer)
        self.analyzer = FileAnalyzer(
            languages_config=self.languages_config,
            kpi_calculator=self.kpi_calculator
        )

    def test_cognitive_complexity_in_file_kpis(self):
        """Should include cognitive_complexity in file-level KPIs."""
        # Create a temporary Python file with nested structure
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write("""
def nested_function(x, y):
    if x:                    # +1
        if y:                # +2 (1 + 1 nesting)
            if x > 10:       # +3 (1 + 2 nesting)
                return True
    return False
""")
            temp_path = f.name

        try:
            file_info = {
                'path': temp_path,
                'ext': '.py'
            }
            repo_root = Path(tempfile.gettempdir())

            # Analyze file
            file_obj = self.analyzer.analyze_file(file_info, repo_root)

            # Verify cognitive_complexity is in file KPIs
            self.assertIsNotNone(file_obj)
            self.assertIn('cognitive_complexity', file_obj.kpis)

            # Verify it's a CognitiveComplexityKPI instance
            cog_kpi = file_obj.kpis['cognitive_complexity']
            self.assertIsInstance(cog_kpi, CognitiveComplexityKPI)

            # Verify the value is correct (should be 6: 1 + 2 + 3)
            self.assertEqual(cog_kpi.value, 6)

        finally:
            os.unlink(temp_path)

    def test_cognitive_complexity_in_function_kpis(self):
        """Should include per-function cognitive_complexity in Function objects."""
        # Create a temporary Python file with two functions
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write("""
def simple_function(x):
    if x == 1: return "one"   # +1
    if x == 2: return "two"   # +1
    return "other"

def nested_function(x, y):
    if x:                    # +1
        if y:                # +2 (1 + 1 nesting)
            return True
    return False
""")
            temp_path = f.name

        try:
            file_info = {
                'path': temp_path,
                'ext': '.py'
            }
            repo_root = Path(tempfile.gettempdir())

            # Analyze file
            file_obj = self.analyzer.analyze_file(file_info, repo_root)

            # Verify we have 2 functions
            self.assertIsNotNone(file_obj)
            self.assertEqual(len(file_obj.functions), 2,
                           f"Expected 2 functions, got {len(file_obj.functions)}")

            # Verify at least one function has cognitive_complexity
            functions_with_cog = [
                f for f in file_obj.functions
                if 'cognitive_complexity' in f.kpis
            ]
            self.assertGreater(len(functions_with_cog), 0,
                             "At least one function should have cognitive_complexity")

        finally:
            os.unlink(temp_path)

    def test_data_model_compatibility(self):
        """Should work with existing Dict[str, BaseKPI] data model."""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write("""
def simple_function(x):
    if x: return True
    return False
""")
            temp_path = f.name

        try:
            file_info = {
                'path': temp_path,
                'ext': '.py'
            }
            repo_root = Path(tempfile.gettempdir())

            # Analyze file
            file_obj = self.analyzer.analyze_file(file_info, repo_root)

            # Verify file_obj.kpis is a dict
            self.assertIsNotNone(file_obj)
            self.assertIsInstance(file_obj.kpis, dict)

            # Verify it contains core KPIs (names may vary)
            self.assertIn('complexity', file_obj.kpis)
            self.assertIn('cognitive_complexity', file_obj.kpis)
            self.assertIn('churn', file_obj.kpis)
            self.assertIn('hotspot', file_obj.kpis)

            # Ownership KPIs may have different names
            has_ownership = any(
                'ownership' in k.lower() for k in file_obj.kpis.keys()
            )
            self.assertTrue(has_ownership, "Should have at least one ownership KPI")

            # Verify all values are BaseKPI instances
            from src.kpis.base_kpi import BaseKPI
            for kpi_name, kpi_obj in file_obj.kpis.items():
                self.assertIsInstance(
                    kpi_obj,
                    BaseKPI,
                    f"KPI '{kpi_name}' should be BaseKPI instance"
                )

        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
