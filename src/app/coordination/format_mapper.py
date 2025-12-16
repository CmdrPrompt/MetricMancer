"""
Format Mapper Module

Maps output formats to their appropriate file extensions and base names.
Extracted from report_coordinator.py to reduce complexity.
"""
from typing import Optional, Dict


class FormatMapper:
    """
    Maps output formats to file extensions and base names.

    Responsibilities:
    - Provide format to extension mapping
    - Provide format to base filename mapping
    - Centralize format configuration
    """

    # Format to extension mappings
    SIMPLE_FORMATS: Dict[str, str] = {
        'json': '.json',
        'html': '.html'
    }

    # CLI format to base filename mappings
    CLI_FORMATS: Dict[str, str] = {
        'summary': 'summary_report',
        'quick-wins': 'quick_wins_report',
        'tree': 'file_tree_report'
    }

    # Review strategy formats and their output filenames
    REVIEW_STRATEGY_FORMATS: Dict[str, str] = {
        'review-strategy': 'review_strategy.md',
        'review-strategy-branch': 'review_strategy_branch.md'
    }

    @classmethod
    def get_extension(cls, output_format: str) -> Optional[str]:
        """
        Get file extension for a simple format (json, csv, html).

        Args:
            output_format: Output format name

        Returns:
            File extension with dot prefix, or None if not a simple format
        """
        return cls.SIMPLE_FORMATS.get(output_format)

    @classmethod
    def get_cli_base_name(cls, output_format: str) -> Optional[str]:
        """
        Get base filename for CLI output formats.

        Args:
            output_format: Output format name

        Returns:
            Base filename without extension, or None if not a CLI format
        """
        return cls.CLI_FORMATS.get(output_format)

    @classmethod
    def is_cli_format(cls, output_format: str) -> bool:
        """
        Check if format is a CLI format.

        Args:
            output_format: Output format name

        Returns:
            True if format is a CLI format
        """
        return output_format in cls.CLI_FORMATS

    @classmethod
    def is_simple_format(cls, output_format: str) -> bool:
        """
        Check if format is a simple format (json, csv, html).

        Args:
            output_format: Output format name

        Returns:
            True if format is a simple format
        """
        return output_format in cls.SIMPLE_FORMATS

    @classmethod
    def is_review_strategy_format(cls, output_format: str) -> bool:
        """
        Check if format is a review strategy format.

        Args:
            output_format: Output format name

        Returns:
            True if format is a review strategy format
        """
        return output_format in cls.REVIEW_STRATEGY_FORMATS

    @classmethod
    def get_review_strategy_filename(cls, output_format: str) -> Optional[str]:
        """
        Get output filename for review strategy format.

        Args:
            output_format: Output format name

        Returns:
            Output filename, or None if not a review strategy format
        """
        return cls.REVIEW_STRATEGY_FORMATS.get(output_format)
