"""
Path helper utilities for handling output file paths.

This module provides utilities to normalize output paths and prevent
path duplication issues (e.g., output/output/file.md).
"""

import os


def normalize_output_path(report_folder, filename):
    """
    Normalize output path to prevent duplication of report_folder.

    This function intelligently combines report_folder and filename,
    avoiding duplication when filename already contains the report_folder prefix.

    Args:
        report_folder: The base folder for reports (e.g., 'output')
        filename: The filename or relative path (e.g., 'report.md' or 'output/report.md')

    Returns:
        Normalized path that doesn't duplicate report_folder

    Examples:
        >>> normalize_output_path('output', 'review.md')
        'output/review.md'

        >>> normalize_output_path('output', 'output/review.md')
        'output/review.md'  # No duplication!

        >>> normalize_output_path('output', './output/review.md')
        'output/review.md'  # Cleaned up

        >>> normalize_output_path('custom', 'subfolder/file.md')
        'custom/subfolder/file.md'
    """
    # Handle empty report_folder
    if not report_folder:
        return filename

    # Normalize paths (remove './', etc.)
    report_folder = os.path.normpath(report_folder)
    filename = os.path.normpath(filename)

    # Check if filename already starts with report_folder
    # This handles cases like:
    # - report_folder='output', filename='output/review.md'
    # - report_folder='output', filename='./output/review.md'
    if filename.startswith(report_folder + os.sep):
        # Filename already contains the report_folder, just return it
        return filename

    # Check for absolute paths - if filename is absolute, use it as-is
    if os.path.isabs(filename):
        return filename

    # Normal case: join report_folder and filename
    return os.path.join(report_folder, filename)
