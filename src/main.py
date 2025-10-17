import sys

import src.utilities.debug
from src.app.metric_mancer_app import MetricMancerApp
from src.config.app_config import AppConfig
from src.report.report_generator_factory import ReportGeneratorFactory
from src.report.report_helpers import get_output_filename
from src.utilities.cli_helpers import parse_args, print_usage
from src.utilities.debug import debug_print


def main():
    """
    Main entry point for MetricMancer.

    MetricMancer uses the Configuration Object Pattern to reduce complexity
    and code churn. All configuration logic is delegated to AppConfig and
    ReportGeneratorFactory.
    """
    # Ensure UTF-8 encoding for stdout/stderr for Unicode output (Python 3.7+)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    debug_print(f"[DEBUG] main: sys.argv={sys.argv}")
    if len(sys.argv) == 1:
        print_usage()
        return

    # Parse CLI arguments
    parser = parse_args()
    parser.add_argument('--debug', action='store_true', help='Visa debugutskrifter')
    args = parser.parse_args()

    # Set debug flag
    src.utilities.debug.DEBUG = getattr(args, 'debug', False)
    debug_print(f"[DEBUG] main: args={args}")

    # Create configuration from CLI arguments
    config = AppConfig.from_cli_args(args)

    # Handle output_file generation for file-based formats if not provided
    # Check if any format in output_formats needs a file
    file_based_formats = {'html', 'json', 'machine'}
    needs_file = any(fmt in file_based_formats for fmt in config.output_formats)

    if needs_file and not config.output_file:
        config.output_file = get_output_filename(args)

    debug_print(f"[DEBUG] main: config={config}")

    # For multi-format, don't create a single generator - let MetricMancerApp handle it
    if len(config.output_formats) > 1:
        # Multi-format: MetricMancerApp will create generators per format
        debug_print(f"[DEBUG] main: Multi-format mode - {len(config.output_formats)} formats")
        app = MetricMancerApp(config=config, report_generator_cls=None)
    else:
        # Single format: Use factory to create appropriate report generator (backward compat)
        generator_cls = ReportGeneratorFactory.create(config.output_format)
        if generator_cls is None:
            # Factory returns None for 'html' - use default ReportGenerator
            from src.report.report_generator import ReportGenerator
            generator_cls = ReportGenerator
        debug_print(f"[DEBUG] main: Single format mode - generator_cls={generator_cls}")
        app = MetricMancerApp(config=config, report_generator_cls=generator_cls)

    app.run()


if __name__ == "__main__":
    main()
