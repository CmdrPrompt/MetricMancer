"""
Helper functions for CLI argument parsing and usage printing for ComplexityScanner.
"""
import argparse
import sys

def print_usage():
    """
    Prints usage instructions and parameter descriptions for the CLI.
    """
    print("\nUSAGE:")
    print("  python -m src.main <directories> [--cli-report | --html-report] [--threshold-low <value>] [--threshold-high <value>] [--problem-file-threshold <value>] [--auto-report-filename] [--report-filename <filename>] [--with-date] [--report-folder <folder>] [--debug]")
    print("\nPARAMETERS:")
    print("  <directories>                One or more root folders to scan for code complexity.")
    print("  --cli-report                 Generate CLI tree report output to the console.")
    print("  --html-report                Generate HTML report file output.")
    print("  --threshold-low              Sets the threshold for low complexity. Default: 10. Files/folders with complexity  this value are rated 'Low'.")
    print("  --threshold-high             Sets the threshold for high complexity. Default: 20. Files/folders with complexity > this value are rated 'High'.")
    print("  --problem-file-threshold     (Optional) Sets the threshold for individual file complexity. Files above this value are listed under each problematic folder in the summary.")
    print("  --auto-report-filename       (Optional) Automatically generate a unique report filename based on date and directories.")
    print("  --report-filename <filename> (Optional) Set the report filename directly. If used, scanned directories are not included in the filename. Optionally add --with-date to append date/time.")
    print("  --with-date                  (Optional) If used with --report-filename, appends date and time to the filename before extension.")
    print("  --report-folder <folder>     (Optional) Folder to write the report to. Default is current directory.")
    print("  --debug                      (Optional) Show debug output during execution.")
    print("\nNOTE:")
    print("  You must specify exactly one of --cli-report or --html-report. Using both or neither will result in an error.")
    print("\nEXAMPLE:")
    print("  python -m src.main src test --html-report --threshold-low 10 --threshold-high 20 --problem-file-threshold 15 --auto-report-filename")
    print("  python -m src.main src test --cli-report --auto-report-filename")
    print("  python -m src.main src test --html-report --report-filename myreport.html")
    print("  python -m src.main src test --html-report --report-filename myreport.html --with-date")
    print("  python -m src.main src test --cli-report --report-folder reports")

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
    parser.add_argument('--cli-report', action='store_true', help='Generate CLI tree report output to the console')
    parser.add_argument('--html-report', action='store_true', help='Generate HTML report file output')
    parser.add_argument('--debug', action='store_true', help='Show debug output during execution')
    return parser

def validate_and_parse_args():
    """
    Parse and validate CLI arguments, ensuring exactly one report type is specified.
    """
    parser = parse_args()
    args = parser.parse_args()
    
    # Check that exactly one of --cli-report or --html-report is specified
    if args.cli_report and args.html_report:
        print("Error: You cannot specify both --cli-report and --html-report at the same time.")
        print("Please choose exactly one report type.")
        print()
        print_usage()
        sys.exit(1)
    elif not args.cli_report and not args.html_report:
        print("Error: You must specify exactly one report type.")
        print("Please use either --cli-report or --html-report.")
        print()
        print_usage()
        sys.exit(1)
    
    return args
