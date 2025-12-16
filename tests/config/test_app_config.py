"""
Unit tests for AppConfig class.

Tests the Configuration Object pattern implementation including
factory methods, validation, and default values.
"""

import pytest
from argparse import Namespace

from src.config.app_config import AppConfig


class TestAppConfigCreation:
    """Test AppConfig instance creation."""

    def test_minimal_config(self):
        """Test creating config with only required fields."""
        config = AppConfig(directories=['src'])

        assert config.directories == ['src']
        assert config.threshold_low == 10.0
        assert config.threshold_high == 20.0
        assert config.output_format == "summary"
        assert config.report_folder == "output"

    def test_full_config(self):
        """Test creating config with all fields specified."""
        config = AppConfig(
            directories=['src', 'tests'],
            threshold_low=5.0,
            threshold_high=15.0,
            problem_file_threshold=12.0,
            output_format='json',
            output_file='report.json',
            report_folder='reports',
            level='function',
            hierarchical=True,
            list_hotspots=True,
            hotspot_threshold=100,
            hotspot_output='hotspots.md',
            review_strategy=True,
            review_output='review.md',
            review_branch_only=True,
            review_base_branch='develop',
            debug=True
        )

        assert config.directories == ['src', 'tests']
        assert config.threshold_low == 5.0
        assert config.threshold_high == 15.0
        assert config.problem_file_threshold == 12.0
        assert config.output_format == 'json'
        assert config.output_file == 'report.json'
        assert config.report_folder == 'reports'
        assert config.level == 'function'
        assert config.hierarchical is True
        assert config.list_hotspots is True
        assert config.hotspot_threshold == 100
        assert config.hotspot_output == 'hotspots.md'
        assert config.review_strategy is True
        assert config.review_output == 'review.md'
        assert config.review_branch_only is True
        assert config.review_base_branch == 'develop'
        assert config.debug is True


