"""
RED Phase: Tests for Cognitive Complexity in Quick Wins Report

Following TDD RED-GREEN-REFACTOR:
- 🔴 RED: These tests SHOULD FAIL initially
- 🟢 GREEN: Implement minimal code to make them pass
- 🔵 REFACTOR: Clean up implementation

Tests verify:
1. Cognitive complexity contributes to impact score
2. Cognitive complexity appears in action recommendations
3. High cognitive complexity triggers specific actions
4. Quick wins data includes cognitive complexity values
"""
import unittest
from unittest.mock import MagicMock
from src.report.cli.cli_quick_wins_format import CLIQuickWinsFormat
from src.kpis.model import File


class TestQuickWinsCognitiveComplexityImpactRED(unittest.TestCase):
    """
    RED Phase: Test that cognitive complexity affects impact scoring.

    Expected to FAIL initially - no implementation exists yet.
    """

    def setUp(self):
        self.formatter = CLIQuickWinsFormat()

    def test_high_cognitive_complexity_increases_impact(self):
        """
        Should increase impact score when cognitive complexity is high.

        A file with high cognitive complexity (e.g., >25) should get bonus
        impact points because it's harder to understand and more error-prone.
        """
        # Current implementation only considers cyclomatic complexity
        # Expected: cognitive_complexity should add to impact score

        # Arrange: File with high cognitive complexity
        complexity = 15  # Moderate cyclomatic
        cognitive_complexity = 30  # High cognitive (nested code)
        churn = 5
        hotspot = 100

        # Act: Calculate impact (method signature may need updating)
        impact = self.formatter._calculate_impact(
            complexity=complexity,
            churn=churn,
            hotspot=hotspot,
            cognitive_complexity=cognitive_complexity  # NEW parameter
        )

        # Assert: Should get bonus points for high cognitive complexity
        # Without cognitive: ~3 points (hotspot:100=2, complexity:15=1)
        # With cognitive:30: ~5 points (hotspot:100=2, complexity:15=1, cognitive:30=2)
        self.assertGreaterEqual(impact, 5,
                                "High cognitive complexity should increase impact score")

    def test_low_cognitive_vs_high_cyclomatic(self):
        """
        Should differentiate between high cyclomatic with low cognitive complexity.

        Example: Flat structure with many simple if-statements
        - High cyclomatic (many branches)
        - Low cognitive (easy to understand)
        - Should have moderate impact (not critical)
        """
        # Arrange: High cyclomatic, low cognitive (flat structure)
        complexity = 25  # High cyclomatic (many branches)
        cognitive_complexity = 8  # Low cognitive (flat, easy to read)
        churn = 3
        hotspot = 75

        # Act
        impact = self.formatter._calculate_impact(
            complexity=complexity,
            churn=churn,
            hotspot=hotspot,
            cognitive_complexity=cognitive_complexity
        )

        # Assert: Moderate impact (not as critical as high cognitive)
        # Should be around 3-4 points, not 5+
        self.assertLess(impact, 5,
                        "Low cognitive complexity should moderate the impact score")


