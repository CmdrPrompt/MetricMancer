"""
RED Phase: Tests for HTML Tabbed Interface

Following TDD RED-GREEN-REFACTOR:
- 🔴 RED: These tests SHOULD FAIL initially
- 🟢 GREEN: Implement minimal code to make them pass
- 🔵 REFACTOR: Clean up implementation

Tests verify:
1. HTML report contains tabbed navigation
2. Tab structure includes all required tabs
3. Cognitive complexity appears in relevant tabs
4. JavaScript tab switching works
"""
import unittest
from unittest.mock import MagicMock, Mock
from src.report.report_renderer import ReportRenderer
from src.kpis.model import RepoInfo, File


def create_test_repo_info(repo_name='test-repo', **kwargs):
    """Helper to create RepoInfo with proper constructor args."""
    return RepoInfo(
        dir_name=kwargs.get('dir_name', repo_name),
        scan_dir_path=kwargs.get('scan_dir_path', '.'),
        repo_root_path=kwargs.get('repo_root_path', '/test'),
        repo_name=repo_name,
        files=kwargs.get('files', {}),
        scan_dirs=kwargs.get('scan_dirs', {}),
        kpis=kwargs.get('kpis', {})
    )


class TestHTMLTabbedStructureRED(unittest.TestCase):
    """
    RED Phase: Test that HTML report has tabbed structure.

    Expected to FAIL initially - tabs don't exist yet.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.renderer = ReportRenderer(
            template_dir='src/report/templates',
            template_file='report.html',
            threshold_low=10.0,
            threshold_high=20.0
        )

    def test_html_contains_tab_navigation(self):
        """
        Should include tab navigation buttons in HTML output.

        Expected structure:
        <div class="tabs">
          <button class="tab-btn active" data-tab="overview">Overview</button>
          <button class="tab-btn" data-tab="tree">File Tree</button>
          ...
        </div>
        """
        # Arrange: Create minimal RepoInfo
        repo_info = create_test_repo_info()

        # Act: Render HTML
        html = self.renderer.render(repo_info=repo_info)

        # Assert: Should contain tab navigation
        self.assertIn('tab-btn', html,
                     "HTML should contain tab buttons")
        self.assertIn('data-tab=', html,
                     "Tab buttons should have data-tab attributes")

    def test_html_contains_overview_tab(self):
        """Should include Overview tab button."""
        repo_info = create_test_repo_info(repo_name='test')
        html = self.renderer.render(repo_info=repo_info)
        self.assertIn('overview', html.lower(),
                     "Should have Overview tab")

    def test_html_contains_tree_tab(self):
        """Should include File Tree tab button."""
        repo_info = create_test_repo_info(repo_name='test')
        html = self.renderer.render(repo_info=repo_info)
        self.assertIn('tree', html.lower(),
                     "Should have File Tree tab")

    def test_html_contains_quickwins_tab(self):
        """Should include Quick Wins tab button."""
        repo_info = create_test_repo_info(repo_name='test')
        html = self.renderer.render(repo_info=repo_info)
        self.assertIn('quick', html.lower(),
                     "Should have Quick Wins tab")


class TestHTMLCognitiveComplexityInTreeRED(unittest.TestCase):
    """
    RED Phase: Test that cognitive complexity appears in File Tree tab.

    Expected to FAIL initially - tree doesn't show Cog: yet.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.renderer = ReportRenderer(
            template_dir='src/report/templates',
            template_file='report.html'
        )

    def test_file_tree_includes_cognitive_complexity(self):
        """
        Should show cognitive complexity in file stats.

        Expected format: [C:10, Cog:5, Churn:3, Hotspot:30.0]
        """
        # Arrange: File with cognitive complexity
        file_obj = File(name='test.py', file_path='/test/test.py')
        file_obj.functions = []

        # Add KPIs including cognitive complexity
        file_obj.kpis = {
            'complexity': Mock(value=10),
            'cognitive_complexity': Mock(value=5),
            'churn': Mock(value=3),
            'hotspot': Mock(value=30.0),
            'Code Ownership': Mock(value={'alice': 100})
        }

        # Create RepoInfo with file
        repo_info = create_test_repo_info(files={'test.py': file_obj})

        # Act: Render HTML
        html = self.renderer.render(repo_info=repo_info)

        # Assert: Should show Cog:5 in the tree
        self.assertIn('Cog:', html,
                     "File tree should show cognitive complexity with 'Cog:' label")
        self.assertIn('C:', html,
                     "Should still show cyclomatic complexity")


class TestHTMLTabContentStructureRED(unittest.TestCase):
    """
    RED Phase: Test that tab content areas exist.

    Expected to FAIL initially - no tab content divs yet.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.renderer = ReportRenderer(
            template_dir='src/report/templates',
            template_file='report.html'
        )

    def test_html_contains_tab_content_divs(self):
        """
        Should include content divs for each tab.

        Expected structure:
        <div id="tab-overview" class="tab-content active">...</div>
        <div id="tab-tree" class="tab-content">...</div>
        ...
        """
        repo_info = create_test_repo_info(repo_name='test')
        html = self.renderer.render(repo_info=repo_info)

        # Should have tab content divs
        self.assertIn('tab-content', html,
                     "Should have tab-content divs")
        self.assertIn('id="tab-', html,
                     "Tab content divs should have IDs like 'tab-overview'")

    def test_overview_tab_content_has_summary_stats(self):
        """
        Overview tab should show repository summary statistics.

        Should include: avg complexity, avg cognitive complexity, file count, etc.
        """
        # Add aggregate KPIs
        kpis = {
            'complexity': Mock(value=15.5),
            'cognitive_complexity': Mock(value=12.3)
        }
        repo_info = create_test_repo_info(repo_name='test-repo', kpis=kpis)

        html = self.renderer.render(repo_info=repo_info)

        # Should show average cognitive complexity in overview
        self.assertIn('Cognitive', html,
                     "Overview should mention Cognitive Complexity")


if __name__ == '__main__':
    unittest.main()
