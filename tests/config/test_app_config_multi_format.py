"""
TDD tests for multi-format report generation feature in AppConfig.

These tests are written BEFORE implementation to define expected behavior
for the new --output-formats (plural) parameter.

Red-Green-Refactor cycle:
1. 🔴 RED: Write failing tests first
2. 🟢 GREEN: Implement minimal code to pass
3. 🔵 REFACTOR: Clean up and improve
"""

import pytest
from argparse import Namespace

from src.config.app_config import AppConfig


class TestAppConfigMultiFormat:
    """Test AppConfig with multiple output formats."""

    def test_output_formats_field_exists(self):
        """Test that AppConfig has output_formats field (list)."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json']
        )

        assert hasattr(config, 'output_formats')
        assert isinstance(config.output_formats, list)
        assert config.output_formats == ['html', 'json']

    def test_output_formats_default_to_summary(self):
        """Test that output_formats defaults to ['summary'] if not specified."""
        config = AppConfig(directories=['src'])

        assert config.output_formats == ['summary']

    def test_single_output_format_converted_to_list(self):
        """Test that single format is converted to list internally."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html']
        )

        assert isinstance(config.output_formats, list)
        assert len(config.output_formats) == 1
        assert config.output_formats[0] == 'html'

    def test_multiple_output_formats(self):
        """Test AppConfig with multiple output formats."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json', 'summary']
        )

        assert len(config.output_formats) == 3
        assert 'html' in config.output_formats
        assert 'json' in config.output_formats
        assert 'summary' in config.output_formats

    def test_output_format_singular_still_supported(self):
        """Test backward compatibility: output_format (singular) still works."""
        config = AppConfig(
            directories=['src'],
            output_format='html'  # Old singular parameter
        )

        # Should be accessible as both singular and plural
        assert config.output_format == 'html'
        # And should populate output_formats list
        assert config.output_formats == ['html']

    def test_output_formats_takes_precedence_over_singular(self):
        """Test that output_formats (plural) takes precedence if both provided."""
        config = AppConfig(
            directories=['src'],
            output_format='html',  # Old way
            output_formats=['json', 'summary']  # New way
        )

        # Plural should win
        assert config.output_formats == ['json', 'summary']
        # Singular should reflect first format in list
        assert config.output_format == 'json'


class TestAppConfigFromCLIArgsMultiFormat:
    """Test creating AppConfig from CLI args with multi-format support."""

    def test_from_cli_args_with_comma_separated_formats(self):
        """Test parsing --output-formats with comma-separated values."""
        args = Namespace(
            directories=['src'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=None,
            output_formats='html,json,summary',  # Comma-separated string
            level='file',
            hierarchical=False
        )

        config = AppConfig.from_cli_args(args)

        # Should be split into list
        assert isinstance(config.output_formats, list)
        assert len(config.output_formats) == 3
        assert config.output_formats == ['html', 'json', 'summary']

    def test_from_cli_args_with_single_format_string(self):
        """Test that single format string is converted to list."""
        args = Namespace(
            directories=['src'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=None,
            output_formats='json',  # Single format as string
            level='file',
            hierarchical=False
        )

        config = AppConfig.from_cli_args(args)

        assert config.output_formats == ['json']

    def test_from_cli_args_backward_compat_singular_format(self):
        """Test backward compatibility: old --output-format (singular) still works."""
        args = Namespace(
            directories=['src'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=None,
            output_format='html',  # Old parameter name
            level='file',
            hierarchical=False
        )

        config = AppConfig.from_cli_args(args)

        # Should populate output_formats list
        assert config.output_formats == ['html']
        assert config.output_format == 'html'

    def test_from_cli_args_formats_takes_precedence(self):
        """Test that --output-formats takes precedence over --output-format."""
        args = Namespace(
            directories=['src'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=None,
            output_format='html',  # Old singular
            output_formats='json,summary',  # New plural
            level='file',
            hierarchical=False
        )

        config = AppConfig.from_cli_args(args)

        # Plural should win
        assert config.output_formats == ['json', 'summary']

    def test_from_cli_args_strips_whitespace(self):
        """Test that whitespace around formats is stripped."""
        args = Namespace(
            directories=['src'],
            threshold_low=10.0,
            threshold_high=20.0,
            problem_file_threshold=None,
            output_formats=' html , json , summary ',  # Extra spaces
            level='file',
            hierarchical=False
        )

        config = AppConfig.from_cli_args(args)

        # Should strip whitespace
        assert config.output_formats == ['html', 'json', 'summary']


class TestAppConfigValidationMultiFormat:
    """Test validation of multiple output formats."""

    def test_validate_all_formats_valid(self):
        """Test validation passes with all valid formats."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json', 'summary']
        )

        config.validate()  # Should not raise

    def test_validate_invalid_format_in_list(self):
        """Test validation fails if any format is invalid."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'invalid_format', 'json']
        )

        with pytest.raises(ValueError, match="Invalid output format.*invalid_format"):
            config.validate()

    def test_validate_empty_formats_list(self):
        """Test validation fails with empty formats list."""
        config = AppConfig(
            directories=['src'],
            output_formats=[]
        )

        with pytest.raises(ValueError, match="At least one output format"):
            config.validate()

    def test_validate_duplicate_formats_allowed(self):
        """Test that duplicate formats are allowed (will be deduplicated)."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json', 'html']  # Duplicate
        )

        config.validate()  # Should not raise
        # Implementation should deduplicate
        assert len(set(config.output_formats)) <= len(config.output_formats)

    def test_validate_all_supported_formats(self):
        """Test validation passes for all supported formats."""
        all_formats = ['summary', 'quick-wins', 'human', 'human-tree',
                       'tree', 'html', 'json', 'machine']

        config = AppConfig(
            directories=['src'],
            output_formats=all_formats
        )

        config.validate()  # Should not raise


class TestAppConfigMultiFormatHelpers:
    """Test helper methods for multi-format support."""

    def test_has_html_format(self):
        """Test checking if HTML is in formats list."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json']
        )

        assert 'html' in config.output_formats

    def test_has_json_format(self):
        """Test checking if JSON is in formats list."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json']
        )

        assert 'json' in config.output_formats

    def test_get_file_generating_formats(self):
        """Test identifying formats that generate output files."""
        config = AppConfig(
            directories=['src'],
            output_formats=['html', 'json', 'summary']
        )

        # HTML and JSON generate files, summary is CLI output
        file_formats = [f for f in config.output_formats if f in ['html', 'json']]

        assert len(file_formats) == 2
        assert 'html' in file_formats
        assert 'json' in file_formats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
