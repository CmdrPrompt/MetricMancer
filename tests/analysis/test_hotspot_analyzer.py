"""
Tests for hotspot_analyzer module.
"""

import unittest
import tempfile
import os
from src.analysis.hotspot_analyzer import (
    extract_hotspots_from_data,
    format_hotspots_table,
    save_hotspots_to_file,
    print_hotspots_summary,
    _format_hotspots_markdown
)


class TestExtractHotspotsFromData(unittest.TestCase):
    """Tests for extract_hotspots_from_data function."""

    def test_extract_hotspots_basic(self):
        """Test extracting hotspots from simple data structure."""
        data = {
            'files': {
                'file1.py': {
                    'kpis': {
                        'hotspot': 100,
                        'complexity': 10,
                        'churn': 10.0
                    }
                },
                'file2.py': {
                    'kpis': {
                        'hotspot': 25,
                        'complexity': 5,
                        'churn': 5.0
                    }
                }
            }
        }

        hotspots = extract_hotspots_from_data(data, threshold=50)

        self.assertEqual(len(hotspots), 1)
        self.assertEqual(hotspots[0], ('file1.py', 100, 10, 10.0))

    def test_extract_hotspots_with_threshold(self):
        """Test that threshold filtering works correctly."""
        data = {
            'files': {
                'high.py': {'kpis': {'hotspot': 150, 'complexity': 15, 'churn': 10.0}},
                'medium.py': {'kpis': {'hotspot': 75, 'complexity': 10, 'churn': 7.5}},
                'low.py': {'kpis': {'hotspot': 25, 'complexity': 5, 'churn': 5.0}}
            }
        }

        hotspots = extract_hotspots_from_data(data, threshold=50)

        self.assertEqual(len(hotspots), 2)
        self.assertIn(('high.py', 150, 15, 10.0), hotspots)
        self.assertIn(('medium.py', 75, 10, 7.5), hotspots)
        self.assertNotIn(('low.py', 25, 5, 5.0), hotspots)

    def test_extract_hotspots_recursive(self):
        """Test recursive extraction from nested directories."""
        data = {
            'files': {
                'root.py': {'kpis': {'hotspot': 100, 'complexity': 10, 'churn': 10.0}}
            },
            'scan_dirs': {
                'subdir': {
                    'files': {
                        'nested.py': {'kpis': {'hotspot': 75, 'complexity': 7, 'churn': 10.0}}
                    }
                }
            }
        }

        hotspots = extract_hotspots_from_data(data, threshold=50)

        self.assertEqual(len(hotspots), 2)
        self.assertIn(('root.py', 100, 10, 10.0), hotspots)
        self.assertIn(('subdir/nested.py', 75, 7, 10.0), hotspots)

    def test_extract_hotspots_empty_data(self):
        """Test handling of empty data."""
        data = {}
        hotspots = extract_hotspots_from_data(data, threshold=50)
        self.assertEqual(len(hotspots), 0)

    def test_extract_hotspots_no_files(self):
        """Test handling when no files meet threshold."""
        data = {
            'files': {
                'low1.py': {'kpis': {'hotspot': 10, 'complexity': 2, 'churn': 5.0}},
                'low2.py': {'kpis': {'hotspot': 20, 'complexity': 4, 'churn': 5.0}}
            }
        }

        hotspots = extract_hotspots_from_data(data, threshold=50)
        self.assertEqual(len(hotspots), 0)

    def test_extract_hotspots_missing_kpis(self):
        """Test handling of files without KPI data."""
        data = {
            'files': {
                'file1.py': {},
                'file2.py': {'kpis': {}},
                'file3.py': {'kpis': {'hotspot': 100, 'complexity': 10, 'churn': 10.0}}
            }
        }

        hotspots = extract_hotspots_from_data(data, threshold=50)
        self.assertEqual(len(hotspots), 1)
        self.assertEqual(hotspots[0], ('file3.py', 100, 10, 10.0))

    def test_extract_hotspots_default_values(self):
        """Test that missing complexity/churn default to 0."""
        data = {
            'files': {
                'file1.py': {'kpis': {'hotspot': 100}}
            }
        }

        hotspots = extract_hotspots_from_data(data, threshold=50)
        self.assertEqual(len(hotspots), 1)
        self.assertEqual(hotspots[0], ('file1.py', 100, 0, 0))


