"""
Application configuration module for MetricMancer.

This module implements the Configuration Object pattern to centralize all
application settings and reduce coupling in main.py.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from src.config.config_validator import ConfigValidator
from src.config.defaults import Defaults


@dataclass
class AppConfig:
    """
    Central configuration object for MetricMancer application.

    This class encapsulates all application settings and provides factory methods
    for creating configurations from different sources (CLI args, files, etc.).

    Attributes:
        directories: List of root folders to scan for code complexity
        threshold_low: Threshold for low complexity rating (default: 10.0)
        threshold_high: Threshold for high complexity rating (default: 20.0)
        problem_file_threshold: Optional threshold for individual file complexity
        output_format: Output format (singular, for backward compatibility)
        output_formats: List of output formats (NEW: multi-format support)
        output_file: Optional output file path
        report_folder: Folder to write all reports to (default: 'output')
        level: Detail level for reports ('file' or 'function')
        hierarchical: Whether to output full hierarchical data model (JSON only)
        list_hotspots: Whether to display hotspot list after analysis
        hotspot_threshold: Minimum hotspot score to include (default: 50)
        hotspot_output: Optional file to save hotspot list
        review_strategy: Whether to generate code review strategy report
        review_output: Output file for review strategy (default: 'review_strategy.md')
        review_branch_only: Only include changed files in review strategy
        review_base_branch: Base branch to compare against (default: 'main')
        churn_period: Number of days to analyze for code churn (default: 30)
        delta_review: Whether to generate delta-based review (function-level)
        delta_base_branch: Base branch for delta comparison (default: 'main')
        delta_target_branch: Target branch for delta comparison (None = current)
        delta_output: Output file for delta review (default: 'delta_review.md')
        debug: Whether to show debug output
    """

    # Required fields
    directories: List[str]

    # Threshold settings
    threshold_low: float = Defaults.THRESHOLD_LOW
    threshold_high: float = Defaults.THRESHOLD_HIGH
    problem_file_threshold: Optional[float] = None
    extreme_complexity_threshold: int = Defaults.EXTREME_COMPLEXITY_THRESHOLD

    # Output settings
    output_format: str = Defaults.OUTPUT_FORMAT  # Backward compatibility (singular)
    output_formats: List[str] = field(default_factory=lambda: [Defaults.OUTPUT_FORMAT])  # Multi-format support
    using_output_formats_flag: bool = False  # True if user explicitly used --output-formats
    output_file: Optional[str] = None
    report_folder: str = Defaults.REPORT_FOLDER
    level: str = Defaults.LEVEL
    hierarchical: bool = False

    # Hotspot analysis settings
    list_hotspots: bool = False
    hotspot_threshold: int = Defaults.HOTSPOT_THRESHOLD
    hotspot_output: Optional[str] = None

    # Review strategy settings
    review_strategy: bool = False
    review_output: str = Defaults.REVIEW_OUTPUT
    review_branch_only: bool = False
    review_base_branch: str = Defaults.REVIEW_BASE_BRANCH
    include_review_tab: bool = False  # Include Code Review tab in HTML report

    # Code churn settings
    churn_period: int = Defaults.CHURN_PERIOD

    # Delta review settings (function-level analysis)
    delta_review: bool = False
    delta_base_branch: str = Defaults.DELTA_BASE_BRANCH
    delta_target_branch: Optional[str] = None  # None = current branch
    delta_output: str = Defaults.DELTA_OUTPUT

    # Debug settings
    debug: bool = False
    no_timing: bool = False  # Suppress timing information output

    def __post_init__(self):
        """
        Post-initialization to sync output_format and output_formats.

        Ensures backward compatibility:
        - If output_formats provided, update output_format to first item
        - If output_format provided but output_formats is default, convert to list
        - output_formats always takes precedence
        """

        # Normalize plural and singular representations with minimal nesting
        if self.output_formats and self.output_formats != ['summary']:
            object.__setattr__(self, 'output_format', self.output_formats[0])
            return

        # If no meaningful plural provided, promote singular to plural when needed
        if self.output_format and self.output_format != 'summary':
            object.__setattr__(self, 'output_formats', [self.output_format])

    @staticmethod
    def _parse_output_formats_from_args(args) -> tuple:
        """
        Parse output formats from CLI arguments.

        Returns:
            tuple: (output_formats_value, using_output_formats_flag, output_format_value)
        """
        using_output_formats_flag = False
        output_formats_value = None

        # Prefer explicit plural parameter when provided
        if getattr(args, 'output_formats', None):
            using_output_formats_flag = True
            raw = args.output_formats
            if isinstance(raw, str):
                output_formats_value = [f.strip() for f in raw.split(',') if f.strip()]
            elif isinstance(raw, list):
                output_formats_value = [f for f in raw if f]

        # Fallback to singular --output-format
        if not output_formats_value and getattr(args, 'output_format', None):
            output_formats_value = [args.output_format]

        output_format_value = getattr(args, 'output_format', Defaults.OUTPUT_FORMAT)
        if output_formats_value:
            output_format_value = output_formats_value[0]

        return output_formats_value, using_output_formats_flag, output_format_value

    @staticmethod
    def _extract_threshold_settings(args) -> dict:
        """Extract threshold-related settings from CLI args."""
        return {
            'threshold_low': args.threshold_low,
            'threshold_high': args.threshold_high,
            'problem_file_threshold': args.problem_file_threshold,
            'extreme_complexity_threshold': getattr(args, 'extreme_complexity_threshold', Defaults.EXTREME_COMPLEXITY_THRESHOLD),
        }

    @staticmethod
    def _extract_output_settings(args, output_formats_value, output_format_value, using_output_formats_flag) -> dict:
        """Extract output-related settings from CLI args."""
        # Handle output filename logic (similar to report_helpers.get_output_filename)
        import os
        import datetime

        # Set file type depending on report format
        ext = '.html'
        if output_format_value == 'json':
            ext = '.json'
        output_file = f'complexity_report{ext}'

        # Safely get report_filename (handle Mock objects in tests)
        report_filename = getattr(args, 'report_filename', None)
        if report_filename and not hasattr(report_filename, '__call__'):  # Not a Mock
            output_file = report_filename
            if getattr(args, 'with_date', False):
                date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                base, ext = os.path.splitext(output_file)
                output_file = f"{base}_{date_str}{ext}"
        elif getattr(args, 'auto_report_filename', False):
            date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            dir_str = "_".join([
                os.path.basename(os.path.normpath(d))
                for d in getattr(args, 'directories', ['src'])
            ])
            output_file = f"complexity_report_{dir_str}_{date_str}.html"

        return {
            'output_format': output_format_value,
            'output_formats': output_formats_value if output_formats_value else [Defaults.OUTPUT_FORMAT],
            'using_output_formats_flag': using_output_formats_flag,
            'output_file': output_file,
            'report_folder': getattr(args, 'report_folder', None) or Defaults.REPORT_FOLDER,
            'level': args.level,
            'hierarchical': args.hierarchical,
        }

    @staticmethod
    def _extract_hotspot_settings(args) -> dict:
        """Extract hotspot-related settings from CLI args."""
        return {
            'list_hotspots': getattr(args, 'list_hotspots', False),
            'hotspot_threshold': getattr(args, 'hotspot_threshold', Defaults.HOTSPOT_THRESHOLD),
            'hotspot_output': getattr(args, 'hotspot_output', None),
        }

    @staticmethod
    def _extract_review_settings(args) -> dict:
        """Extract review strategy settings from CLI args."""
        return {
            'review_strategy': getattr(args, 'review_strategy', False),
            'review_output': getattr(args, 'review_output', Defaults.REVIEW_OUTPUT),
            'review_branch_only': getattr(args, 'review_branch_only', False),
            'review_base_branch': getattr(args, 'review_base_branch', Defaults.REVIEW_BASE_BRANCH),
            'include_review_tab': getattr(args, 'include_review_tab', False),
        }

    @staticmethod
    def _extract_churn_settings(args) -> dict:
        """Extract code churn settings from CLI args."""
        return {
            'churn_period': getattr(args, 'churn_period', Defaults.CHURN_PERIOD),
        }

    @staticmethod
    def _extract_delta_settings(args) -> dict:
        """Extract delta review settings from CLI args."""
        return {
            'delta_review': getattr(args, 'delta_review', False),
            'delta_base_branch': getattr(args, 'delta_base_branch', Defaults.DELTA_BASE_BRANCH),
            'delta_target_branch': getattr(args, 'delta_target_branch', None),
            'delta_output': getattr(args, 'delta_output', Defaults.DELTA_OUTPUT),
        }

    @staticmethod
    def _extract_debug_settings(args) -> dict:
        """Extract debug settings from CLI args."""
        return {
            'debug': getattr(args, 'debug', False),
            'no_timing': getattr(args, 'no_timing', False),
        }

    @classmethod
    def from_cli_args(cls, args):
        """
        Create AppConfig from parsed CLI arguments.

        Supports both --output-format (singular, backward compat) and
        --output-formats (plural, new multi-format support).

        Args:
            args: Parsed arguments from argparse.ArgumentParser

        Returns:
            AppConfig instance with settings from CLI arguments

        Example:
            >>> parser = parse_args()
            >>> args = parser.parse_args()
            >>> config = AppConfig.from_cli_args(args)
        """

        # Parse and extract settings using helpers
        output_formats_value, using_output_formats_flag, output_format_value = cls._parse_output_formats_from_args(args)

        threshold_settings = cls._extract_threshold_settings(args)
        output_settings = cls._extract_output_settings(
            args, output_formats_value, output_format_value, using_output_formats_flag)
        hotspot_settings = cls._extract_hotspot_settings(args)
        review_settings = cls._extract_review_settings(args)
        churn_settings = cls._extract_churn_settings(args)
        delta_settings = cls._extract_delta_settings(args)
        debug_settings = cls._extract_debug_settings(args)

        config_kwargs = {
            'directories': args.directories,
            **threshold_settings,
            **output_settings,
            **hotspot_settings,
            **review_settings,
            **churn_settings,
            **delta_settings,
            **debug_settings,
        }

        return cls(**config_kwargs)

    def validate(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ValueError: If configuration is invalid

        Example:
            >>> config = AppConfig(directories=['src'])
            >>> config.validate()  # Raises if invalid
        """
        # Delegate to ConfigValidator to keep AppConfig focused on data
        ConfigValidator(self).validate()

    # Validation logic moved to src.config.config_validator.ConfigValidator

    def __repr__(self) -> str:
        """Return detailed string representation of configuration."""
        return (
            f"AppConfig(\n"
            f"  directories={self.directories},\n"
            f"  thresholds=({self.threshold_low}, {self.threshold_high}),\n"
            f"  output_format='{self.output_format}',\n"
            f"  level='{self.level}',\n"
            f"  features={{\n"
            f"    hotspots={self.list_hotspots},\n"
            f"    review={self.review_strategy},\n"
            f"    hierarchical={self.hierarchical}\n"
            f"  }}\n"
            f")"
        )