class TestQuickWinsCognitiveComplexityActionsRED(unittest.TestCase):
    """
    RED Phase: Test that cognitive complexity affects action recommendations.

    Expected to FAIL initially - no cognitive-specific actions exist yet.
    """

    def setUp(self):
        self.formatter = CLIQuickWinsFormat()

    def test_high_cognitive_complexity_suggests_reduce_nesting(self):
        """
        Should recommend "Reduce nesting" when cognitive complexity is high.

        High cognitive complexity usually indicates deeply nested code.
        The action should specifically mention reducing nesting.
        """
        # Arrange: File with high cognitive complexity
        file_obj = MagicMock(spec=File)
        file_obj.name = "complex_nested.py"
        file_obj.functions = []
        file_obj.kpis = {
            'complexity': MagicMock(value=20),
            'cognitive_complexity': MagicMock(value=35),  # Very high
            'churn': MagicMock(value=5),
            'hotspot': MagicMock(value=100),
            'Shared Code Ownership': None
        }

        complexity = 20
        cognitive_complexity = 35
        churn = 5
        hotspot = 100

        # Act: Determine action (method signature may need updating)
        action_type, action_desc, reason = self.formatter._determine_action(
            file_obj=file_obj,
            complexity=complexity,
            churn=churn,
            hotspot=hotspot,
            ownership_kpi=None,
            shared_kpi=None,
            cognitive_complexity=cognitive_complexity  # NEW parameter
        )

        # Assert: Should recommend reducing nesting
        self.assertEqual(action_type, 'Reduce Nesting',
                         "High cognitive complexity should trigger 'Reduce Nesting' action")
        self.assertIn('nesting', action_desc.lower(),
                      "Action description should mention nesting")
        self.assertIn('cognitive', reason.lower(),
                      "Reason should mention cognitive complexity")

    def test_high_cognitive_includes_value_in_reason(self):
        """
        Should include cognitive complexity value in the reason string.

        Example: "High cognitive complexity (CogC:35)"
        """
        # Arrange
        file_obj = MagicMock(spec=File)
        file_obj.name = "test.py"
        file_obj.functions = []
        file_obj.kpis = {
            'complexity': MagicMock(value=15),
            'cognitive_complexity': MagicMock(value=28),
            'Shared Code Ownership': None
        }

        # Act
        _, _, reason = self.formatter._determine_action(
            file_obj=file_obj,
            complexity=15,
            churn=5,
            hotspot=75,
            ownership_kpi=None,
            shared_kpi=None,
            cognitive_complexity=28
        )

        # Assert: Reason should include cognitive complexity value
        self.assertIn('28', reason,
                      "Reason should include cognitive complexity value")
        self.assertIn('Cog', reason,
                      "Reason should use 'Cog' abbreviation for cognitive complexity")


class TestQuickWinsDataIncludesCognitiveRED(unittest.TestCase):
    """
    RED Phase: Test that quick wins data structure includes cognitive complexity.

    Expected to FAIL initially - data structure doesn't include it yet.
    """

    def setUp(self):
        self.formatter = CLIQuickWinsFormat()

    def test_quick_win_dict_includes_cognitive_complexity(self):
        """
        Should include 'cognitive_complexity' in quick wins data dict.

        Each quick win entry should have cognitive_complexity alongside
        complexity, churn, and hotspot for complete analysis.
        """
        # Arrange: File with all KPIs including cognitive complexity
        file_obj = MagicMock(spec=File)
        file_obj.name = "test.py"
        file_obj.file_path = "src/test.py"
        file_obj.functions = []

        # Create proper KPI mocks
        complexity_kpi = MagicMock()
        complexity_kpi.value = 15

        cognitive_kpi = MagicMock()
        cognitive_kpi.value = 22

        churn_kpi = MagicMock()
        churn_kpi.value = 8

        hotspot_kpi = MagicMock()
        hotspot_kpi.value = 120

        ownership_kpi = MagicMock()
        ownership_kpi.value = {'alice': 60, 'bob': 40}  # Git tracked

        file_obj.kpis = {
            'complexity': complexity_kpi,
            'cognitive_complexity': cognitive_kpi,
            'churn': churn_kpi,
            'hotspot': hotspot_kpi,
            'Code Ownership': ownership_kpi,
            'Shared Code Ownership': None
        }

        # Act: Calculate quick wins for this file
        quick_wins = self.formatter._calculate_quick_wins([file_obj])

        # Assert: Quick win entry should include cognitive_complexity
        self.assertGreater(len(quick_wins), 0, "Should have at least one quick win")

        first_win = quick_wins[0]
        self.assertIn('cognitive_complexity', first_win,
                      "Quick win dict should include 'cognitive_complexity' key")
        self.assertEqual(first_win['cognitive_complexity'], 22,
                         "Cognitive complexity value should match KPI value")


if __name__ == '__main__':
    unittest.main()
