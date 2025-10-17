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

    # Handle delta review (function-level analysis)
    if config.delta_review:
        from src.analysis.delta import DeltaAnalyzer, DeltaReviewStrategyFormat
        import os

        debug_print(f"[DEBUG] main: Delta review mode activated")
        debug_print(f"[DEBUG] main: Base={config.delta_base_branch}, Target={config.delta_target_branch}")

        # Use first directory as repo path
        repo_path = config.directories[0]

        try:
            # Run delta analysis
            analyzer = DeltaAnalyzer(repo_path=repo_path)
            delta_diff = analyzer.analyze_branch_delta(
                base_branch=config.delta_base_branch,
                target_branch=config.delta_target_branch
            )

            # Format report
            formatter = DeltaReviewStrategyFormat()
            report = formatter.format(delta_diff)

            # Write to file
            output_path = os.path.join(config.report_folder, config.delta_output)
            os.makedirs(config.report_folder, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"\n✅ Delta review report generated: {output_path}")
            print(f"\n📊 Summary:")
            print(f"  - Functions changed: {len(delta_diff.added_functions) + len(delta_diff.modified_functions) + len(delta_diff.deleted_functions)}")
            print(f"  - Complexity delta: {delta_diff.total_complexity_delta:+d}")
            print(f"  - Estimated review time: {delta_diff.total_review_time_minutes} minutes")

            if delta_diff.critical_changes:
                print(f"  - Critical changes: {len(delta_diff.critical_changes)}")
            if delta_diff.refactorings:
                print(f"  - Refactorings: {len(delta_diff.refactorings)}")

            return

        except Exception as e:
            print(f"\n❌ Error generating delta review: {e}")
            import traceback
            traceback.print_exc()
            return

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
