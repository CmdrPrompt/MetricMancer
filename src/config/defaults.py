"""
Centralized default values for MetricMancer application.

This module provides a single source of truth for all default configuration values,
ensuring consistency between CLI arguments (cli_helpers.py) and configuration
objects (app_config.py).

Usage:
    from src.config.defaults import Defaults

    # In CLI:
    parser.add_argument("--threshold-low", default=Defaults.THRESHOLD_LOW, ...)

    # In AppConfig:
    threshold_low: float = Defaults.THRESHOLD_LOW
"""


class Defaults:
    """
    Central repository for all default configuration values.

    Organized by category to make it easy to find related settings.
    All values are class constants to prevent accidental modification.
    """

    # =========================================================================
    # Threshold Settings
    # =========================================================================
    THRESHOLD_LOW: float = 10.0
    """Threshold for low complexity rating. Files below this are considered simple."""

    THRESHOLD_HIGH: float = 20.0
    """Threshold for high complexity rating. Files above this need attention."""

    EXTREME_COMPLEXITY_THRESHOLD: int = 100
    """Files above this are flagged as critical regardless of churn."""

    # =========================================================================
    # Output Settings
    # =========================================================================
    OUTPUT_FORMAT: str = "summary"
    """Default output format (singular, for backward compatibility)."""

    REPORT_FOLDER: str = "output"
    """Default folder for all generated reports."""

    LEVEL: str = "file"
    """Default detail level for reports ('file' or 'function')."""

    # =========================================================================
    # Hotspot Settings
    # =========================================================================
    HOTSPOT_THRESHOLD: int = 50
    """Minimum hotspot score to include in hotspot analysis."""

    # =========================================================================
    # Review Strategy Settings
    # =========================================================================
    REVIEW_OUTPUT: str = "review_strategy.md"
    """Default output file for code review strategy report."""

    REVIEW_BASE_BRANCH: str = "main"
    """Default base branch for branch comparisons."""

    # =========================================================================
    # Code Churn Settings
    # =========================================================================
    CHURN_PERIOD: int = 30
    """Number of days to analyze for code churn."""

    # =========================================================================
    # Delta Review Settings
    # =========================================================================
    DELTA_BASE_BRANCH: str = "main"
    """Default base branch for delta comparison."""

    DELTA_OUTPUT: str = "delta_review.md"
    """Default output file for delta review report."""