class TestFormatHotspotsTable(unittest.TestCase):
    """Tests for format_hotspots_table function."""

    def test_format_empty_list(self):
        """Test formatting an empty hotspot list."""
        result = format_hotspots_table([])
        self.assertIn("No hotspots found", result)

    def test_format_basic_table(self):
        """Test basic table formatting."""
        hotspots = [
            ('app/file1.py', 100, 10, 10.0),
            ('app/file2.py', 50, 5, 10.0)
        ]

        result = format_hotspots_table(hotspots, show_risk_categories=False)

        self.assertIn("HOTSPOT ANALYSIS", result)
        self.assertIn("app/file1.py", result)
        self.assertIn("app/file2.py", result)
        self.assertIn("100", result)
        self.assertIn("50", result)

    def test_format_sorted_by_hotspot(self):
        """Test that hotspots are sorted by score (highest first)."""
        hotspots = [
            ('low.py', 50, 5, 10.0),
            ('high.py', 200, 20, 10.0),
            ('medium.py', 100, 10, 10.0)
        ]

        result = format_hotspots_table(hotspots, show_risk_categories=False)

        # high.py should appear before medium.py, which should appear before low.py
        high_pos = result.find('high.py')
        medium_pos = result.find('medium.py')
        low_pos = result.find('low.py')

        self.assertLess(high_pos, medium_pos)
        self.assertLess(medium_pos, low_pos)

    def test_format_with_risk_categories(self):
        """Test that risk categories are included when enabled."""
        hotspots = [
            ('critical.py', 200, 20, 15.0),  # High complexity + high churn
            ('emerging.py', 100, 10, 12.0),  # Medium complexity + high churn
            ('stable.py', 80, 20, 4.0)       # High complexity + low churn
        ]

        result = format_hotspots_table(hotspots, show_risk_categories=True)

        self.assertIn("CRITICAL HOTSPOTS", result)
        self.assertIn("EMERGING HOTSPOTS", result)
        self.assertIn("STABLE COMPLEXITY", result)
        self.assertIn("critical.py", result)
        self.assertIn("emerging.py", result)
        self.assertIn("stable.py", result)

    def test_format_interpretation_guide(self):
        """Test that interpretation guide is included."""
        hotspots = [('file.py', 100, 10, 10.0)]

        result = format_hotspots_table(hotspots)

        self.assertIn("INTERPRETATION GUIDE", result)
        self.assertIn("Hotspot Score Classification", result)
        self.assertIn("Complexity Thresholds", result)
        self.assertIn("Code Churn Thresholds", result)
        self.assertIn("Adam Tornhill", result)

    def test_format_complete_hotspot_list(self):
        """Test that complete list is included."""
        hotspots = [
            ('file1.py', 100, 10, 10.0),
            ('file2.py', 50, 5, 10.0)
        ]

        result = format_hotspots_table(hotspots)

        self.assertIn("COMPLETE HOTSPOT LIST", result)
        self.assertIn("Total files above threshold: 2", result)


class TestFormatHotspotsMarkdown(unittest.TestCase):
    """Tests for _format_hotspots_markdown function."""

    def test_format_markdown_empty_list(self):
        """Test markdown formatting of empty list."""
        result = _format_hotspots_markdown([])
        self.assertIn("# 🔥 Hotspot Analysis", result)
        self.assertIn("No hotspots found", result)

    def test_format_markdown_basic(self):
        """Test basic markdown formatting."""
        hotspots = [
            ('app/file1.py', 100, 10, 10.0),
            ('app/file2.py', 50, 5, 10.0)
        ]

        result = _format_hotspots_markdown(hotspots, show_risk_categories=False)

        # Check markdown headers
        self.assertIn("# 🔥 Hotspot Analysis", result)
        self.assertIn("## 📊 Interpretation Guide", result)
        self.assertIn("## 📋 Complete Hotspot List", result)

        # Check blockquotes
        self.assertIn("> *Generated by MetricMancer", result)
        self.assertIn("Adam Tornhill", result)

        # Check table formatting
        self.assertIn("| File | Hotspot | Complexity | Churn |", result)
        self.assertIn("|------|---------|------------|-------|", result)
        self.assertIn("| `app/file1.py` | 100 | 10 | 10.0 |", result)

    def test_format_markdown_risk_categories(self):
        """Test markdown risk category sections."""
        hotspots = [
            ('critical.py', 200, 20, 15.0),  # Critical
            ('emerging.py', 100, 10, 12.0),  # Emerging
            ('stable.py', 80, 20, 4.0)       # Stable
        ]

        result = _format_hotspots_markdown(hotspots, show_risk_categories=True)

        # Check risk category headers with emojis
        self.assertIn("## 🔴 Critical Hotspots", result)
        self.assertIn("## 🟡 Emerging Hotspots", result)
        self.assertIn("## 🟢 Stable Complexity", result)

        # Check criteria descriptions
        self.assertIn("**Criteria:** High Complexity (>15) + High Churn (>10)", result)
        self.assertIn("**Actions:**", result)

    def test_format_markdown_interpretation_tables(self):
        """Test that interpretation guide includes proper markdown tables."""
        hotspots = [('file.py', 100, 10, 10.0)]

        result = _format_hotspots_markdown(hotspots)

        # Check for table headers
        self.assertIn("### Hotspot Score Classification", result)
        self.assertIn("### Complexity Thresholds", result)
        self.assertIn("### Code Churn Thresholds", result)
        self.assertIn("### Recommended Actions", result)

        # Check for emojis in tables
        self.assertIn("🔴", result)
        self.assertIn("🟡", result)
        self.assertIn("🟢", result)
        self.assertIn("🟠", result)

    def test_format_markdown_sorted(self):
        """Test that markdown output is sorted by hotspot score."""
        hotspots = [
            ('low.py', 50, 5, 10.0),
            ('high.py', 200, 20, 10.0),
            ('medium.py', 100, 10, 10.0)
        ]

        result = _format_hotspots_markdown(hotspots)

        # Check order in complete list
        high_pos = result.find('`high.py`')
        medium_pos = result.find('`medium.py`')
        low_pos = result.find('`low.py`')

        # Find positions in the complete list section (after "Complete Hotspot List")
        complete_list_pos = result.find("Complete Hotspot List")
        self.assertGreater(high_pos, complete_list_pos)
        self.assertLess(high_pos, medium_pos)
        self.assertLess(medium_pos, low_pos)


