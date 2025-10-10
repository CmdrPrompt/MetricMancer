"""
Tests for fallback KPI classes that handle calculation errors gracefully.
"""
import unittest
from src.kpis.codeownership.fallback_kpi import FallbackCodeOwnershipKPI
from src.kpis.sharedcodeownership.fallback_kpi import (
    FallbackSharedOwnershipKPI
)


class TestFallbackKPIs(unittest.TestCase):

    def test_fallback_code_ownership_kpi_creation(self):
        """Test FallbackCodeOwnershipKPI creation with error message."""
        error_message = "File not found in git repository"
        kpi = FallbackCodeOwnershipKPI(error_message)

        self.assertEqual(kpi.name, "Code Ownership")
        self.assertIn("error", kpi.value)
        self.assertIn(error_message, kpi.value["error"])
        self.assertEqual(
            kpi.description,
            "Proportion of code lines owned by each author (via git blame)"
        )

    def test_fallback_code_ownership_kpi_calculate(self):
        """Test that calculate method returns the error value."""
        error_message = "Git blame failed"
        kpi = FallbackCodeOwnershipKPI(error_message)

        result = kpi.calculate()
        self.assertEqual(result, kpi.value)

    def test_fallback_shared_ownership_kpi_creation(self):
        """Test FallbackSharedOwnershipKPI creation with error message."""
        error_message = "Repository access denied"
        kpi = FallbackSharedOwnershipKPI(error_message)

        self.assertEqual(kpi.name, "Shared Ownership")
        self.assertIn("error", kpi.value)
        self.assertIn(error_message, kpi.value["error"])
        self.assertEqual(
            kpi.description,
            "Number of significant authors per file (ownership > threshold)"
        )

    def test_fallback_shared_ownership_kpi_calculate(self):
        """Test that calculate method returns the error value."""
        error_message = "No git history available"
        kpi = FallbackSharedOwnershipKPI(error_message)

        result = kpi.calculate()
        self.assertEqual(result, kpi.value)

    def test_fallback_kpis_with_complex_error_messages(self):
        """Test fallback KPIs with complex error messages."""
        complex_error = ("Failed to parse: 'file with spaces.py' - "
                         "Permission denied (errno: 13)")

        ownership_kpi = FallbackCodeOwnershipKPI(complex_error)
        shared_kpi = FallbackSharedOwnershipKPI(complex_error)

        self.assertIn(complex_error, ownership_kpi.value["error"])
        self.assertIn(complex_error, shared_kpi.value["error"])


if __name__ == '__main__':
    unittest.main()
