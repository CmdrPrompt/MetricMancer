import unittest
from unittest.mock import patch, MagicMock
from src.kpis.sharedcodeownership.shared_code_ownership import SharedOwnershipKPI


class TestSharedOwnershipKPI(unittest.TestCase):
    @patch('src.kpis.sharedcodeownership.shared_code_ownership.CodeOwnershipKPI')
    def test_shared_ownership_basic(self, mock_code_ownership_kpi):
        # Mock the class constructor to return a mock instance with .value attribute
        mock_instance = MagicMock()
        mock_instance.value = {'Alice': 60.0, 'Bob': 30.0, 'Carol': 10.0}
        mock_code_ownership_kpi.return_value = mock_instance
        
        kpi = SharedOwnershipKPI('dummy.py', '/repo', threshold=20.0)
        self.assertEqual(kpi.value['num_significant_authors'], 2)
        self.assertIn('Alice', kpi.value['authors'])
        self.assertIn('Bob', kpi.value['authors'])
        self.assertNotIn('Carol', kpi.value['authors'])
        self.assertEqual(kpi.value['threshold'], 20.0)

    @patch('src.kpis.sharedcodeownership.shared_code_ownership.CodeOwnershipKPI')
    def test_shared_ownership_all_below_threshold(self, mock_code_ownership_kpi):
        # All authors below threshold
        mock_instance = MagicMock()
        mock_instance.value = {'Alice': 10.0, 'Bob': 15.0}
        mock_code_ownership_kpi.return_value = mock_instance
        
        kpi = SharedOwnershipKPI('dummy.py', '/repo', threshold=20.0)
        self.assertEqual(kpi.value['num_significant_authors'], 0)
        self.assertEqual(kpi.value['authors'], [])
        self.assertEqual(kpi.value['threshold'], 20.0)

    @patch('src.kpis.sharedcodeownership.shared_code_ownership.CodeOwnershipKPI')
    def test_shared_ownership_all_above_threshold(self, mock_code_ownership_kpi):
        # All authors above threshold
        mock_instance = MagicMock()
        mock_instance.value = {'Alice': 50.0, 'Bob': 50.0}
        mock_code_ownership_kpi.return_value = mock_instance
        
        kpi = SharedOwnershipKPI('dummy.py', '/repo', threshold=20.0)
        self.assertEqual(kpi.value['num_significant_authors'], 2)
        self.assertCountEqual(kpi.value['authors'], ['Alice', 'Bob'])

    def test_shared_ownership_with_precomputed_data(self):
        # Pass precomputed ownership data directly
        ownership = {'Alice': 40.0, 'Bob': 25.0, 'Carol': 35.0}
        kpi = SharedOwnershipKPI('dummy.py', '/repo', threshold=30.0, ownership_data=ownership)
        self.assertEqual(kpi.value['num_significant_authors'], 2)
        self.assertCountEqual(kpi.value['authors'], ['Alice', 'Carol'])

    def test_shared_ownership_na(self):
        # Ownership is not available (e.g., file not tracked)
        kpi = SharedOwnershipKPI('dummy.py', '/repo', ownership_data={'ownership': 'N/A'})
        self.assertEqual(kpi.value, {'shared_ownership': 'N/A'})


if __name__ == '__main__':
    unittest.main()
