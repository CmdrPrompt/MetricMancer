"""
Helper functions for CLI argument parsing and usage printing for ComplexityScanner.
"""

import argparse


def print_usage():
    """
    Prints usage instructions and parameter descriptions for the CLI.
    """
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
    print("\nOUTPUT FORMATTING:")
    print("  --output-format <format>     Set the output format. Options: 'human' (default CLI tree), 'html', 'json', 'machine' (CSV).")
    print("  --level <level>              Set the detail level for reports. Options: 'file' (default), 'function'.")
    print("  --hierarchical               (JSON only) Output the full hierarchical data model instead of a flat list.")
    print("  --list-hotspots              Display list of highest hotspots after analysis.")
    print("  --hotspot-threshold <score>  Minimum hotspot score to include (default: 50).")
    print("  --hotspot-output <file>      Save hotspot list to file instead of terminal.")
    print("  --review-strategy            Generate code review strategy report based on KPIs.")
    print("  --review-output <file>       Save review strategy to file (default: review_strategy.txt).")
    print("  --review-branch-only         Only include files changed in current branch in review strategy.")
    print("  --review-base-branch <name>  Base branch to compare against (default: main).")
    print("  --auto-report-filename       (Optional) Automatically generate a unique report filename based on date and directories.")
    print(
        "  --report-filename <filename> (Optional) Set the report filename directly. "
        "If used, scanned directories are not included in the filename. Optionally add --with-date to append date/time."
    )
    print("  --with-date                  (Optional) If used with --report-filename, appends date and time to the filename before extension.")
    print("  --report-folder <folder>     (Optional) Folder to write the report to. Default is current directory.")
    print("\nEXAMPLE:")
    print(
        "  python -m src.main src test --threshold-low 10 --threshold-high 20 "
        "--problem-file-threshold 15 --auto-report-filename"
    )
    print("  python -m src.main src test --auto-report-filename")
    print("  python -m src.main src test --report-filename myreport.html")
    print("  python -m src.main src test --report-filename myreport.html --with-date")
    print("  python -m src.main src test --report-folder reports")
    print("  python -m src.main src --list-hotspots --hotspot-threshold 100")
    print("  python -m src.main src --list-hotspots --hotspot-output hotspots.txt")
    print("  python -m src.main src --review-strategy --review-output review_strategy.txt")
    print("  python -m src.main src --review-strategy --review-branch-only")
    print("  python -m src.main src --review-strategy --review-branch-only --review-base-branch develop")


def parse_args():
    """
    Returns an ArgumentParser for the CLI arguments.
    """

    parser = argparse.ArgumentParser(description="Analyze cyclomatic complexity")
    parser.add_argument(
        "directories",
        nargs="+",
        help="Root folders to scan"
    )
    parser.add_argument(
        "--report-folder",
        type=str,
        default=None,
        help="Folder to write the report to. Default is current directory."
    )
    parser.add_argument(
        "--threshold-low",
        type=float,
        default=10.0,
        help="Threshold for low complexity (default: 10.0)"
    )
    parser.add_argument(
        "--threshold-high",
        type=float,
        default=20.0,
        help="Threshold for high complexity (default: 20.0)"
    )
    parser.add_argument(
        "--problem-file-threshold",
        type=float,
        default=None,
        help="Threshold for problem files (default: same as high threshold)"
    )
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
        default="human",
        help="Output format: 'human' (default), 'html', 'json', 'machine' (CSV)."
    )
    parser.add_argument(
        "--level",
        type=str,
        default="file",
        help="Detail level for reports: 'file' (default) or 'function'."
    )
    parser.add_argument(
        "--hierarchical",
        action="store_true",
        help="(JSON only) Output the full hierarchical data model."
    )
    parser.add_argument(
        "--list-hotspots",
        action="store_true",
        help="Display list of highest hotspots after analysis."
    )
    parser.add_argument(
        "--hotspot-threshold",
        type=int,
        default=50,
        help="Minimum hotspot score to include in hotspot list (default: 50)."
    )
    parser.add_argument(
        "--hotspot-output",
        type=str,
        default=None,
        help="Save hotspot list to file instead of displaying on terminal."
    )
    parser.add_argument(
        "--review-strategy",
        action="store_true",
        help="Generate code review strategy report based on complexity, churn, and ownership metrics."
    )
    parser.add_argument(
        "--review-output",
        type=str,
        default="review_strategy.txt",
        help="Output file for code review strategy report (default: review_strategy.txt)."
    )
    parser.add_argument(
        "--review-branch-only",
        action="store_true",
        help="Only include files changed in current branch in review strategy report."
    )
    parser.add_argument(
        "--review-base-branch",
        type=str,
        default="main",
        help="Base branch to compare against when using --review-branch-only (default: main)."
    )
    return parser
