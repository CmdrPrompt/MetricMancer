"""
Helper functions for CLI argument parsing and usage printing for ComplexityScanner.
"""

import argparse

from src.config.defaults import Defaults


def _print_basic_usage():
    """Print basic usage and parameter descriptions."""
    print("\nUSAGE:")
    print("  python -m src.main <directories> [options]")
    print("\nPARAMETERS:")
    print("  <directories>                One or more root folders to scan for code complexity.")
    print(
        "  --threshold-low              Sets the threshold for low complexity. Default: 10.\n"
        "                               Files/folders with complexity <= this value are rated 'Low'.\n"
        "                               Files/folders with complexity > this value are rated 'High'."
    )
    print(
        "  --problem-file-threshold     (Optional) Sets the threshold for individual file complexity. "
        "Files above this value are listed under each problematic folder in the summary."
    )
    print(
        "  --extreme-complexity-threshold  Threshold for extreme complexity (default: 100). "
        "Files above this are flagged as critical in summary report regardless of churn."
    )


def _print_output_options():
    """Print output formatting options."""
    print("\nOUTPUT FORMATTING:")
    print("  --output-format <format>     Set the output format. Options: 'summary' (default dashboard), "
          "'quick-wins' (prioritized improvements), 'tree' (file tree), 'html', 'json'.")
    print("  --output-formats <formats>   Generate multiple formats in one run (comma-separated). "
          "Example: 'html,json,summary,review-strategy'. Includes 'review-strategy' and 'review-strategy-branch'. "
          "Scans code once, generates all formats.")
    print("  --level <level>              Set the detail level for reports. Options: 'file' (default), 'function'.")
    print("  --hierarchical               (JSON only) Output the full hierarchical data model "
          "instead of a flat list.")
    print("  --churn-period <days>        Number of days to analyze for code churn (default: 30).")
    print("  --auto-report-filename       (Optional) Automatically generate a unique report filename "
          "based on date and directories.")
    print(
        "  --report-filename <filename> (Optional) Set the report filename directly. "
        "If used, scanned directories are not included in the filename. Optionally add --with-date to append date/time."
    )
    print("  --with-date                  (Optional) If used with --report-filename, "
          "appends date and time to the filename before extension.")
    print("  --report-folder <folder>     (Optional) Folder to write all reports to. Default is 'output'.")


def _print_hotspot_options():
    """Print hotspot analysis options."""
    print("\nHOTSPOT ANALYSIS:")
    print("  --list-hotspots              Display list of highest hotspots after analysis.")
    print("  --hotspot-threshold <score>  Minimum hotspot score to include (default: 50).")
    print("  --hotspot-output <file>      Save hotspot list to file instead of terminal. "
          "Use .md for markdown (default), .txt for plain text.")


def _print_review_options():
    """Print code review strategy options."""
    print("\nCODE REVIEW STRATEGY:")
    print("  --review-strategy            Generate code review strategy report based on KPIs.")
    print("  --review-output <file>       Save review strategy to file (default: review_strategy.md, "
          "supports .txt and .md).")
    print("  --review-branch-only         Only include files changed in current branch in review strategy.")
    print("  --review-base-branch <name>  Base branch to compare against (default: main).")


def _print_delta_options():
    """Print delta review options."""
    print("\nDELTA REVIEW (FUNCTION-LEVEL):")
    print("  --delta-review               Generate delta-based review (function-level changes only).")
    print("  --delta-base-branch <name>   Base branch for delta comparison (default: main).")
    print("  --delta-target-branch <name> Target branch for delta comparison (default: current branch).")
    print("  --delta-output <file>        Output file for delta review (default: delta_review.md).")


def _print_examples():
    """Print usage examples."""
    print("\nEXAMPLE:")
    print(
        "  python -m src.main src test --threshold-low 10 --threshold-high 20 "
        "--problem-file-threshold 15 --auto-report-filename"
    )
    print("  python -m src.main src test --auto-report-filename")
    print("  python -m src.main src test --report-filename myreport.html")
    print("  python -m src.main src test --report-filename myreport.html --with-date")
    print("  python -m src.main src test --report-folder reports")
    print("  python -m src.main src test --output-formats html,json,summary")
    print("  python -m src.main src --list-hotspots --hotspot-threshold 100")
    print("  python -m src.main src --list-hotspots --hotspot-output hotspots.md")
    print("  python -m src.main src --review-strategy --review-output review_strategy.md")
    print("  python -m src.main src --review-strategy --review-branch-only")
    print("  python -m src.main src --review-strategy --review-branch-only --review-base-branch develop")
    print("  python -m src.main src --delta-review")
    print("  python -m src.main src --delta-review --delta-base-branch main --delta-target-branch feature/new")


def print_usage():
    """
    Prints usage instructions and parameter descriptions for the CLI.
    """
    _print_basic_usage()
    _print_output_options()
    _print_hotspot_options()
    _print_review_options()
    _print_delta_options()
    _print_examples()


