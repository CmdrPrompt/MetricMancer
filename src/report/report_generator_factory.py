"""
Factory for creating appropriate report generators based on output format.

This module implements the Factory pattern to encapsulate report generator
creation logic and remove it from main.py.
"""

from typing import Optional, Type

from src.report.cli.cli_report_generator import CLIReportGenerator
from src.report.json.json_report_generator import JSONReportGenerator
from src.report.report_generator import ReportGenerator


class ReportGeneratorFactory:
    """
    Factory for creating report generator instances.

    This factory encapsulates the logic for selecting the appropriate report
    generator based on output format, keeping main.py clean and focused.

    Example:
        >>> factory = ReportGeneratorFactory()
        >>> generator_cls = factory.create('json')
        >>> generator = generator_cls(repo_info, thresholds...)
    """

    # Mapping of output formats to their corresponding generator classes
    _GENERATORS = {
        'json': JSONReportGenerator,
        'summary': CLIReportGenerator,
        'quick-wins': CLIReportGenerator,
        'tree': CLIReportGenerator,
    }

    @classmethod
    def create(cls, output_format: str) -> Optional[Type[ReportGenerator]]:
        """
        Create and return the appropriate report generator class.

        Args:
            output_format: The desired output format (json, machine, html, etc.)

        Returns:
            Report generator class, or None for default HTML generator

        Example:
            >>> generator_cls = ReportGeneratorFactory.create('json')
            >>> print(generator_cls.__name__)
            'JSONReportGenerator'

            >>> generator_cls = ReportGeneratorFactory.create('html')
            >>> print(generator_cls)
            None  # Uses default ReportGenerator
        """
        # Return None for HTML to use default ReportGenerator
        if output_format == 'html':
            return None

        # Return mapped generator or default to CLI generator
        return cls._GENERATORS.get(output_format, CLIReportGenerator)

    @classmethod
    def get_supported_formats(cls) -> list:
        """
        Get list of all supported output formats.

        Returns:
            List of supported format strings

        Example:
            >>> formats = ReportGeneratorFactory.get_supported_formats()
            >>> 'json' in formats
            True
        """
        return list(cls._GENERATORS.keys()) + ['html']

    @classmethod
    def is_format_supported(cls, output_format: str) -> bool:
        """
        Check if an output format is supported.

        Args:
            output_format: Format string to check

        Returns:
            True if format is supported, False otherwise

        Example:
            >>> ReportGeneratorFactory.is_format_supported('json')
            True
            >>> ReportGeneratorFactory.is_format_supported('invalid')
            False
        """
        return output_format == 'html' or output_format in cls._GENERATORS