class TestAppConfigFromCLIArgs:
    """Test creating AppConfig from CLI arguments."""

    def test_from_minimal_args(self):
        """Test creating config from minimal CLI arguments."""
        args = Namespace(
            directories=['src'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=None,
            output_format='summary',
            level='file',
            hierarchical=False
        )

        config = AppConfig.from_cli_args(args)

        assert config.directories == ['src']
        assert config.threshold_low == 10.0
        assert config.threshold_high == 20.0
        assert config.output_format == 'summary'

    def test_from_full_args(self):
        """Test creating config from full CLI arguments."""
        args = Namespace(
            directories=['src', 'tests'],
            threshold_low=5.0,
            threshold_high=15.0,
            problem_file_threshold=12.0,
            output_format='json',
            report_folder='reports',
            level='function',
            hierarchical=True,
            list_hotspots=True,
            hotspot_threshold=100,
            hotspot_output='hotspots.md',
            review_strategy=True,
            review_output='review.md',
            review_branch_only=True,
            review_base_branch='develop',
            debug=True
        )

        config = AppConfig.from_cli_args(args)

        assert config.directories == ['src', 'tests']
        assert config.threshold_low == 5.0
        assert config.output_format == 'json'
        assert config.report_folder == 'reports'
        assert config.list_hotspots is True
        assert config.review_strategy is True
        assert config.debug is True

    def test_from_args_with_defaults(self):
        """Test that missing optional args use defaults."""
        args = Namespace(
            directories=['src'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=None,
            output_format='summary',
            level='file',
            hierarchical=False
        )

        config = AppConfig.from_cli_args(args)

        assert config.report_folder == 'output'
        assert config.list_hotspots is False
        assert config.hotspot_threshold == 50
        assert config.review_strategy is False
        assert config.review_output == 'review_strategy.md'
        assert config.debug is False


class TestAppConfigValidation:
    """Test AppConfig validation logic."""

    def test_validate_success(self):
        """Test validation passes with valid config."""
        config = AppConfig(directories=['src'])
        config.validate()  # Should not raise

    def test_validate_empty_directories(self):
        """Test validation fails with empty directories."""
        config = AppConfig(directories=[])

        with pytest.raises(ValueError, match="At least one directory"):
            config.validate()

    def test_validate_threshold_order(self):
        """Test validation fails if threshold_low >= threshold_high."""
        config = AppConfig(
            directories=['src'],
            threshold_low=20.0,
            threshold_high=10.0
        )

        with pytest.raises(ValueError, match="threshold_low.*must be less than"):
            config.validate()

    def test_validate_equal_thresholds(self):
        """Test validation fails if thresholds are equal."""
        config = AppConfig(
            directories=['src'],
            threshold_low=15.0,
            threshold_high=15.0
        )

        with pytest.raises(ValueError, match="threshold_low.*must be less than"):
            config.validate()

    def test_validate_negative_thresholds(self):
        """Test validation fails with negative thresholds."""
        config = AppConfig(
            directories=['src'],
            threshold_low=-5.0,
            threshold_high=10.0
        )

        with pytest.raises(ValueError, match="Thresholds must be non-negative"):
            config.validate()

    def test_validate_negative_hotspot_threshold(self):
        """Test validation fails with negative hotspot threshold."""
        config = AppConfig(
            directories=['src'],
            hotspot_threshold=-10
        )

        with pytest.raises(ValueError, match="Hotspot threshold must be non-negative"):
            config.validate()

    def test_validate_invalid_output_format(self):
        """Test validation fails with invalid output format."""
        config = AppConfig(
            directories=['src'],
            output_format='invalid_format'
        )

        with pytest.raises(ValueError, match="Invalid output format"):
            config.validate()

    def test_validate_invalid_level(self):
        """Test validation fails with invalid level."""
        config = AppConfig(
            directories=['src'],
            level='invalid_level'
        )

        with pytest.raises(ValueError, match="Invalid level"):
            config.validate()

    def test_validate_all_valid_formats(self):
        """Test validation passes for all valid output formats."""
        valid_formats = [
            'summary', 'quick-wins', 'tree', 'html', 'json', 'machine'
        ]

        for fmt in valid_formats:
            config = AppConfig(directories=['src'], output_format=fmt)
            config.validate()  # Should not raise

    def test_validate_all_valid_levels(self):
        """Test validation passes for all valid levels."""
        for level in ['file', 'function']:
            config = AppConfig(directories=['src'], level=level)
            config.validate()  # Should not raise


class TestAppConfigRepr:
    """Test AppConfig string representation."""

    def test_repr_contains_key_info(self):
        """Test __repr__ contains key configuration info."""
        config = AppConfig(
            directories=['src', 'tests'],
            output_format='json',
            list_hotspots=True
        )

        repr_str = repr(config)

        assert 'AppConfig' in repr_str
        assert 'src' in repr_str
        assert 'tests' in repr_str
        assert 'json' in repr_str
        assert 'hotspots=True' in repr_str


class TestAppConfigDefaults:
    """Test default values in AppConfig."""

    def test_default_thresholds(self):
        """Test default threshold values."""
        config = AppConfig(directories=['src'])

        assert config.threshold_low == 10.0
        assert config.threshold_high == 20.0
        assert config.problem_file_threshold is None

    def test_default_output_settings(self):
        """Test default output settings."""
        config = AppConfig(directories=['src'])

        assert config.output_format == 'summary'
        assert config.output_file is None
        assert config.report_folder == 'output'
        assert config.level == 'file'
        assert config.hierarchical is False

    def test_default_hotspot_settings(self):
        """Test default hotspot settings."""
        config = AppConfig(directories=['src'])

        assert config.list_hotspots is False
        assert config.hotspot_threshold == 50
        assert config.hotspot_output is None

    def test_default_review_settings(self):
        """Test default review strategy settings."""
        config = AppConfig(directories=['src'])

        assert config.review_strategy is False
        assert config.review_output == 'review_strategy.md'
        assert config.review_branch_only is False
        assert config.review_base_branch == 'main'

    def test_default_debug(self):
        """Test default debug setting."""
        config = AppConfig(directories=['src'])

        assert config.debug is False
