"""
Analysis package for MetricMancer.
Contains hotspot analysis and code review strategy tools.
"""

from src.analysis.hotspot_analyzer import (
    extract_hotspots_from_data,
    format_hotspots_table,
    save_hotspots_to_file,
    print_hotspots_summary
)

from src.analysis.code_review_advisor import (
    CodeReviewAdvisor,
    ReviewRecommendation,
    generate_review_report
)

__all__ = [
    # Hotspot analysis
    'extract_hotspots_from_data',
    'format_hotspots_table',
    'save_hotspots_to_file',
    'print_hotspots_summary',
    # Code review
    'CodeReviewAdvisor',
    'ReviewRecommendation',
    'generate_review_report',
]
