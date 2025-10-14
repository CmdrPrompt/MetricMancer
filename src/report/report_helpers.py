"""
Helper functions for report generation, including grading, file extensions,
and filename handling for ComplexityScanner.
"""

import os
import datetime


def grade(value: float, threshold_low: float, threshold_high: float) -> dict:
    """
    Return a grade label and color for a given value based on thresholds.
    Args:
        value: The value to grade (e.g., complexity score).
        threshold_low: Lower threshold for best grade.
        threshold_high: Upper threshold for medium grade.
    Returns:
        dict: Dictionary with 'label' (A/B/C) and 'color' (hex color code).
    """
    if value < threshold_low:
        return {"label": "A", "color": "#4CAF50"}  # Green
    elif value < threshold_high:
        return {"label": "B", "color": "#FFC107"}  # Amber
    else:
        return {"label": "C", "color": "#F44336"}  # Red


def get_file_extension(filename: str) -> str:
    """
    Get the file extension for a given filename.
    Args:
        filename: The name of the file.
    Returns:
        str: The file extension (without dot), or empty string if none.
    """
    return filename.split('.')[-1] if '.' in filename else ''


def get_language_from_extension(extension: str) -> str:
    """
    Get the programming language for a given file extension.
    Args:
        extension: The file extension (without dot).
    Returns:
        str: The programming language name, or 'Unknown' if not mapped.
    """
    mapping = {
        'py': 'Python',
        'js': 'JavaScript',
        'ts': 'TypeScript',
        'java': 'Java',
        'cpp': 'C++',
        'c': 'C',
        'cs': 'C#',
        'go': 'Go',
        'rb': 'Ruby',
        'php': 'PHP',
        'swift': 'Swift',
        'kt': 'Kotlin',
        'scala': 'Scala',
        'rs': 'Rust',
        'm': 'Objective-C',
        'ada': 'Ada',
    }
    return mapping.get(extension, 'Unknown')


def get_output_filename(args):
    """
    Determines the output filename for the report based on CLI arguments.
    Handles --report-filename, --with-date, --auto-report-filename.
    """
    # Set file type depending on report format
    ext = '.html'
    if getattr(args, 'output_format', None) == 'json':
        ext = '.json'
    output_file = f'complexity_report{ext}'

    if getattr(args, 'report_filename', None):
        output_file = args.report_filename
        if getattr(args, 'with_date', False):
            date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            base, ext = os.path.splitext(output_file)
            output_file = f"{base}_{date_str}{ext}"
    elif getattr(args, 'auto_report_filename', False):
        date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        dir_str = "_".join([
            os.path.basename(os.path.normpath(d))
            for d in getattr(args, 'directories', ['src'])
        ])
        output_file = f"complexity_report_{dir_str}_{date_str}.html"

    return output_file


def ensure_report_folder(report_folder):
    """
    Ensures the report folder exists. Returns the folder path if specified, 
    else returns the default 'output' folder.
    """
    if report_folder is None:
        report_folder = 'output'
    os.makedirs(report_folder, exist_ok=True)
    return report_folder
