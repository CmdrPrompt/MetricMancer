"""Tests for centralized default values."""

import unittest

from src.config.defaults import Defaults


class TestDefaults(unittest.TestCase):
    """Test cases for the Defaults class."""

    def test_threshold_defaults_are_numeric(self):
        """Test that threshold defaults are proper numeric values."""
        self.assertIsInstance(Defaults.THRESHOLD_LOW, (int, float))
        self.assertIsInstance(Defaults.THRESHOLD_HIGH, (int, float))
        self.assertIsInstance(Defaults.EXTREME_COMPLEXITY_THRESHOLD, int)

    def test_threshold_low_less_than_high(self):
        """Test that THRESHOLD_LOW is less than THRESHOLD_HIGH."""
        self.assertLess(Defaults.THRESHOLD_LOW, Defaults.THRESHOLD_HIGH)

    def test_output_defaults_are_strings(self):
        """Test that output defaults are strings."""
        self.assertIsInstance(Defaults.OUTPUT_FORMAT, str)
        self.assertIsInstance(Defaults.REPORT_FOLDER, str)
        self.assertIsInstance(Defaults.LEVEL, str)

    def test_hotspot_threshold_is_positive(self):
        """Test that HOTSPOT_THRESHOLD is a positive integer."""
        self.assertIsInstance(Defaults.HOTSPOT_THRESHOLD, int)
        self.assertGreater(Defaults.HOTSPOT_THRESHOLD, 0)

    def test_review_defaults_are_strings(self):
        """Test that review defaults are strings."""
        self.assertIsInstance(Defaults.REVIEW_OUTPUT, str)
        self.assertIsInstance(Defaults.REVIEW_BASE_BRANCH, str)

    def test_churn_period_is_positive(self):
        """Test that CHURN_PERIOD is a positive integer."""
        self.assertIsInstance(Defaults.CHURN_PERIOD, int)
        self.assertGreater(Defaults.CHURN_PERIOD, 0)

    def test_delta_defaults_are_strings(self):
        """Test that delta defaults are strings."""
        self.assertIsInstance(Defaults.DELTA_BASE_BRANCH, str)
        self.assertIsInstance(Defaults.DELTA_OUTPUT, str)

    def test_default_values_match_documented_values(self):
        """Test that default values match the documented/expected values."""
        # These are the expected values based on documentation
        self.assertEqual(Defaults.THRESHOLD_LOW, 10.0)
        self.assertEqual(Defaults.THRESHOLD_HIGH, 20.0)
        self.assertEqual(Defaults.EXTREME_COMPLEXITY_THRESHOLD, 100)
        self.assertEqual(Defaults.OUTPUT_FORMAT, "summary")
        self.assertEqual(Defaults.REPORT_FOLDER, "output")
        self.assertEqual(Defaults.LEVEL, "file")
        self.assertEqual(Defaults.HOTSPOT_THRESHOLD, 50)
        self.assertEqual(Defaults.REVIEW_OUTPUT, "review_strategy.md")
        self.assertEqual(Defaults.REVIEW_BASE_BRANCH, "main")
        self.assertEqual(Defaults.CHURN_PERIOD, 30)
        self.assertEqual(Defaults.DELTA_BASE_BRANCH, "main")
        self.assertEqual(Defaults.DELTA_OUTPUT, "delta_review.md")


class TestDefaultsImmutability(unittest.TestCase):
    """Test that Defaults values behave like constants."""

    def test_defaults_are_class_attributes(self):
        """Test that all defaults are class attributes, not instance attributes."""
        # All attributes should be accessible without instantiation
        attrs = [
            'THRESHOLD_LOW', 'THRESHOLD_HIGH', 'EXTREME_COMPLEXITY_THRESHOLD',
            'OUTPUT_FORMAT', 'REPORT_FOLDER', 'LEVEL',
            'HOTSPOT_THRESHOLD',
            'REVIEW_OUTPUT', 'REVIEW_BASE_BRANCH',
            'CHURN_PERIOD',
            'DELTA_BASE_BRANCH', 'DELTA_OUTPUT'
        ]
        for attr in attrs:
            self.assertTrue(
                hasattr(Defaults, attr),
                f"Defaults class should have attribute {attr}"
            )


if __name__ == '__main__':
    unittest.main()
