"""
Application configuration module for MetricMancer.

This module implements the Configuration Object pattern to centralize all
application settings and reduce coupling in main.py.
"""

from dataclasses import dataclass, field
from typing import List, Optional


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
        debug: Whether to show debug output
    """

    # Required fields
    directories: List[str]

    # Threshold settings
    threshold_low: float = 10.0
    threshold_high: float = 20.0
    problem_file_threshold: Optional[float] = None

    # Output settings
    output_format: str = "summary"  # Backward compatibility (singular)
    output_formats: List[str] = field(default_factory=lambda: ['summary'])  # NEW: Multi-format support
    output_file: Optional[str] = None
    report_folder: str = "output"
    level: str = "file"
    hierarchical: bool = False

    # Hotspot analysis settings
    list_hotspots: bool = False
    hotspot_threshold: int = 50
    hotspot_output: Optional[str] = None

    # Review strategy settings
    review_strategy: bool = False
    review_output: str = "review_strategy.md"
    review_branch_only: bool = False
    review_base_branch: str = "main"

    # Debug settings
    debug: bool = False

    def __post_init__(self):
        """
        Post-initialization to sync output_format and output_formats.

        Ensures backward compatibility:
        - If output_formats provided, update output_format to first item
        - If output_format provided but output_formats is default, convert to list
        - output_formats always takes precedence
        """

        # If output_formats is provided (not default), use it
        if self.output_formats != ['summary']:
            # Update singular to match first item in plural
            if self.output_formats:
                object.__setattr__(self, 'output_format', self.output_formats[0])
        # If output_format differs from default but output_formats is default
        elif self.output_format != 'summary':
            # Convert singular to list
            object.__setattr__(self, 'output_formats', [self.output_format])

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

        # Determine paths
        output_formats_value = None
        if hasattr(args, 'output_formats') and args.output_formats:
            # New plural parameter provided
            if isinstance(args.output_formats, str):
                # Parse comma-separated string
                output_formats_value = [f.strip() for f in args.output_formats.split(',')]
            elif isinstance(args.output_formats, list):
                output_formats_value = args.output_formats
        elif hasattr(args, 'output_format') and args.output_format:
            # Fallback to singular for backward compatibility
            output_formats_value = [args.output_format]

        # Get singular format for backward compatibility
        output_format_value = getattr(args, 'output_format', 'summary')
        if output_formats_value and isinstance(output_formats_value, list) and output_formats_value:
            output_format_value = output_formats_value[0]

        return cls(
            # Required
            directories=args.directories,

            # Thresholds
            threshold_low=args.threshold_low,
            threshold_high=args.threshold_high,
            problem_file_threshold=args.problem_file_threshold,

            # Output settings
            output_format=output_format_value,
            output_formats=output_formats_value if output_formats_value else ['summary'],
            output_file=None,  # Will be set later if needed
            report_folder=getattr(args, 'report_folder', None) or 'output',
            level=args.level,
            hierarchical=args.hierarchical,

            # Hotspot settings
            list_hotspots=getattr(args, 'list_hotspots', False),
            hotspot_threshold=getattr(args, 'hotspot_threshold', 50),
            hotspot_output=getattr(args, 'hotspot_output', None),

            # Review strategy settings
            review_strategy=getattr(args, 'review_strategy', False),
            review_output=getattr(args, 'review_output', 'review_strategy.md'),
            review_branch_only=getattr(args, 'review_branch_only', False),
            review_base_branch=getattr(args, 'review_base_branch', 'main'),

            # Debug
            debug=getattr(args, 'debug', False)
        )

    def validate(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ValueError: If configuration is invalid

        Example:
            >>> config = AppConfig(directories=['src'])
            >>> config.validate()  # Raises if invalid
        """
        if not self.directories:
            raise ValueError("At least one directory must be specified")

        if self.threshold_low >= self.threshold_high:
            raise ValueError(
                f"threshold_low ({self.threshold_low}) must be less than "
                f"threshold_high ({self.threshold_high})"
            )

        if self.threshold_low < 0 or self.threshold_high < 0:
            raise ValueError("Thresholds must be non-negative")

        if self.hotspot_threshold < 0:
            raise ValueError("Hotspot threshold must be non-negative")

        valid_formats = [
            'summary', 'quick-wins', 'human', 'human-tree', 'tree',
            'html', 'json', 'machine',
            'review-strategy', 'review-strategy-branch'
        ]

        # Validate output_formats list (NEW: multi-format support)
        if not self.output_formats:
            raise ValueError("At least one output format must be specified")

        for fmt in self.output_formats:
            if fmt not in valid_formats:
                raise ValueError(
                    f"Invalid output format '{fmt}'. "
                    f"Must be one of: {', '.join(valid_formats)}"
                )

        # Validate singular output_format for backward compatibility
        if self.output_format not in valid_formats:
            raise ValueError(
                f"Invalid output format '{self.output_format}'. "
                f"Must be one of: {', '.join(valid_formats)}"
            )

        valid_levels = ['file', 'function']
        if self.level not in valid_levels:
            raise ValueError(
                f"Invalid level '{self.level}'. Must be one of: {', '.join(valid_levels)}"
            )

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
