"""
Unit tests for FileChangeDetector (TDD for Refactoring #5).

These tests verify that file change detection can be extracted into a dedicated
service class, improving separation of concerns and testability.

RED-GREEN-REFACTOR:
1. RED: These tests will FAIL initially because FileChangeDetector doesn't exist yet
2. GREEN: Create FileChangeDetector with git change detection logic
3. REFACTOR: Update metric_mancer_app to use FileChangeDetector
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


class TestFileChangeDetectorBasics(unittest.TestCase):
    """Test basic FileChangeDetector functionality."""

    def test_file_change_detector_class_exists(self):
        """Test that FileChangeDetector class can be imported."""
        # This test will FAIL initially - that's expected in TDD!
        from src.app.services.file_change_detector import FileChangeDetector
        self.assertIsNotNone(FileChangeDetector)

    def test_file_change_detector_initialization(self):
        """Test that FileChangeDetector can be initialized with repo path."""
        from src.app.services.file_change_detector import FileChangeDetector

        detector = FileChangeDetector(repo_path='/path/to/repo')

        self.assertIsNotNone(detector)
        self.assertEqual(detector.repo_path, '/path/to/repo')

    def test_get_changed_files_method_exists(self):
        """Test that get_changed_files method exists."""
        from src.app.services.file_change_detector import FileChangeDetector

        detector = FileChangeDetector(repo_path='/path/to/repo')
        self.assertTrue(hasattr(detector, 'get_changed_files'))
        self.assertTrue(callable(detector.get_changed_files))


class TestGetChangedFiles(unittest.TestCase):
    """Test changed file detection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch('src.app.services.file_change_detector.get_current_branch')
    @patch('src.app.services.file_change_detector.get_changed_files_in_branch')
    def test_returns_current_branch_and_changed_files(self, mock_get_changed, mock_get_branch):
        """Test that get_changed_files returns tuple of (current_branch, changed_files)."""
        from src.app.services.file_change_detector import FileChangeDetector

        mock_get_branch.return_value = 'feature/test-branch'
        mock_get_changed.return_value = ['file1.py', 'file2.py']

        detector = FileChangeDetector(repo_path=self.temp_dir)
        result = detector.get_changed_files(base_branch='main')

        self.assertEqual(result, ('feature/test-branch', ['file1.py', 'file2.py']))

    @patch('src.app.services.file_change_detector.get_current_branch')
    def test_calls_get_current_branch_with_repo_path(self, mock_get_branch):
        """Test that get_current_branch is called with correct repo path."""
        from src.app.services.file_change_detector import FileChangeDetector

        mock_get_branch.return_value = 'feature/test'

        detector = FileChangeDetector(repo_path='/my/repo')
        detector.get_changed_files(base_branch='main')

        mock_get_branch.assert_called_once_with('/my/repo')

    @patch('src.app.services.file_change_detector.get_current_branch')
    @patch('src.app.services.file_change_detector.get_changed_files_in_branch')
    def test_calls_get_changed_files_with_correct_params(self, mock_get_changed, mock_get_branch):
        """Test that get_changed_files_in_branch is called with correct parameters."""
        from src.app.services.file_change_detector import FileChangeDetector

        mock_get_branch.return_value = 'feature/test'
        mock_get_changed.return_value = []

        detector = FileChangeDetector(repo_path='/my/repo')
        detector.get_changed_files(base_branch='develop')

        mock_get_changed.assert_called_once_with(
            repo_path='/my/repo',
            base_branch='develop'
        )

    @patch('src.app.services.file_change_detector.get_current_branch')
    @patch('src.app.services.file_change_detector.get_changed_files_in_branch')
    def test_uses_main_as_default_base_branch(self, mock_get_changed, mock_get_branch):
        """Test that 'main' is used as default base branch."""
        from src.app.services.file_change_detector import FileChangeDetector

        mock_get_branch.return_value = 'feature/test'
        mock_get_changed.return_value = []

        detector = FileChangeDetector(repo_path='/my/repo')
        detector.get_changed_files()  # No base_branch specified

        mock_get_changed.assert_called_once_with(
            repo_path='/my/repo',
            base_branch='main'
        )


