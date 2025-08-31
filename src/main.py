    # ...existing code...
import argparse
import sys
from src.app import ComplexityScannerApp
from src.cli_helpers import print_usage, parse_args
from src.report_helpers import get_output_filename, ensure_report_folder
from src.report.cli_report_generator import CLIReportGenerator
import os
from src.debug import debug_print

def main():
    print(f"[DEBUG] main: sys.argv={sys.argv}")
    if len(sys.argv) == 1:
        print_usage()
        sys.exit(0)
    parser = parse_args()
    parser.add_argument('--debug', action='store_true', help='Visa debugutskrifter')
    args = parser.parse_args()
    import src.debug
    src.debug.DEBUG = getattr(args, 'debug', False)
    debug_print(f"[DEBUG] main: args={args}")
    if getattr(args, 'cli_report', False):
        debug_print("[DEBUG] main: CLI report mode")
        app = ComplexityScannerApp(
            directories=args.directories,
            threshold_low=args.threshold_low,
            threshold_high=args.threshold_high,
            problem_file_threshold=args.problem_file_threshold,
            output_file=None,
            report_generator_cls=CLIReportGenerator
        )
        app.run()
    else:
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

if __name__ == "__main__":
    main()
