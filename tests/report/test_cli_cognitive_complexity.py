"""
RED Phase: Tests for Cognitive Complexity in CLI Report Format

Following TDD RED-GREEN-REFACTOR:
- 🔴 RED: These tests SHOULD FAIL initially
- 🟢 GREEN: Implement minimal code to make them pass
- 🔵 REFACTOR: Clean up implementation

Tests verify:
1. File-level cognitive complexity appears in CLI output
2. Function-level cognitive complexity appears in CLI output
3. Fallback to '?' when cognitive complexity is not available
"""
import unittest
from unittest.mock import MagicMock
from src.report.cli.cli_report_format import CLIReportFormat
from src.kpis.model import File, Function


class TestCLIReportCognitiveComplexityFileLevelRED(unittest.TestCase):
    """
    RED Phase: Test file-level cognitive complexity in CLI output.

    Expected to FAIL initially - no implementation exists yet.
    """

    def setUp(self):
        self.format_strategy = CLIReportFormat()

    def test_format_file_stats_includes_cognitive_complexity(self):
        """
        Should include 'Cog:' in file stats string when cognitive_complexity KPI exists.

        Expected output format: [C:10, Cog:5, Churn:3, Hotspot:30.0]
        """
        # Arrange: Create mock file with cognitive complexity
        file_obj = MagicMock(spec=File)
        file_obj.name = "test.py"

        # Mock complexity KPI
        complexity_kpi = MagicMock()
        complexity_kpi.value = 10

        # Mock cognitive complexity KPI
        cognitive_kpi = MagicMock()
        cognitive_kpi.value = 5

        # Mock other KPIs
        churn_kpi = MagicMock()
        churn_kpi.value = 3

        hotspot_kpi = MagicMock()
        hotspot_kpi.value = 30.0

        file_obj.kpis = {
            'complexity': complexity_kpi,
            'cognitive_complexity': cognitive_kpi,
            'churn': churn_kpi,
            'hotspot': hotspot_kpi
        }

        # Act: Format file stats
        result = self.format_strategy._format_file_stats(file_obj)

        # Assert: Should contain cognitive complexity
        self.assertIn("Cog:5", result, "Should include cognitive complexity in format 'Cog:5'")
        self.assertIn("C:10", result, "Should still include cyclomatic complexity")
        self.assertIn("Churn:3", result, "Should still include churn")
        self.assertIn("Hotspot:30.0", result, "Should still include hotspot")

    def test_format_file_stats_fallback_when_cog_missing(self):
        """
        Should show 'Cog:?' when cognitive_complexity KPI is missing.

        This ensures backward compatibility with old data.
        """
        # Arrange: Create mock file WITHOUT cognitive complexity
        file_obj = MagicMock(spec=File)
        file_obj.name = "old_file.py"

        complexity_kpi = MagicMock()
        complexity_kpi.value = 8

        file_obj.kpis = {
            'complexity': complexity_kpi,
            'churn': MagicMock(value=2),
            'hotspot': MagicMock(value=16.0)
        }

        # Act
        result = self.format_strategy._format_file_stats(file_obj)

        # Assert: Should show '?' for missing cognitive complexity
        self.assertIn("Cog:?", result, "Should show 'Cog:?' when cognitive_complexity is missing")

    def test_format_file_stats_fallback_when_cog_none(self):
        """
        Should show 'Cog:?' when cognitive_complexity value is None.

        This handles non-Python files where cognitive complexity isn't calculated.
        """
        # Arrange: Create mock file with None cognitive complexity
        file_obj = MagicMock(spec=File)
        file_obj.name = "script.js"

        complexity_kpi = MagicMock()
        complexity_kpi.value = 5

        cognitive_kpi = MagicMock()
        cognitive_kpi.value = None  # Not calculated for JavaScript

        file_obj.kpis = {
            'complexity': complexity_kpi,
            'cognitive_complexity': cognitive_kpi,
            'churn': MagicMock(value=1),
            'hotspot': MagicMock(value=5.0)
        }

        # Act
        result = self.format_strategy._format_file_stats(file_obj)

        # Assert
        self.assertIn("Cog:?", result, "Should show 'Cog:?' when value is None")


class TestCLIReportCognitiveComplexityFunctionLevelRED(unittest.TestCase):
    """
    RED Phase: Test function-level cognitive complexity in CLI output.

    Expected to FAIL initially - no implementation exists yet.
    """

    def setUp(self):
        self.format_strategy = CLIReportFormat()

    def test_print_functions_includes_cognitive_complexity(self):
        """
        Should include 'Cog:' in function stats when cognitive_complexity KPI exists.

        Expected output format: function_name() [C:5, Cog:3]
        """
        # Arrange: Create function with cognitive complexity
        func = MagicMock(spec=Function)
        func.name = "calculate"

        complexity_kpi = MagicMock()
        complexity_kpi.value = 5

        cognitive_kpi = MagicMock()
        cognitive_kpi.value = 3

        func.kpis = {
            'complexity': complexity_kpi,
            'cognitive_complexity': cognitive_kpi
        }

        # Act: Format function (we'll capture print output)
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        self.format_strategy._print_functions([func], prefix="", is_file_last=True)

        sys.stdout = sys.__stdout__
        result = captured_output.getvalue()

        # Assert: Should contain cognitive complexity
        self.assertIn("Cog:3", result, "Should include cognitive complexity 'Cog:3'")
        self.assertIn("C:5", result, "Should still include cyclomatic complexity")
        self.assertIn("calculate()", result, "Should include function name")

    def test_print_functions_fallback_when_cog_missing(self):
        """
        Should show 'Cog:?' when function has no cognitive_complexity KPI.
        """
        # Arrange: Function without cognitive complexity
        func = MagicMock(spec=Function)
        func.name = "old_function"

        complexity_kpi = MagicMock()
        complexity_kpi.value = 2

        func.kpis = {
            'complexity': complexity_kpi
            # No cognitive_complexity
        }

        # Act
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        self.format_strategy._print_functions([func], prefix="", is_file_last=True)

        sys.stdout = sys.__stdout__
        result = captured_output.getvalue()

        # Assert
        self.assertIn("Cog:?", result, "Should show 'Cog:?' when cognitive_complexity is missing")


if __name__ == '__main__':
    unittest.main()