class TestExceptionHandling(unittest.TestCase):
    """Test exception handling in FileChangeDetector."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch('src.app.services.file_change_detector.get_current_branch')
    def test_returns_none_tuple_when_get_current_branch_fails(self, mock_get_branch):
        """Test that (None, None) is returned when get_current_branch fails."""
        from src.app.services.file_change_detector import FileChangeDetector

        mock_get_branch.side_effect = RuntimeError("Git command failed")

        detector = FileChangeDetector(repo_path=self.temp_dir)
        result = detector.get_changed_files(base_branch='main')

        self.assertEqual(result, (None, None))

    @patch('src.app.services.file_change_detector.get_current_branch')
    @patch('src.app.services.file_change_detector.get_changed_files_in_branch')
    def test_returns_none_tuple_when_get_changed_files_fails(self, mock_get_changed, mock_get_branch):
        """Test that (None, None) is returned when get_changed_files_in_branch fails."""
        from src.app.services.file_change_detector import FileChangeDetector

        mock_get_branch.return_value = 'feature/test'
        mock_get_changed.side_effect = RuntimeError("Git diff failed")

        detector = FileChangeDetector(repo_path=self.temp_dir)
        result = detector.get_changed_files(base_branch='main')

        self.assertEqual(result, (None, None))

    @patch('sys.stdout', new_callable=MagicMock)
    @patch('src.app.services.file_change_detector.get_current_branch')
    def test_prints_warning_message_on_failure(self, mock_get_branch, mock_stdout):
        """Test that a warning message is printed on failure."""
        from src.app.services.file_change_detector import FileChangeDetector

        mock_get_branch.side_effect = RuntimeError("Git command failed")

        detector = FileChangeDetector(repo_path=self.temp_dir)
        detector.get_changed_files(base_branch='main')

        # Should have printed a warning message
        # (exact assertion depends on implementation)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases in FileChangeDetector."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch('src.app.services.file_change_detector.get_current_branch')
    @patch('src.app.services.file_change_detector.get_changed_files_in_branch')
    def test_handles_empty_changed_files_list(self, mock_get_changed, mock_get_branch):
        """Test that empty list of changed files is handled correctly."""
        from src.app.services.file_change_detector import FileChangeDetector

        mock_get_branch.return_value = 'feature/test'
        mock_get_changed.return_value = []

        detector = FileChangeDetector(repo_path=self.temp_dir)
        result = detector.get_changed_files(base_branch='main')

        self.assertEqual(result, ('feature/test', []))

    @patch('src.app.services.file_change_detector.get_current_branch')
    @patch('src.app.services.file_change_detector.get_changed_files_in_branch')
    def test_handles_many_changed_files(self, mock_get_changed, mock_get_branch):
        """Test that large list of changed files is handled correctly."""
        from src.app.services.file_change_detector import FileChangeDetector

        mock_get_branch.return_value = 'feature/test'
        changed_files = [f'file{i}.py' for i in range(100)]
        mock_get_changed.return_value = changed_files

        detector = FileChangeDetector(repo_path=self.temp_dir)
        result = detector.get_changed_files(base_branch='main')

        self.assertEqual(result, ('feature/test', changed_files))


class TestIntegrationWithExceptionHandler(unittest.TestCase):
    """Test integration with ExceptionHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch('src.app.services.file_change_detector.ExceptionHandler')
    @patch('src.app.services.file_change_detector.get_current_branch')
    @patch('src.app.services.file_change_detector.get_changed_files_in_branch')
    def test_uses_exception_handler_for_git_operations(self, mock_get_changed, mock_get_branch, mock_handler):
        """Test that ExceptionHandler is used to wrap git operations."""
        from src.app.services.file_change_detector import FileChangeDetector

        # Mock ExceptionHandler to return successful result
        mock_handler.handle_git_operation.return_value = ('feature/test', ['file1.py'])

        detector = FileChangeDetector(repo_path=self.temp_dir)
        result = detector.get_changed_files(base_branch='main')

        # Should have called ExceptionHandler
        mock_handler.handle_git_operation.assert_called()


if __name__ == '__main__':
    unittest.main()
