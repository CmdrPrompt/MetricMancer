    # ...existing code...
import argparse
import sys
from src.app.metric_mancer_app import MetricMancerApp
from src.utilities.cli_helpers import parse_args, print_usage
from src.report.report_helpers import get_output_filename # This function is not in the provided context, but the import is being kept as per the original file.
from src.report.cli.cli_report_generator import CLIReportGenerator # This path is already correct in the provided context.
import os
from src.utilities.debug import debug_print

def main():
    debug_print(f"[DEBUG] main: sys.argv={sys.argv}")
    if len(sys.argv) == 1:
        print_usage()
        return

    parser = parse_args()
    parser.add_argument('--debug', action='store_true', help='Visa debugutskrifter')
    args = parser.parse_args()

    import src.utilities.debug
    src.utilities.debug.DEBUG = getattr(args, 'debug', False)
    debug_print(f"[DEBUG] main: args={args}")

    # Determine report generator based on output format
    if args.output_format == 'json':
        from src.report.json.json_report_generator import JSONReportGenerator
        generator_cls = JSONReportGenerator
    elif args.output_format == 'human' or args.output_format == 'machine':
        generator_cls = CLIReportGenerator
    else: # Default to HTML if a report filename is given
        debug_print("[DEBUG] main: HTML report mode")
        generator_cls = None # Will default to HTMLReportGenerator

    # Determine output file
    output_file = None
    if generator_cls is None or args.output_format == 'json': # HTML or JSON
        output_file = get_output_filename(args)

    app = MetricMancerApp(
        directories=args.directories,
        threshold_low=args.threshold_low,
        threshold_high=args.threshold_high,
        problem_file_threshold=args.problem_file_threshold,
        output_file=output_file,
        report_generator_cls=generator_cls,
        level=args.level,
        hierarchical=args.hierarchical,
        output_format=args.output_format
    )
    app.run()

if __name__ == "__main__":
    main()
