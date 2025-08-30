
import argparse
import sys
from src.app import ComplexityScannerApp
from src.cli_helpers import print_usage, parse_args
from src.report_helpers import get_output_filename, ensure_report_folder
import os



def create_and_run_app(args):
    """
    Creates and runs the ComplexityScannerApp based on parsed CLI arguments.
    """
    output_file = get_output_filename(args)
    folder = ensure_report_folder(args.report_folder)
    if folder:
        output_file = os.path.join(folder, output_file)

    app = ComplexityScannerApp(
        directories=args.directories,
        threshold_low=args.threshold_low,
        threshold_high=args.threshold_high,
        problem_file_threshold=args.problem_file_threshold,
        output_file=output_file
    )
    app.run()

def main():
    if len(sys.argv) == 1:
        print_usage()
        sys.exit(0)
    parser = parse_args()
    args = parser.parse_args()
    create_and_run_app(args)

if __name__ == "__main__":
    main()
