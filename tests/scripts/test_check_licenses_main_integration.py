"""Integration-style tests for scripts/check_licenses.py main flow."""

import json
import unittest
from unittest.mock import patch, Mock

from scripts import check_licenses


class TestCheckLicensesMainIntegration(unittest.TestCase):
    """Test main() end-to-end behavior with mocked dependency inputs."""

    @patch('scripts.check_licenses.get_license_from_pypi', return_value=('', ''))
    @patch('scripts.check_licenses.get_pyproject_dependencies')
    @patch('scripts.check_licenses.get_installed_licenses')
    @patch('scripts.check_licenses.subprocess.run')
    def test_main_exits_zero_when_all_dependencies_are_permissive(
        self,
        mock_run,
        mock_get_installed,
        mock_get_deps,
        _mock_get_pypi,
    ):
        """main() should exit 0 when all packages are allowed."""
        mock_get_installed.return_value = [
            {'Name': 'metricmancer', 'Version': '3.1.0', 'License': 'MIT License'},
            {'Name': 'goodpkg', 'Version': '1.0.0', 'License': 'MIT'},
        ]
        mock_get_deps.return_value = ({'goodpkg'}, set())
        mock_run.return_value = Mock(stdout=json.dumps([]))

        with self.assertRaises(SystemExit) as exc:
            check_licenses.main()

        self.assertEqual(exc.exception.code, 0)

    @patch('scripts.check_licenses.get_license_from_pypi', return_value=('', ''))
    @patch('scripts.check_licenses.get_pyproject_dependencies')
    @patch('scripts.check_licenses.get_installed_licenses')
    @patch('scripts.check_licenses.subprocess.run')
    def test_main_exits_one_when_review_package_exists(
        self,
        mock_run,
        mock_get_installed,
        mock_get_deps,
        _mock_get_pypi,
    ):
        """main() should exit 1 when a package requires manual review."""
        mock_get_installed.return_value = [
            {'Name': 'metricmancer', 'Version': '3.1.0', 'License': 'MIT License'},
            {'Name': 'reviewpkg', 'Version': '2.0.0', 'License': 'Custom-Internal-License'},
        ]
        mock_get_deps.return_value = ({'reviewpkg'}, set())
        mock_run.return_value = Mock(stdout=json.dumps([]))

        with self.assertRaises(SystemExit) as exc:
            check_licenses.main()

        self.assertEqual(exc.exception.code, 1)

    @patch('scripts.check_licenses.get_license_from_pypi', return_value=('', ''))
    @patch('scripts.check_licenses.get_pyproject_dependencies')
    @patch('scripts.check_licenses.get_installed_licenses')
    @patch('scripts.check_licenses.subprocess.run')
    def test_main_exits_one_when_forbidden_license_exists(
        self,
        mock_run,
        mock_get_installed,
        mock_get_deps,
        _mock_get_pypi,
    ):
        """main() should exit 1 when a forbidden/copyleft license is found."""
        mock_get_installed.return_value = [
            {'Name': 'metricmancer', 'Version': '3.1.0', 'License': 'MIT License'},
            {'Name': 'badpkg', 'Version': '9.9.9', 'License': 'GPLv3'},
        ]
        mock_get_deps.return_value = ({'badpkg'}, set())
        mock_run.return_value = Mock(stdout=json.dumps([]))

        with self.assertRaises(SystemExit) as exc:
            check_licenses.main()

        self.assertEqual(exc.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
