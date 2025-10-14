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

    Simplified version using Configuration Object Pattern to reduce complexity
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

    # Handle output_file generation for json/html formats if not provided
    if config.output_format in ['html', 'json'] and not config.output_file:
        config.output_file = get_output_filename(args)

    # Use factory to create appropriate report generator
    generator_cls = ReportGeneratorFactory.create(config.output_format)

    debug_print(f"[DEBUG] main: config={config}")
    debug_print(f"[DEBUG] main: generator_cls={generator_cls}")

    # Create and run application
    app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
    app.run()


if __name__ == "__main__":
    main()
