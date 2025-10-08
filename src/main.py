
import argparse
import sys
from src.app.metric_mancer_app import MetricMancerApp
from src.utilities.cli_helpers import parse_args, print_usage
from src.report.report_helpers import get_output_filename
from src.report.cli.cli_report_generator import CLIReportGenerator
import os
from src.utilities.debug import debug_print

def main():
    # Ensure UTF-8 encoding for stdout/stderr for Unicode output (Python 3.7+)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

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
    elif args.output_format == 'machine':
        generator_cls = CLIReportGenerator
    elif args.output_format == 'html':
        debug_print("[DEBUG] main: HTML report mode")
        generator_cls = None  # Will default to HTMLReportGenerator
    else:
        generator_cls = CLIReportGenerator


    # Determine output file
    output_file = None
    if args.output_format in ['html', 'json']:
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
