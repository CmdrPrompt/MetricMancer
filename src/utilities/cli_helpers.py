"""
Helper functions for CLI argument parsing and usage printing for ComplexityScanner.
"""
import argparse

def print_usage():
    """
    Prints usage instructions and parameter descriptions for the CLI.
    """
    print("\nUSAGE:")
    print("  python -m src.main <directories> [--threshold-low <value>] [--threshold-high <value>] [--problem-file-threshold <value>] [--auto-report-filename] [--report-filename <filename>] [--with-date] [--report-folder <folder>]")
    print("\nPARAMETERS:")
    print("  <directories>                One or more root folders to scan for code complexity.")
    print("  --threshold-low              Sets the threshold for low complexity. Default: 10. Files/folders with complexity  this value are rated 'Low'.")
    print("  --threshold-high             Sets the threshold for high complexity. Default: 20. Files/folders with complexity > this value are rated 'High'.")
    print("  --problem-file-threshold     (Optional) Sets the threshold for individual file complexity. Files above this value are listed under each problematic folder in the summary.")
    print("  --auto-report-filename       (Optional) Automatically generate a unique report filename based on date and directories.")
    print("  --report-filename <filename> (Optional) Set the report filename directly. If used, scanned directories are not included in the filename. Optionally add --with-date to append date/time.")
    print("  --with-date                  (Optional) If used with --report-filename, appends date and time to the filename before extension.")
    print("  --report-folder <folder>     (Optional) Folder to write the report to. Default is current directory.")
    print("\nEXAMPLE:")
    print("  python -m src.main src test --threshold-low 10 --threshold-high 20 --problem-file-threshold 15 --auto-report-filename")
    print("  python -m src.main src test --auto-report-filename")
    print("  python -m src.main src test --report-filename myreport.html")
    print("  python -m src.main src test --report-filename myreport.html --with-date")
    print("  python -m src.main src test --report-folder reports")

def parse_args():
    """
    Returns an ArgumentParser for the CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Analyze cyclomatic complexity")
    parser.add_argument("directories", nargs="+", help="Root folders to scan")
    parser.add_argument("--report-folder", type=str, default=None,
                        help="Folder to write the report to. Default is current directory.")
    parser.add_argument("--threshold-low", type=float, default=10.0,
                        help="Threshold for low complexity (default: 10.0)")
    parser.add_argument("--threshold-high", type=float, default=20.0,
                        help="Threshold for high complexity (default: 20.0)")
    parser.add_argument("--problem-file-threshold", type=float, default=None,
                        help="Threshold for problem files (default: same as high threshold)")
    parser.add_argument("--auto-report-filename", action="store_true",
                        help="Automatically generate a unique report filename based on date and directories.")
    parser.add_argument("--report-filename", type=str, default=None,
                        help="Set the report filename directly. If used, scanned directories are not included in the filename. Optionally add --with-date to append date/time.")
    parser.add_argument("--with-date", action="store_true",
                        help="If used with --report-filename, appends date and time to the filename before extension.")
    parser.add_argument('--cli-report', action='store_true', help='Print CLI tree report to the console')
    return parser
