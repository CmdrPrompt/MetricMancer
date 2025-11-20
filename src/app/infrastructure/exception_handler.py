"""
Centralized exception handling for MetricMancer operations.

This module provides standardized exception handling to reduce code duplication
and ensure consistent error messages and logging across the application.
"""

import traceback
from src.utilities.debug import debug_print


class ExceptionHandler:
    """
    Centralized exception handler for MetricMancer operations.

    Provides static methods for handling different types of operations
    with consistent error reporting and logging.
    """

    @staticmethod
    def handle_git_operation(operation_name: str, func, *args, **kwargs):
        """
        Handle exceptions from git operations with consistent logging.

        Args:
            operation_name: Human-readable name of the operation (e.g., "fetch changed files")
            func: The function to execute
            *args: Positional arguments to pass to func
            **kwargs: Keyword arguments to pass to func

        Returns:
            The result of func if successful, None if an exception occurred

        Example:
            result = ExceptionHandler.handle_git_operation(
                "fetch changed files",
                get_changed_files,
                repo_path,
                base_branch="main"
            )
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"   ⚠️  {operation_name} failed: {e}")
            debug_print(f"[DEBUG] {operation_name} error: {e}")
            return None

    @staticmethod
    def handle_report_generation(operation_name: str, func, *args, **kwargs):
        """
        Handle exceptions from report generation with traceback.

        Args:
            operation_name: Human-readable name of the operation (e.g., "hotspot analysis")
            func: The function to execute
            *args: Positional arguments to pass to func
            **kwargs: Keyword arguments to pass to func

        Returns:
            The result of func if successful, None if an exception occurred

        Example:
            result = ExceptionHandler.handle_report_generation(
                "hotspot analysis",
                generate_hotspot_report,
                repo_data,
                threshold=50
            )
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"\n❌ Error in {operation_name}: {e}")
            debug_print(f"[DEBUG] Full traceback for {operation_name}: {e}")
            traceback.print_exc()
            return None
