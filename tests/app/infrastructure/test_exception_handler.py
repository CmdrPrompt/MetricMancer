"""
Unit tests for ExceptionHandler (TDD for Refactoring #2).

These tests verify that exception handling can be centralized and reused
across the application, reducing code duplication.

RED-GREEN-REFACTOR:
1. RED: These tests will FAIL initially because ExceptionHandler doesn't exist yet
2. GREEN: Create ExceptionHandler with standardized error handling
3. REFACTOR: Clean up existing exception handling to use new handler
"""

import unittest
from unittest.mock import patch
import io


class TestExceptionHandlerBasics(unittest.TestCase):
    """Test basic exception handling functionality."""

    def test_exception_handler_class_exists(self):
        """Test that ExceptionHandler class can be imported."""
        # This test will FAIL initially - that's expected in TDD!
        from src.app.infrastructure.exception_handler import ExceptionHandler
        self.assertIsNotNone(ExceptionHandler)

    def test_handle_git_operation_method_exists(self):
        """Test that handle_git_operation method exists."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        self.assertTrue(hasattr(ExceptionHandler, 'handle_git_operation'))
        self.assertTrue(callable(ExceptionHandler.handle_git_operation))

    def test_handle_report_generation_method_exists(self):
        """Test that handle_report_generation method exists."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        self.assertTrue(hasattr(ExceptionHandler, 'handle_report_generation'))
        self.assertTrue(callable(ExceptionHandler.handle_report_generation))


class TestGitOperationHandling(unittest.TestCase):
    """Test exception handling for git operations."""

    def test_successful_git_operation_returns_result(self):
        """Test that successful git operation returns the result."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def mock_operation():
            return ['file1.py', 'file2.py']

        result = ExceptionHandler.handle_git_operation(
            'test operation',
            mock_operation
        )

        self.assertEqual(result, ['file1.py', 'file2.py'])

    def test_failed_git_operation_returns_none(self):
        """Test that failed git operation returns None."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_operation():
            raise RuntimeError("Git command failed")

        result = ExceptionHandler.handle_git_operation(
            'test operation',
            failing_operation
        )

        self.assertIsNone(result)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_failed_git_operation_prints_warning(self, mock_stdout):
        """Test that failed git operation prints user-friendly warning."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_operation():
            raise RuntimeError("Git command failed")

        ExceptionHandler.handle_git_operation(
            'fetch changed files',
            failing_operation
        )

        output = mock_stdout.getvalue()
        self.assertIn('⚠️', output)
        self.assertIn('fetch changed files', output.lower())

    def test_git_operation_with_args(self):
        """Test that git operation can accept arguments."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def operation_with_args(repo_path, branch):
            return f"Files in {repo_path} on {branch}"

        result = ExceptionHandler.handle_git_operation(
            'test operation',
            operation_with_args,
            '/repo/path',
            'main'
        )

        self.assertEqual(result, "Files in /repo/path on main")

    def test_git_operation_with_kwargs(self):
        """Test that git operation can accept keyword arguments."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def operation_with_kwargs(repo_path=None, branch='main'):
            return f"{repo_path}:{branch}"

        result = ExceptionHandler.handle_git_operation(
            'test operation',
            operation_with_kwargs,
            repo_path='/repo',
            branch='develop'
        )

        self.assertEqual(result, "/repo:develop")


class TestReportGenerationHandling(unittest.TestCase):
    """Test exception handling for report generation."""

    def test_successful_report_generation_returns_result(self):
        """Test that successful report generation returns the result."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def mock_generator():
            return "Report generated successfully"

        result = ExceptionHandler.handle_report_generation(
            'test report',
            mock_generator
        )

        self.assertEqual(result, "Report generated successfully")

    def test_failed_report_generation_returns_none(self):
        """Test that failed report generation returns None."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_generator():
            raise ValueError("Invalid report data")

        result = ExceptionHandler.handle_report_generation(
            'test report',
            failing_generator
        )

        self.assertIsNone(result)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_failed_report_shows_error_message(self, mock_stdout):
        """Test that failed report generation shows error message."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_generator():
            raise ValueError("Invalid report data")

        ExceptionHandler.handle_report_generation(
            'hotspot analysis',
            failing_generator
        )

        output = mock_stdout.getvalue()
        self.assertIn('❌', output)
        self.assertIn('hotspot analysis', output.lower())

    @patch('traceback.print_exc')
    def test_report_generation_prints_traceback(self, mock_traceback):
        """Test that report generation failure prints full traceback."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_generator():
            raise ValueError("Invalid report data")

        ExceptionHandler.handle_report_generation(
            'test report',
            failing_generator
        )

        # Should have printed traceback for debugging
        mock_traceback.assert_called_once()


class TestExceptionTypes(unittest.TestCase):
    """Test handling of different exception types."""

    def test_handles_runtime_error(self):
        """Test that RuntimeError is handled correctly."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_op():
            raise RuntimeError("Runtime error")

        result = ExceptionHandler.handle_git_operation('test', failing_op)
        self.assertIsNone(result)

    def test_handles_io_error(self):
        """Test that IOError is handled correctly."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_op():
            raise IOError("File not found")

        result = ExceptionHandler.handle_git_operation('test', failing_op)
        self.assertIsNone(result)

    def test_handles_value_error(self):
        """Test that ValueError is handled correctly."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_op():
            raise ValueError("Invalid value")

        result = ExceptionHandler.handle_report_generation('test', failing_op)
        self.assertIsNone(result)

    def test_handles_generic_exception(self):
        """Test that generic Exception is handled correctly."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_op():
            raise Exception("Generic error")

        result = ExceptionHandler.handle_git_operation('test', failing_op)
        self.assertIsNone(result)


class TestDebugOutput(unittest.TestCase):
    """Test debug output for exception handling."""

    @patch('src.app.infrastructure.exception_handler.debug_print')
    def test_debug_output_on_git_failure(self, mock_debug):
        """Test that debug information is logged on git failure."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_op():
            raise RuntimeError("Git failed")

        ExceptionHandler.handle_git_operation('test', failing_op)

        # Should have called debug_print with error details
        mock_debug.assert_called()
        call_args = str(mock_debug.call_args)
        self.assertIn('test', call_args.lower())

    @patch('src.app.infrastructure.exception_handler.debug_print')
    def test_debug_output_on_report_failure(self, mock_debug):
        """Test that debug information is logged on report failure."""
        from src.app.infrastructure.exception_handler import ExceptionHandler

        def failing_op():
            raise ValueError("Report failed")

        ExceptionHandler.handle_report_generation('test', failing_op)

        # Should have called debug_print with error details
        mock_debug.assert_called()


if __name__ == '__main__':
    unittest.main()
