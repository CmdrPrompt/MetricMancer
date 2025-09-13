    # ...existing code...
import argparse
import sys
from src.app.app import ComplexityScannerApp
from src.utilities.cli_helpers import print_usage, parse_args
from src.report.report_helpers import get_output_filename # This function is not in the provided context, but the import is being kept as per the original file.
from src.report.cli.cli_report_generator import CLIReportGenerator # This path is already correct in the provided context.
import os
from src.utilities.debug import debug_print

def main():
    debug_print(f"[DEBUG] main: sys.argv={sys.argv}")
    if len(sys.argv) == 1:
        print_usage()
        sys.exit(0)
    parser = parse_args()
    parser.add_argument('--debug', action='store_true', help='Visa debugutskrifter')
    args = parser.parse_args()
    import src.utilities.debug
    src.utilities.debug.DEBUG = getattr(args, 'debug', False)
    debug_print(f"[DEBUG] main: args={args}")
    # Default: human-readable CLI report unless HTML output is explicitly requested
    if getattr(args, 'report_filename', None) or getattr(args, 'auto_report_filename', False):
        debug_print("[DEBUG] main: HTML report mode")
        app = ComplexityScannerApp(
            directories=args.directories,
            threshold_low=args.threshold_low,
            threshold_high=args.threshold_high,
            problem_file_threshold=args.problem_file_threshold,
            output_file=get_output_filename(args),
            report_generator_cls=None
        )
        app.run()
    else:
        debug_print("[DEBUG] main: CLI report mode (default)")
        app = ComplexityScannerApp(
            directories=args.directories,
            threshold_low=args.threshold_low,
            threshold_high=args.threshold_high,
            problem_file_threshold=args.problem_file_threshold,
            output_file=None,
            report_generator_cls=CLIReportGenerator
        )
        app.run()

if __name__ == "__main__":
    main()
