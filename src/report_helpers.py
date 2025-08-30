"""
Helper functions for report filename and folder handling for ComplexityScanner.
"""

import os
import datetime

def get_output_filename(args):
    """
    Determines the output filename for the report based on CLI arguments.
    Handles --report-filename, --with-date, --auto-report-filename.
    """
    output_file = 'complexity_report.html'
    if getattr(args, 'report_filename', None):
        output_file = args.report_filename
        if getattr(args, 'with_date', False):
            date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            base, ext = os.path.splitext(output_file)
            output_file = f"{base}_{date_str}{ext}"
    elif getattr(args, 'auto_report_filename', False):
        date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        dir_str = "_".join([os.path.basename(os.path.normpath(d)) for d in getattr(args, 'directories', ['src'])])
        output_file = f"complexity_report_{dir_str}_{date_str}.html"
    return output_file

def ensure_report_folder(report_folder):
    """
    Ensures the report folder exists. Returns the folder path if specified, else None.
    """
    if report_folder:
        os.makedirs(report_folder, exist_ok=True)
        return report_folder
    return None