def _add_basic_args(parser):
    """Add basic directory and threshold arguments."""
    parser.add_argument(
        "directories",
        nargs="+",
        help="Root folders to scan"
    )
    parser.add_argument(
        "--report-folder",
        type=str,
        default=None,
        help=f"Folder to write all reports to. Default is '{Defaults.REPORT_FOLDER}'."
    )
    parser.add_argument(
        "--threshold-low",
        type=float,
        default=Defaults.THRESHOLD_LOW,
        help=f"Threshold for low complexity (default: {Defaults.THRESHOLD_LOW})"
    )
    parser.add_argument(
        "--threshold-high",
        type=float,
        default=Defaults.THRESHOLD_HIGH,
        help=f"Threshold for high complexity (default: {Defaults.THRESHOLD_HIGH})"
    )
    parser.add_argument(
        "--problem-file-threshold",
        type=float,
        default=None,
        help="Threshold for problem files (default: same as high threshold)"
    )
    parser.add_argument(
        "--extreme-complexity-threshold",
        type=int,
        default=Defaults.EXTREME_COMPLEXITY_THRESHOLD,
        help=(
            f"Threshold for extreme complexity in summary report. "
            f"Files above this threshold are flagged as critical regardless of churn "
            f"(default: {Defaults.EXTREME_COMPLEXITY_THRESHOLD})"
        )
    )


def _add_output_args(parser):
    """Add output formatting and report generation arguments."""
    parser.add_argument(
        "--auto-report-filename",
        action="store_true",
        help="Automatically generate a unique report filename based on date and directories."
    )
    parser.add_argument(
        "--report-filename",
        type=str,
        default=None,
        help=(
            "Set the report filename directly. If used, scanned directories are not included in the filename. "
            "Optionally add --with-date to append date/time."
        )
    )
    parser.add_argument(
        "--with-date",
        action="store_true",
        help="If used with --report-filename, appends date and time to the filename before extension."
    )
    parser.add_argument(
        "--output-format",
        type=str,
        default=Defaults.OUTPUT_FORMAT,
        help=f"Output format: '{Defaults.OUTPUT_FORMAT}' (default dashboard), 'quick-wins' (prioritized improvements), "
        "'tree' (file tree), 'html', 'json'."
    )
    parser.add_argument(
        "--output-formats",
        type=str,
        default=None,
        help="Generate multiple output formats in a single run (comma-separated). "
             "Example: 'html,json,summary,review-strategy'. "
             "Includes 'review-strategy' (full repo) and 'review-strategy-branch' (changed files only). "
             "Eliminates redundant scanning for multiple formats."
    )
    parser.add_argument(
        "--level",
        type=str,
        default=Defaults.LEVEL,
        help=f"Detail level for reports: '{Defaults.LEVEL}' (default) or 'function'."
    )
    parser.add_argument(
        "--hierarchical",
        action="store_true",
        help="(JSON only) Output the full hierarchical data model."
    )
    parser.add_argument(
        "--churn-period",
        type=int,
        default=Defaults.CHURN_PERIOD,
        help=f"Number of days to analyze for code churn (default: {Defaults.CHURN_PERIOD})."
    )
    parser.add_argument(
        "--no-timing",
        action="store_true",
        help="Suppress timing information output."
    )


def _add_hotspot_args(parser):
    """Add hotspot analysis arguments."""
    parser.add_argument(
        "--list-hotspots",
        action="store_true",
        help="Display list of highest hotspots after analysis."
    )
    parser.add_argument(
        "--hotspot-threshold",
        type=int,
        default=Defaults.HOTSPOT_THRESHOLD,
        help=f"Minimum hotspot score to include in hotspot list (default: {Defaults.HOTSPOT_THRESHOLD})."
    )
    parser.add_argument(
        "--hotspot-output",
        type=str,
        default=None,
        help="Save hotspot list to file instead of displaying on terminal. "
             "Supports .md (markdown) and .txt (plain text). Default format is markdown."
    )


def _add_review_args(parser):
    """Add code review strategy arguments."""
    parser.add_argument(
        "--review-strategy",
        action="store_true",
        help="Generate code review strategy report based on complexity, churn, and ownership metrics."
    )
    parser.add_argument(
        "--review-output",
        type=str,
        default=Defaults.REVIEW_OUTPUT,
        help=f"Output file for code review strategy report (default: {Defaults.REVIEW_OUTPUT}, supports .txt and .md)."
    )
    parser.add_argument(
        "--review-branch-only",
        action="store_true",
        help="Only include files changed in current branch in review strategy report."
    )
    parser.add_argument(
        "--review-base-branch",
        type=str,
        default=Defaults.REVIEW_BASE_BRANCH,
        help=f"Base branch to compare against when using --review-branch-only (default: {Defaults.REVIEW_BASE_BRANCH})."
    )
    parser.add_argument(
        "--include-review-tab",
        action="store_true",
        help="Include Code Review tab in HTML report with review recommendations. "
             "Use with --review-branch-only to show only changed files."
    )


def _add_delta_args(parser):
    """Add delta review arguments."""
    parser.add_argument(
        "--delta-review",
        action="store_true",
        help="Generate delta-based review strategy with function-level analysis."
    )
    parser.add_argument(
        "--delta-base-branch",
        type=str,
        default=Defaults.DELTA_BASE_BRANCH,
        help=f"Base branch for delta comparison (default: {Defaults.DELTA_BASE_BRANCH})."
    )
    parser.add_argument(
        "--delta-target-branch",
        type=str,
        default=None,
        help="Target branch for delta comparison (default: current branch)."
    )
    parser.add_argument(
        "--delta-output",
        type=str,
        default=Defaults.DELTA_OUTPUT,
        help=f"Output file for delta review report (default: {Defaults.DELTA_OUTPUT})."
    )


def parse_args():
    """
    Returns an ArgumentParser for the CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Analyze cyclomatic complexity")

    _add_basic_args(parser)
    _add_output_args(parser)
    _add_hotspot_args(parser)
    _add_review_args(parser)
    _add_delta_args(parser)

    return parser
