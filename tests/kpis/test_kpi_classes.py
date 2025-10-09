import unittest
from src.kpis.complexity.kpi import ComplexityKPI
from src.kpis.codechurn.kpi import ChurnKPI
from src.kpis.hotspot.hotspot_kpi import HotspotKPI


class TestKPIClasses(unittest.TestCase):
    def test_complexity_kpi(self):
        kpi = ComplexityKPI()
        kpi.calculate(complexity=7, function_count=3)
        self.assertEqual(kpi.value, 7)
        self.assertEqual(kpi.calculation_values['function_count'], 3)
        self.assertEqual(kpi.name, 'complexity')
        self.assertEqual(kpi.unit, 'points')

    def test_churn_kpi_absolute_and_filename(self):
        churn_data = {
            '/abs/path/to/file.py': 5,
            '/other/file2.py': 2
        }
        kpi = ChurnKPI()
        # Absolute path match
        kpi.calculate(file_path='/abs/path/to/file.py', churn_data=churn_data)
        self.assertEqual(kpi.value, 5)
        # Filename match fallback
        kpi2 = ChurnKPI()
        kpi2.calculate(file_path='file2.py', churn_data=churn_data)
        self.assertEqual(kpi2.value, 2)
        # No match
        kpi3 = ChurnKPI()
        kpi3.calculate(file_path='notfound.py', churn_data=churn_data)
        self.assertEqual(kpi3.value, 0)

    def test_hotspot_kpi(self):
        kpi = HotspotKPI()
        kpi.calculate(complexity=4, churn=3)
        self.assertEqual(kpi.value, 12)
        self.assertEqual(kpi.calculation_values['complexity'], 4)
        self.assertEqual(kpi.calculation_values['churn'], 3)
        # None if missing args
        kpi2 = HotspotKPI()
        kpi2.calculate()
        self.assertIsNone(kpi2.value)


if __name__ == '__main__':
    unittest.main()
