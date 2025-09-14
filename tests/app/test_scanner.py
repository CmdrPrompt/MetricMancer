import os
import unittest
from pathlib import Path
from unittest.mock import patch

from src.app.scanner import Scanner
from src.languages.config import Config

class TestScanner(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory structure for testing."""
        self.test_dir = Path("test_scanner_temp_dir")
        self.test_dir.mkdir(exist_ok=True)

        # Create a mock config. We'll use the real LANGUAGES for this test.
        self.config = Config()

        # Create test files and directories
        (self.test_dir / "project_a").mkdir()
        (self.test_dir / "project_a" / "main.py").touch()
        (self.test_dir / "project_a" / "utils.js").touch()
        (self.test_dir / "project_a" / "README.md").touch() # Unsupported

        (self.test_dir / "project_a" / "src").mkdir()
        (self.test_dir / "project_a" / "src" / "component.ts").touch()

        # Hidden files and directories
        (self.test_dir / "project_a" / ".env").touch()
        (self.test_dir / "project_a" / ".vscode").mkdir()
        (self.test_dir / "project_a" / ".vscode" / "settings.json").touch()

        # Nested hidden directory
        (self.test_dir / "project_a" / "dist").mkdir()
        (self.test_dir / "project_a" / "dist" / ".generated").mkdir()
        (self.test_dir / "project_a" / "dist" / ".generated" / "bundle.js").touch()

        # Another project
        (self.test_dir / "project_b").mkdir()
        (self.test_dir / "project_b" / "app.java").touch()

        # A hidden project root
        (self.test_dir / ".hidden_project").mkdir()
        (self.test_dir / ".hidden_project" / "secret.py").touch()

        self.scanner = Scanner(self.config.languages)

    def tearDown(self):
        """Clean up the temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    @patch('src.utilities.debug.debug_print')
    def test_scan_finds_supported_files(self, mock_debug_print):
        """Test that scan finds all supported files in a directory."""
        import os
        scan_path = str(self.test_dir / "project_a")
        files = self.scanner.scan([scan_path])

        self.assertEqual(len(files), 3)

        abs_scan_path = os.path.abspath(scan_path)
        def norm(p):
            return os.path.normcase(p)
        found_paths = sorted([norm(f['path']) for f in files])

        expected_paths = sorted([
            norm(os.path.abspath(os.path.join(scan_path, "main.py"))),
            norm(os.path.abspath(os.path.join(scan_path, "utils.js"))),
            norm(os.path.abspath(os.path.join(scan_path, "src", "component.ts"))),
        ])

        self.assertEqual(found_paths, expected_paths)
        for f in files:
            self.assertEqual(norm(f['root']), norm(abs_scan_path))

    @patch('src.utilities.debug.debug_print')
    def test_scan_multiple_directories(self, mock_debug_print):
        """Test scanning multiple directories at once."""
        path_a = str(self.test_dir / "project_a")
        path_b = str(self.test_dir / "project_b")
        files = self.scanner.scan([path_a, path_b])

        self.assertEqual(len(files), 4)

        import os
        def norm(p):
            return os.path.normcase(p)
        found_paths = sorted([norm(f['path']) for f in files])
        expected_paths = sorted([
            norm(os.path.abspath(os.path.join(path_a, "main.py"))),
            norm(os.path.abspath(os.path.join(path_a, "utils.js"))),
            norm(os.path.abspath(os.path.join(path_a, "src", "component.ts"))),
            norm(os.path.abspath(os.path.join(path_b, "app.java"))),
        ])
        self.assertEqual(found_paths, expected_paths)

    @patch('src.utilities.debug.debug_print')
    def test_scan_ignores_hidden_files_and_dirs(self, mock_debug_print):
        """Test that hidden files and directories are ignored."""
        scan_path = str(self.test_dir / "project_a")
        files = self.scanner.scan([scan_path])

        found_paths = [f['path'] for f in files]
        self.assertNotIn(os.path.abspath(os.path.join(scan_path, ".env")), found_paths)
        self.assertNotIn(os.path.abspath(os.path.join(scan_path, ".vscode", "settings.json")), found_paths)
        self.assertNotIn(os.path.abspath(os.path.join(scan_path, "dist", ".generated", "bundle.js")), found_paths)

    @patch('src.utilities.debug.debug_print')
    def test_scan_ignores_hidden_root_directory(self, mock_debug_print):
        """Test that a hidden root directory is skipped entirely."""
        scan_path = str(self.test_dir / ".hidden_project")
        files = self.scanner.scan([scan_path])
        self.assertEqual(len(files), 0)

    @patch('src.utilities.debug.debug_print')
    def test_scan_handles_non_existent_directory(self, mock_debug_print):
        """Test that a non-existent directory is handled gracefully."""
        scan_path = str(self.test_dir / "non_existent_dir")
        files = self.scanner.scan([scan_path])
        self.assertEqual(len(files), 0)
        # Check that a warning was printed, normalizing paths for cross-platform compatibility
        expected_msg = f"[WARN] Folder '{os.path.abspath(scan_path)}' doesn't exist – skipping."
        # Normalize for case and slashes
        def norm(s):
            import re, os
            # Extract the path from the message
            m = re.match(r"\[WARN\] Folder '(.+)' doesn't exist – skipping.", s)
            if m:
                norm_path = os.path.normcase(os.path.abspath(m.group(1)))
                return f"[WARN] Folder '{norm_path}' doesn't exist – skipping."
            return s
        normalized_expected = norm(expected_msg)
        normalized_actuals = [norm(str(call.args[0])) for call in mock_debug_print.call_args_list]
        self.assertIn(normalized_expected, normalized_actuals)

    @patch('src.utilities.debug.debug_print')
    def test_scan_returns_empty_list_for_no_supported_files(self, mock_debug_print):
        """Test scanning a directory with no supported files returns an empty list."""
        (self.test_dir / "empty_proj").mkdir()
        (self.test_dir / "empty_proj" / "file.txt").touch()
        files = self.scanner.scan([str(self.test_dir / "empty_proj")])
        self.assertEqual(len(files), 0)

if __name__ == '__main__':
    unittest.main()