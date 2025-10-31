import sys
import src.utilities.debug
from src.app.metric_mancer_app import MetricMancerApp
from src.config.app_config import AppConfig
from src.utilities.cli_helpers import parse_args, print_usage
from src.utilities.debug import debug_print


def setup_utf8_encoding():
    """
    Ensure UTF-8 encoding for stdout/stderr for Unicode output (Python 3.7+).
    """
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')


def setup_debug_mode(args):
    """
    Configure debug mode based on CLI arguments.

    Args:
        args: Parsed CLI arguments
    """
    src.utilities.debug.DEBUG = getattr(args, 'debug', False)
    debug_print(f"[DEBUG] main: args={args}")


def create_app_from_config(config):
    """
    Create MetricMancerApp instance from configuration.
    Uses Configuration Object Pattern - all logic delegated to AppConfig and MetricMancerApp.

    Args:
        config: AppConfig instance

    Returns:
        MetricMancerApp: Configured application instance
    """
    debug_print(f"[DEBUG] main: config={config}")
    # Configuration Object Pattern: AppConfig handles all format-specific logic
    # MetricMancerApp uses factory pattern internally for generator selection
    return MetricMancerApp(config=config)


def main():
    """
    Main entry point for MetricMancer.

    Follows Single Responsibility Principle: main() only orchestrates high-level flow.
    All business logic delegated to specialized components per Configuration Object Pattern.
    """
    setup_utf8_encoding()

    debug_print(f"[DEBUG] main: sys.argv={sys.argv}")
    if len(sys.argv) == 1:
        print_usage()
        return

    # Parse CLI arguments - delegated to CLI helpers
    parser = parse_args()
    parser.add_argument('--debug', action='store_true', help='Visa debugutskrifter')
    args = parser.parse_args()

    setup_debug_mode(args)

    # Create configuration - Configuration Object Pattern
    config = AppConfig.from_cli_args(args)

    # Create and run application - all logic delegated to MetricMancerApp
    app = create_app_from_config(config)
    app.run()


if __name__ == "__main__":
    main()
