import unittest
from src.kpis.hotspot.hotspot_kpi import HotspotKPI


class TestHotspotKPIEdgeCases(unittest.TestCase):
    def test_calculate_with_none(self):
        kpi = HotspotKPI()
        result = kpi.calculate(complexity=None, churn=None)
        self.assertIsNone(result.value)
        self.assertEqual(result.calculation_values, {})

    def test_calculate_with_only_complexity(self):
        kpi = HotspotKPI()
        result = kpi.calculate(complexity=5, churn=None)
        self.assertIsNone(result.value)
        self.assertEqual(result.calculation_values, {})

    def test_calculate_with_only_churn(self):
        kpi = HotspotKPI()
        result = kpi.calculate(complexity=None, churn=3)
        self.assertIsNone(result.value)
        self.assertEqual(result.calculation_values, {})

    def test_calculate_with_zero(self):
        kpi = HotspotKPI()
        result = kpi.calculate(complexity=0, churn=0)
        self.assertEqual(result.value, 0)
        self.assertEqual(result.calculation_values, {"complexity": 0, "churn": 0})

    def test_calculate_with_negative(self):
        kpi = HotspotKPI()
        result = kpi.calculate(complexity=-2, churn=3)
        self.assertEqual(result.value, -6)
        self.assertEqual(result.calculation_values, {"complexity": -2, "churn": 3})


if __name__ == "__main__":
    unittest.main()
