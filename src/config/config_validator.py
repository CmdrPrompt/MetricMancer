"""Configuration validation helpers extracted from AppConfig.

This module centralizes validation logic to keep AppConfig focused on
configuration data and construction.
"""
from typing import Iterable


VALID_OUTPUT_FORMATS = {
    'summary', 'quick-wins', 'human', 'human-tree', 'tree',
    'html', 'json', 'machine',
    'review-strategy', 'review-strategy-branch'
}


class ConfigValidator:
    """Validates AppConfig-like objects.

    The validator accepts any object with the expected attributes so it can be
    used by AppConfig without creating circular imports.
    """

    def __init__(self, cfg) -> None:
        self.cfg = cfg

    def validate(self) -> None:
        self._validate_directories()
        self._validate_thresholds()
        self._validate_output_formats()
        self._validate_level()

    def _validate_directories(self) -> None:
        if not getattr(self.cfg, 'directories', None):
            raise ValueError("At least one directory must be specified")

    def _validate_thresholds(self) -> None:
        low = getattr(self.cfg, 'threshold_low', None)
        high = getattr(self.cfg, 'threshold_high', None)
        if low is None or high is None:
            return
        if low >= high:
            raise ValueError(f"threshold_low ({low}) must be less than threshold_high ({high})")
        if low < 0 or high < 0:
            raise ValueError("Thresholds must be non-negative")
        if getattr(self.cfg, 'hotspot_threshold', 0) < 0:
            raise ValueError("Hotspot threshold must be non-negative")

    def _validate_output_formats(self) -> None:
        output_formats = getattr(self.cfg, 'output_formats', None)
        if not output_formats:
            raise ValueError("At least one output format must be specified")
        invalid = set(output_formats) - VALID_OUTPUT_FORMATS
        if invalid:
            raise ValueError(
                f"Invalid output format(s) '{', '.join(sorted(invalid))}'. "
                f"Must be one of: {', '.join(sorted(VALID_OUTPUT_FORMATS))}"
            )
        if getattr(self.cfg, 'output_format', None) not in VALID_OUTPUT_FORMATS:
            raise ValueError(
                f"Invalid output format '{getattr(self.cfg, 'output_format')}'. "
                f"Must be one of: {', '.join(sorted(VALID_OUTPUT_FORMATS))}"
            )

    def _validate_level(self) -> None:
        valid_levels = ('file', 'function')
        level = getattr(self.cfg, 'level', None)
        if level not in valid_levels:
            raise ValueError(f"Invalid level '{level}'. Must be one of: {', '.join(valid_levels)}")
