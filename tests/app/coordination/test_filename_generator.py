"""
Tests for FileNameGenerator

Tests filename generation logic for different formats and repository configurations.
"""
import unittest
from src.app.coordination.filename_generator import FileNameGenerator


class MockRepoInfo:
    """Mock repository info for testing."""

    def __init__(self, name):
        self.repo_name = name


class TestFileNameGenerator(unittest.TestCase):
    """Test FileNameGenerator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = FileNameGenerator(
            "complexity_report.html",
            using_output_formats_flag=False
        )

    def test_get_base_and_extension_simple_format(self):
        """Test base and extension for simple formats."""
        base, ext = self.generator.get_base_and_extension('json', is_multi_format=False)
        self.assertEqual(base, 'complexity_report')
        self.assertEqual(ext, '.json')

    def test_get_base_and_extension_cli_format_single(self):
        """Test base and extension for CLI format with single output."""
        base, ext = self.generator.get_base_and_extension('summary', is_multi_format=False)
        self.assertEqual(base, 'complexity_report')
        self.assertEqual(ext, '.html')

    def test_get_base_and_extension_cli_format_multi(self):
        """Test base and extension for CLI format with multi-format."""
        base, ext = self.generator.get_base_and_extension('summary', is_multi_format=True)
        self.assertEqual(base, 'summary_report')
        self.assertEqual(ext, '.md')

        base, ext = self.generator.get_base_and_extension('quick-wins', is_multi_format=True)
        self.assertEqual(base, 'quick_wins_report')
        self.assertEqual(ext, '.md')

    def test_get_base_and_extension_cli_format_with_flag(self):
        """Test base and extension for CLI format with output-formats flag."""
        generator = FileNameGenerator(
            "complexity_report.html",
            using_output_formats_flag=True
        )

        base, ext = generator.get_base_and_extension('summary', is_multi_format=False)
        self.assertEqual(base, 'summary_report')
        self.assertEqual(ext, '.md')

    def test_generate_filename_single_repo(self):
        """Test filename generation for single repository."""
        filename = self.generator.generate_filename('report', '.html', 0, 1)
        self.assertEqual(filename, 'report.html')

    def test_generate_filename_multi_repo(self):
        """Test filename generation for multiple repositories."""
        filename = self.generator.generate_filename('report', '.html', 0, 3)
        self.assertEqual(filename, 'report_1.html')

        filename = self.generator.generate_filename('report', '.html', 1, 3)
        self.assertEqual(filename, 'report_2.html')

        filename = self.generator.generate_filename('report', '.html', 2, 3)
        self.assertEqual(filename, 'report_3.html')

    def test_generate_with_links_single_repo(self):
        """Test filename and links generation for single repository."""
        report_links = []

        filename, links = self.generator.generate_with_links(
            'report', '.html', 0, 1, report_links
        )

        self.assertEqual(filename, 'report.html')
        self.assertEqual(links, [])

    def test_generate_with_links_multi_repo(self):
        """Test filename and links generation for multiple repositories."""
        report_links = [
            {'href': 'report_1.html', 'name': 'Repo 1', 'selected': False},
            {'href': 'report_2.html', 'name': 'Repo 2', 'selected': False},
            {'href': 'report_3.html', 'name': 'Repo 3', 'selected': False}
        ]

        filename, links = self.generator.generate_with_links(
            'report', '.html', 0, 3, report_links
        )

        # Check filename
        self.assertEqual(filename, 'report_1.html')

        # Check that current report is marked as selected
        self.assertTrue(report_links[0]['selected'])
        self.assertFalse(report_links[1]['selected'])
        self.assertFalse(report_links[2]['selected'])

        # Check that current report is excluded from returned links
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]['href'], 'report_2.html')
        self.assertEqual(links[1]['href'], 'report_3.html')

    def test_prepare_report_links_single_repo(self):
        """Test report links preparation for single repository."""
        repo_infos = [MockRepoInfo('MyRepo')]

        links = FileNameGenerator.prepare_report_links(repo_infos, 'report.html')

        self.assertEqual(len(links), 0)

    def test_prepare_report_links_multi_repo(self):
        """Test report links preparation for multiple repositories."""
        repo_infos = [
            MockRepoInfo('Repo1'),
            MockRepoInfo('Repo2'),
            MockRepoInfo('Repo3')
        ]

        links = FileNameGenerator.prepare_report_links(repo_infos, 'report.html')

        self.assertEqual(len(links), 3)
        self.assertEqual(links[0]['href'], 'report_1.html')
        self.assertEqual(links[0]['name'], 'Repo1')
        self.assertFalse(links[0]['selected'])

        self.assertEqual(links[1]['href'], 'report_2.html')
        self.assertEqual(links[1]['name'], 'Repo2')

        self.assertEqual(links[2]['href'], 'report_3.html')
        self.assertEqual(links[2]['name'], 'Repo3')

    def test_prepare_report_links_no_repo_name(self):
        """Test report links preparation when repo has no name attribute."""
        class MockRepoNoName:
            pass

        repo_infos = [MockRepoNoName(), MockRepoNoName()]

        links = FileNameGenerator.prepare_report_links(repo_infos, 'report.html')

        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]['name'], 'Repo 1')
        self.assertEqual(links[1]['name'], 'Repo 2')


if __name__ == '__main__':
    unittest.main()
