"""
Integration tests for churn configuration in the Analyzer.

Tests that the Analyzer properly accepts and uses churn_period_days parameter.
"""

import unittest
from src.app import Analyzer
from src.languages.config import Config


class TestChurnConfiguration(unittest.TestCase):
    """
    Tests for churn period configuration in Analyzer.
    """

    def setUp(self):
        self.languages_config = Config()

    def test_different_time_periods_should_be_configurable(self):
        """
        Tests that different time periods can be configured.
        Uses churn_period_days parameter.
        """
        # Test that Analyzer accepts churn_period_days parameter
        analyzer_90d = Analyzer(self.languages_config.languages, churn_period_days=90)
        analyzer_180d = Analyzer(self.languages_config.languages, churn_period_days=180)
        analyzer_365d = Analyzer(self.languages_config.languages, churn_period_days=365)

        # Verify the parameter is set correctly
        self.assertEqual(analyzer_90d.churn_period_days, 90)
        self.assertEqual(analyzer_180d.churn_period_days, 180)
        self.assertEqual(analyzer_365d.churn_period_days, 365)

    def test_default_churn_period(self):
        """Test that default churn period is 30 days."""
        analyzer = Analyzer(self.languages_config.languages)
        self.assertEqual(analyzer.churn_period_days, 30)


if __name__ == '__main__':
    unittest.main()