class TestSaveHotspotsToFile(unittest.TestCase):
    """Tests for save_hotspots_to_file function."""

    def test_save_markdown_format(self):
        """Test saving hotspots in markdown format."""
        hotspots = [('file.py', 100, 10, 10.0)]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            filename = f.name

        try:
            save_hotspots_to_file(hotspots, filename)

            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Should be markdown format
            self.assertIn("# 🔥 Hotspot Analysis", content)
            self.assertIn("| File | Hotspot | Complexity | Churn |", content)
            self.assertIn("|------|---------|------------|-------|", content)
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_save_text_format(self):
        """Test saving hotspots in plain text format."""
        hotspots = [('file.py', 100, 10, 10.0)]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            filename = f.name

        try:
            save_hotspots_to_file(hotspots, filename)

            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Should be text format with ASCII lines
            self.assertIn("=" * 100, content)
            self.assertIn("HOTSPOT ANALYSIS", content)
            # Should NOT contain markdown
            self.assertNotIn("# 🔥", content)
            self.assertNotIn("| File |", content)
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_save_with_risk_categories(self):
        """Test that risk categories are included when enabled."""
        hotspots = [
            ('critical.py', 200, 20, 15.0),
            ('emerging.py', 100, 10, 12.0)
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            filename = f.name

        try:
            save_hotspots_to_file(hotspots, filename, show_risk_categories=True)

            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn("Critical Hotspots", content)
            self.assertIn("Emerging Hotspots", content)
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_save_without_risk_categories(self):
        """Test that risk categories can be disabled."""
        hotspots = [('critical.py', 200, 20, 15.0)]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            filename = f.name

        try:
            save_hotspots_to_file(hotspots, filename, show_risk_categories=False)

            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Should still have complete list but not categorized sections
            self.assertIn("Complete Hotspot List", content)
            # Risk category section titles should not appear
            sections_count = content.count("Critical Hotspots")
            # May appear in interpretation guide, but not as a separate section
            self.assertLessEqual(sections_count, 1)
        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestPrintHotspotsSummary(unittest.TestCase):
    """Tests for print_hotspots_summary function."""

    def test_print_summary_with_hotspots(self):
        """Test printing summary with hotspots."""
        hotspots = [
            ('file1.py', 200, 20, 10.0),
            ('file2.py', 150, 15, 10.0),
            ('file3.py', 100, 10, 10.0)
        ]

        # This function prints to stdout, so we just verify it doesn't raise
        try:
            print_hotspots_summary(hotspots)
        except Exception as e:
            self.fail(f"print_hotspots_summary raised {type(e).__name__}: {e}")

    def test_print_summary_empty_list(self):
        """Test printing summary with empty list."""
        try:
            print_hotspots_summary([])
        except Exception as e:
            self.fail(f"print_hotspots_summary raised {type(e).__name__}: {e}")

    def test_print_summary_single_hotspot(self):
        """Test printing summary with single hotspot."""
        hotspots = [('file.py', 100, 10, 10.0)]

        try:
            print_hotspots_summary(hotspots)
        except Exception as e:
            self.fail(f"print_hotspots_summary raised {type(e).__name__}: {e}")


if __name__ == '__main__':
    unittest.main()
