"""
Timing Reporter Module

Handles timing measurements and reporting for analysis steps.
Separates timing concerns from main application logic.
"""
import time
from typing import Dict, Any, Optional


class TimingReporter:
    """
    Manages timing measurements and generates timing reports.

    Responsibilities:
    - Measure execution time for various steps
    - Format and print timing summaries
    """

    def __init__(self):
        """Initialize TimingReporter with empty timing data."""
        self.timings = {
            'scan_start': 0.0,
            'scan_end': 0.0,
            'analyze_start': 0.0,
            'analyze_end': 0.0,
            'reportgen_start': 0.0,
            'reportgen_end': 0.0
        }

    def start_scan(self):
        """Mark the start of scanning phase."""
        self.timings['scan_start'] = time.perf_counter()

    def end_scan(self):
        """Mark the end of scanning phase."""
        self.timings['scan_end'] = time.perf_counter()

    def start_analysis(self):
        """Mark the start of analysis phase."""
        self.timings['analyze_start'] = time.perf_counter()

    def end_analysis(self):
        """Mark the end of analysis phase."""
        self.timings['analyze_end'] = time.perf_counter()

    def start_report_generation(self):
        """Mark the start of report generation phase."""
        self.timings['reportgen_start'] = time.perf_counter()

    def end_report_generation(self):
        """Mark the end of report generation phase."""
        self.timings['reportgen_end'] = time.perf_counter()

    def get_scan_duration(self) -> float:
        """Get scanning duration in seconds."""
        return self.timings['scan_end'] - self.timings['scan_start']

    def get_analysis_duration(self) -> float:
        """Get analysis duration in seconds."""
        return self.timings['analyze_end'] - self.timings['analyze_start']

    def get_report_generation_duration(self) -> float:
        """Get report generation duration in seconds."""
        return self.timings['reportgen_end'] - self.timings['reportgen_start']

    @staticmethod
    def safe_format(val: Any) -> str:
        """
        Safely format a value as float with 2 decimal places.

        Args:
            val: Value to format

        Returns:
            Formatted string or "N/A" if formatting fails
        """
        try:
            return f"{float(val):.2f}"
        except Exception:
            return "N/A"

    def print_analysis_breakdown(self, analyzer_timing: Optional[Dict] = None):
        """
        Print detailed breakdown of analysis timing.

        Args:
            analyzer_timing: Optional timing data from analyzer
        """
        if not analyzer_timing:
            return

        print("-- Analysis breakdown --")
        print(f"  Cache pre-building:     "
              f"{self.safe_format(analyzer_timing.get('cache_prebuild', 0))} seconds")
        print(f"  Complexity analysis:    "
              f"{self.safe_format(analyzer_timing.get('complexity', 0))} seconds")
        print(f"  ChurnKPI (per file):    "
              f"{self.safe_format(analyzer_timing.get('filechurn', 0))} seconds")
        print(f"  HotspotKPI:             "
              f"{self.safe_format(analyzer_timing.get('hotspot', 0))} seconds")
        print(f"  CodeOwnershipKPI:       "
              f"{self.safe_format(analyzer_timing.get('ownership', 0))} seconds")
        print(f"  SharedOwnershipKPI:     "
              f"{self.safe_format(analyzer_timing.get('sharedownership', 0))} seconds")

    def print_summary(self, analyzer_timing: Optional[Dict] = None):
        """
        Print complete timing summary.

        Args:
            analyzer_timing: Optional timing data from analyzer
        """
        print("\n=== TIME SUMMARY ===")
        print(f"Scanning:           {self.get_scan_duration():.2f} seconds")
        print(f"Analysis:           {self.get_analysis_duration():.2f} seconds")
        print(f"Report generation:  {self.get_report_generation_duration():.2f} seconds")

        self.print_analysis_breakdown(analyzer_timing)
