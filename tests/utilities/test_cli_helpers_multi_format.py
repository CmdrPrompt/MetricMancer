"""
TDD tests for multi-format CLI argument parsing.

Phase 2: CLI Parser Updates for Multi-Format Support

These tests verify that the CLI parser correctly handles:
1. New --output-formats argument (plural)
2. Backward compatibility with --output-format (singular)
3. Comma-separated format lists
4. Whitespace handling
5. Precedence rules
"""

from src.utilities.cli_helpers import parse_args


class TestCLIMultiFormatArgument:
    """Test that CLI parser accepts --output-formats argument."""

    def test_output_formats_argument_exists(self):
        """Test that --output-formats argument is recognized."""
        parser = parse_args()
        args = parser.parse_args(['src', '--output-formats', 'html,json'])

        assert hasattr(args, 'output_formats')

    def test_output_formats_single_value(self):
        """Test parsing single format in --output-formats."""
        parser = parse_args()
        args = parser.parse_args(['src', '--output-formats', 'html'])

        assert args.output_formats == 'html'

    def test_output_formats_comma_separated(self):
        """Test parsing comma-separated formats in --output-formats."""
        parser = parse_args()
        args = parser.parse_args(['src', '--output-formats', 'html,json,summary'])

        # Parser should pass the string as-is, AppConfig will split it
        assert args.output_formats == 'html,json,summary'

    def test_output_formats_with_whitespace(self):
        """Test that whitespace in format list is preserved (AppConfig handles it)."""
        parser = parse_args()
        args = parser.parse_args(['src', '--output-formats', 'html, json, summary'])

        assert args.output_formats == 'html, json, summary'


class TestCLIBackwardCompatibility:
    """Test backward compatibility with existing --output-format argument."""

    def test_output_format_singular_still_works(self):
        """Test that old --output-format (singular) still works."""
        parser = parse_args()
        args = parser.parse_args(['src', '--output-format', 'html'])

        assert hasattr(args, 'output_format')
        assert args.output_format == 'html'

    def test_both_arguments_coexist(self):
        """Test that both --output-format and --output-formats can be defined."""
        parser = parse_args()
        args = parser.parse_args([
            'src',
            '--output-format', 'summary',
            '--output-formats', 'html,json'
        ])

        assert hasattr(args, 'output_format')
        assert hasattr(args, 'output_formats')
        # Both should be present in parsed args
        assert args.output_format == 'summary'
        assert args.output_formats == 'html,json'

    def test_default_format_preserved(self):
        """Test that default format is still 'summary' for backward compat."""
        parser = parse_args()
        args = parser.parse_args(['src'])

        assert args.output_format == 'summary'


class TestCLIHelpText:
    """Test that help text documents the new argument."""

    def test_help_includes_output_formats(self):
        """Test that --help mentions --output-formats."""
        parser = parse_args()
        help_text = parser.format_help()

        assert '--output-formats' in help_text

    def test_help_shows_comma_separated_example(self):
        """Test that help text shows comma-separated example."""
        parser = parse_args()
        help_text = parser.format_help()

        # Should mention comma-separated or multiple formats
        assert 'comma' in help_text.lower() or 'multiple' in help_text.lower()


class TestCLIEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_formats_string_allowed(self):
        """Test that empty string is allowed (validation happens in AppConfig)."""
        parser = parse_args()
        args = parser.parse_args(['src', '--output-formats', ''])

        assert args.output_formats == ''

    def test_single_comma_only(self):
        """Test that single comma is parsed (AppConfig validates)."""
        parser = parse_args()
        args = parser.parse_args(['src', '--output-formats', ','])

        assert args.output_formats == ','

    def test_multiple_directories_with_formats(self):
        """Test that multiple directories work with --output-formats."""
        parser = parse_args()
        args = parser.parse_args(['src', 'tests', '--output-formats', 'html,json'])

        assert args.directories == ['src', 'tests']
        assert args.output_formats == 'html,json'
