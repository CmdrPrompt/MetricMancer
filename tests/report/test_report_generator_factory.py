"""
Unit tests for ReportGeneratorFactory class.

Tests the Factory pattern implementation for creating report generators.
"""

from src.report.report_generator_factory import ReportGeneratorFactory
from src.report.cli.cli_report_generator import CLIReportGenerator
from src.report.json.json_report_generator import JSONReportGenerator


class TestReportGeneratorFactoryCreate:
    """Test ReportGeneratorFactory.create() method."""

    def test_create_json_generator(self):
        """Test creating JSON report generator."""
        generator_cls = ReportGeneratorFactory.create('json')

        assert generator_cls is JSONReportGenerator

    def test_create_summary_generator(self):
        """Test creating summary report generator."""
        generator_cls = ReportGeneratorFactory.create('summary')

        assert generator_cls is CLIReportGenerator

    def test_create_quick_wins_generator(self):
        """Test creating quick-wins report generator."""
        generator_cls = ReportGeneratorFactory.create('quick-wins')

        assert generator_cls is CLIReportGenerator

    def test_create_human_generator(self):
        """Test creating human-readable report generator."""
        generator_cls = ReportGeneratorFactory.create('human')

        assert generator_cls is CLIReportGenerator

    def test_create_human_tree_generator(self):
        """Test creating human-tree report generator."""
        generator_cls = ReportGeneratorFactory.create('human-tree')

        assert generator_cls is CLIReportGenerator

    def test_create_tree_generator(self):
        """Test creating tree report generator."""
        generator_cls = ReportGeneratorFactory.create('tree')

        assert generator_cls is CLIReportGenerator

    def test_create_html_generator(self):
        """Test creating HTML report generator returns None (uses default)."""
        generator_cls = ReportGeneratorFactory.create('html')

        assert generator_cls is None

    def test_create_unknown_format_returns_default(self):
        """Test unknown format returns default CLI generator."""
        generator_cls = ReportGeneratorFactory.create('unknown_format')

        assert generator_cls is CLIReportGenerator


class TestReportGeneratorFactoryFormats:
    """Test format-related helper methods."""

    def test_get_supported_formats(self):
        """Test getting list of supported formats."""
        formats = ReportGeneratorFactory.get_supported_formats()

        assert isinstance(formats, list)
        assert 'json' in formats
        assert 'summary' in formats
        assert 'quick-wins' in formats
        assert 'html' in formats
        assert 'human' in formats
        assert 'human-tree' in formats
        assert 'tree' in formats

    def test_is_format_supported_valid(self):
        """Test is_format_supported with valid formats."""
        assert ReportGeneratorFactory.is_format_supported('json') is True
        assert ReportGeneratorFactory.is_format_supported('html') is True
        assert ReportGeneratorFactory.is_format_supported('summary') is True

    def test_is_format_supported_invalid(self):
        """Test is_format_supported with invalid formats."""
        assert ReportGeneratorFactory.is_format_supported('invalid') is False
        assert ReportGeneratorFactory.is_format_supported('') is False
        assert ReportGeneratorFactory.is_format_supported('XML') is False


class TestReportGeneratorFactoryConsistency:
    """Test consistency between factory methods."""

    def test_all_supported_formats_can_be_created(self):
        """Test that all formats from get_supported_formats can be created."""
        formats = ReportGeneratorFactory.get_supported_formats()

        for fmt in formats:
            # Should not raise any exception
            generator_cls = ReportGeneratorFactory.create(fmt)
            # HTML returns None, others return a class
            if fmt == 'html':
                assert generator_cls is None
            else:
                assert generator_cls is not None

    def test_supported_formats_and_is_supported_consistent(self):
        """Test get_supported_formats and is_format_supported are consistent."""
        formats = ReportGeneratorFactory.get_supported_formats()

        for fmt in formats:
            assert ReportGeneratorFactory.is_format_supported(fmt) is True


class TestReportGeneratorFactoryUsage:
    """Test realistic usage scenarios."""

    def test_factory_workflow_json(self):
        """Test complete workflow for creating JSON generator."""
        # Check format is supported
        assert ReportGeneratorFactory.is_format_supported('json')

        # Create generator class
        generator_cls = ReportGeneratorFactory.create('json')

        # Verify it's the correct type
        assert generator_cls is JSONReportGenerator
        assert generator_cls.__name__ == 'JSONReportGenerator'

    def test_factory_workflow_unknown_format(self):
        """Test workflow with unknown format (should use default)."""
        # Unknown format not in supported list
        assert 'custom_format' not in ReportGeneratorFactory.get_supported_formats()

        # But factory still returns a default
        generator_cls = ReportGeneratorFactory.create('custom_format')

        # Should be CLI generator (default)
        assert generator_cls is CLIReportGenerator
