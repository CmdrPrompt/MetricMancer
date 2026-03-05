"""Unit tests for scripts/check_licenses.py."""

import unittest
from unittest.mock import patch

from scripts import check_licenses


class TestLicenseNormalization(unittest.TestCase):
    """Tests for license normalization and expression parsing helpers."""

    def test_normalize_license_name_maps_known_alias(self):
        self.assertEqual(
            check_licenses.normalize_license_name('Apache Software License'),
            'Apache-2.0'
        )

    def test_split_license_expression_handles_spdx_operators(self):
        parts = check_licenses.split_license_expression('MIT OR Apache-2.0')
        self.assertEqual(parts, ['MIT', 'Apache-2.0'])

    def test_split_license_expression_handles_parenthesized_license(self):
        parts = check_licenses.split_license_expression('Mozilla Public License 2.0 (MPL 2.0)')
        self.assertEqual(parts, ['MPL-2.0'])

    def test_split_license_expression_handles_and_with_parentheses(self):
        parts = check_licenses.split_license_expression('(MIT) AND (BSD-3-Clause)')
        self.assertEqual(parts, ['MIT', 'BSD-3-Clause'])

    def test_is_allowed_license_term_uses_exact_and_marker_match(self):
        self.assertTrue(check_licenses.is_allowed_license_term('PSF-2.0'))
        self.assertTrue(check_licenses.is_allowed_license_term('Apache-2.0 OR BSD-2-Clause'))
        self.assertFalse(check_licenses.is_allowed_license_term('Custom-Internal-License'))


class TestCheckLicense(unittest.TestCase):
    """Tests for license compliance classification behavior."""

    def test_check_license_rejects_forbidden_license(self):
        allowed, reason = check_licenses.check_license('badpkg', 'GPLv3')

        self.assertFalse(allowed)
        self.assertIn('forbidden', reason.lower())

    def test_check_license_allows_multi_license_if_any_term_is_permissive(self):
        allowed, reason = check_licenses.check_license('somepkg', 'MIT OR Proprietary')

        self.assertTrue(allowed)
        self.assertIn('Permissive license', reason)

    def test_check_license_forbidden_takes_precedence_over_allowed_term(self):
        allowed, reason = check_licenses.check_license('mixedpkg', 'MIT AND GPL')

        self.assertFalse(allowed)
        self.assertIn('forbidden', reason.lower())

    def test_check_license_local_package_unknown_is_allowed(self):
        allowed, reason = check_licenses.check_license('metricmancer', 'UNKNOWN')

        self.assertTrue(allowed)
        self.assertIn('Local development package', reason)

    @patch('scripts.check_licenses.get_license_from_pypi')
    def test_check_license_unknown_uses_pypi_and_allows_permissive(self, mock_get_license):
        mock_get_license.return_value = ('Apache License 2.0', 'https://github.com/example/repo')

        allowed, reason = check_licenses.check_license('remote_pkg', 'UNKNOWN')

        self.assertTrue(allowed)
        self.assertIn('Permissive license from PyPI', reason)

    @patch('scripts.check_licenses.get_license_from_pypi')
    def test_check_license_unknown_uses_pypi_and_flags_review(self, mock_get_license):
        mock_get_license.return_value = ('Commercial-Only', 'https://github.com/example/repo')

        allowed, reason = check_licenses.check_license('remote_pkg', 'UNKNOWN')

        self.assertIsNone(allowed)
        self.assertIn('needs review', reason)

    @patch('scripts.check_licenses.get_license_from_pypi')
    def test_check_license_unknown_without_pypi_data_flags_review(self, mock_get_license):
        mock_get_license.return_value = ('', '')

        allowed, reason = check_licenses.check_license('remote_pkg', 'UNKNOWN')

        self.assertIsNone(allowed)
        self.assertIn('UNKNOWN', reason)


if __name__ == '__main__':
    unittest.main()
