import unittest
import os
from src.kpis.codechurn.kpi import ChurnKPI


def make_churn_data_for_test():
    # Simulate churn_data as produced by CodeChurnAnalyzer (absolute paths)
    return {
        os.path.abspath("/repo/file1.py"): 5,
        os.path.abspath("/repo/file2.py"): 3,
    }


class TestChurnKPIPathMismatch(unittest.TestCase):

    def test_churn_lookup_with_relative_path_should_match_absolute(self):
        churn_data = make_churn_data_for_test()
        # Simulate Analyzer using str(file_path) (relative path)
        rel_path = "file1.py"
        # Should still find the churn value if implementation is robust
        churn_kpi = ChurnKPI().calculate(file_path=rel_path, churn_data=churn_data)
        self.assertEqual(
            churn_kpi.value, 5,
            "ChurnKPI should return correct churn even if file_path is relative and churn_data uses absolute paths. This test should FAIL if implementation is not robust."
        )

    def test_churn_lookup_with_absolute_path(self):
        churn_data = make_churn_data_for_test()
        abs_path = os.path.abspath("/repo/file1.py")
        churn_kpi = ChurnKPI().calculate(file_path=abs_path, churn_data=churn_data)
        self.assertEqual(churn_kpi.value, 5, "ChurnKPI should return correct churn when file_path is absolute and matches churn_data")


if __name__ == "__main__":
    unittest.main()
