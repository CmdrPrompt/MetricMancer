"""
Unit tests for _deep_merge_scan_dirs refactoring (TDD for Refactoring #3).

These tests verify that the _deep_merge_scan_dirs method can be split into
smaller, more focused helper methods for improved readability and maintainability.

RED-GREEN-REFACTOR:
1. RED: These tests will FAIL initially because helper methods don't exist yet
2. GREEN: Create helper methods and refactor _deep_merge_scan_dirs
3. REFACTOR: Ensure behavior is preserved with cleaner code
"""

import unittest
from src.config.app_config import AppConfig
from src.app.metric_mancer_app import MetricMancerApp


class TestDeepMergeHelperMethods(unittest.TestCase):
    """Test that _deep_merge_scan_dirs is split into helper methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig(directories=['/test'])
        self.app = MetricMancerApp(config=self.config)

    def test_merge_files_helper_exists(self):
        """Test that _merge_files_at_level helper method exists."""
        # This test will FAIL initially - that's expected in TDD!
        self.assertTrue(hasattr(self.app, '_merge_files_at_level'))
        self.assertTrue(callable(self.app._merge_files_at_level))

    def test_merge_subdirs_helper_exists(self):
        """Test that _merge_subdirectories helper method exists."""
        self.assertTrue(hasattr(self.app, '_merge_subdirectories'))
        self.assertTrue(callable(self.app._merge_subdirectories))

    def test_merge_other_keys_helper_exists(self):
        """Test that _merge_other_keys helper method exists."""
        self.assertTrue(hasattr(self.app, '_merge_other_keys'))
        self.assertTrue(callable(self.app._merge_other_keys))


class TestMergeFilesAtLevel(unittest.TestCase):
    """Test _merge_files_at_level helper method."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig(directories=['/test'])
        self.app = MetricMancerApp(config=self.config)

    def test_merge_files_creates_files_dict_if_missing(self):
        """Test that files dict is created in target if it doesn't exist."""
        target = {}
        source = {'files': {'file1.py': {'name': 'file1.py'}}}

        self.app._merge_files_at_level(target, source)

        self.assertIn('files', target)
        self.assertIn('file1.py', target['files'])

    def test_merge_files_updates_existing_files(self):
        """Test that existing files dict is updated with new files."""
        target = {'files': {'file1.py': {'name': 'file1.py'}}}
        source = {'files': {'file2.py': {'name': 'file2.py'}}}

        self.app._merge_files_at_level(target, source)

        self.assertEqual(len(target['files']), 2)
        self.assertIn('file1.py', target['files'])
        self.assertIn('file2.py', target['files'])

    def test_merge_files_does_nothing_if_no_files_in_source(self):
        """Test that method handles source without 'files' key."""
        target = {'files': {'file1.py': {'name': 'file1.py'}}}
        source = {'other_key': 'value'}

        self.app._merge_files_at_level(target, source)

        # Target should be unchanged
        self.assertEqual(len(target['files']), 1)
        self.assertIn('file1.py', target['files'])


class TestMergeSubdirectories(unittest.TestCase):
    """Test _merge_subdirectories helper method."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig(directories=['/test'])
        self.app = MetricMancerApp(config=self.config)

    def test_merge_subdirs_creates_scan_dirs_if_missing(self):
        """Test that scan_dirs dict is created in target if it doesn't exist."""
        target = {}
        source = {'scan_dirs': {'subdir': {}}}

        self.app._merge_subdirectories(target, source)

        self.assertIn('scan_dirs', target)
        self.assertIn('subdir', target['scan_dirs'])

    def test_merge_subdirs_recursively_merges(self):
        """Test that subdirectories are merged recursively."""
        target = {'scan_dirs': {'subdir': {'files': {'file1.py': {}}}}}
        source = {'scan_dirs': {'subdir': {'files': {'file2.py': {}}}}}

        self.app._merge_subdirectories(target, source)

        # Should have merged both files in subdir
        self.assertEqual(len(target['scan_dirs']['subdir']['files']), 2)
        self.assertIn('file1.py', target['scan_dirs']['subdir']['files'])
        self.assertIn('file2.py', target['scan_dirs']['subdir']['files'])

    def test_merge_subdirs_handles_missing_source_scan_dirs(self):
        """Test that method handles source without 'scan_dirs' key."""
        target = {'scan_dirs': {'subdir': {}}}
        source = {'other_key': 'value'}

        self.app._merge_subdirectories(target, source)

        # Target should be unchanged
        self.assertIn('scan_dirs', target)
        self.assertIn('subdir', target['scan_dirs'])


class TestMergeOtherKeys(unittest.TestCase):
    """Test _merge_other_keys helper method."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig(directories=['/test'])
        self.app = MetricMancerApp(config=self.config)

    def test_merge_other_keys_copies_kpis(self):
        """Test that KPI data is copied from source to target."""
        target = {}
        source = {'kpis': {'complexity': 10}}

        self.app._merge_other_keys(target, source)

        self.assertIn('kpis', target)
        self.assertEqual(target['kpis'], {'complexity': 10})

    def test_merge_other_keys_skips_files_and_scan_dirs(self):
        """Test that 'files' and 'scan_dirs' are not copied."""
        target = {}
        source = {
            'files': {'file1.py': {}},
            'scan_dirs': {'subdir': {}},
            'kpis': {'complexity': 10}
        }

        self.app._merge_other_keys(target, source)

        self.assertNotIn('files', target)
        self.assertNotIn('scan_dirs', target)
        self.assertIn('kpis', target)

    def test_merge_other_keys_handles_multiple_keys(self):
        """Test that multiple non-special keys are copied."""
        target = {}
        source = {
            'kpis': {'complexity': 10},
            'metadata': {'author': 'test'},
            'stats': {'lines': 100}
        }

        self.app._merge_other_keys(target, source)

        self.assertIn('kpis', target)
        self.assertIn('metadata', target)
        self.assertIn('stats', target)


class TestDeepMergeRefactoredBehavior(unittest.TestCase):
    """Test that refactored _deep_merge_scan_dirs preserves original behavior."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig(directories=['/test'])
        self.app = MetricMancerApp(config=self.config)

    def test_deep_merge_uses_helper_methods(self):
        """Test that _deep_merge_scan_dirs calls helper methods."""
        target = {}
        source = {
            'dir1': {
                'files': {'file1.py': {}},
                'scan_dirs': {'subdir': {}},
                'kpis': {'complexity': 10}
            }
        }

        # Call the main method
        self.app._deep_merge_scan_dirs(target, source)

        # Should have merged all components
        self.assertIn('dir1', target)
        self.assertIn('files', target['dir1'])
        self.assertIn('scan_dirs', target['dir1'])
        self.assertIn('kpis', target['dir1'])

    def test_deep_merge_preserves_recursive_behavior(self):
        """Test that recursive merging still works after refactoring."""
        target = {
            'dir1': {
                'scan_dirs': {
                    'subdir': {
                        'files': {'file1.py': {}}
                    }
                }
            }
        }
        source = {
            'dir1': {
                'scan_dirs': {
                    'subdir': {
                        'files': {'file2.py': {}}
                    }
                }
            }
        }

        self.app._deep_merge_scan_dirs(target, source)

        # Should have deep-merged the nested files
        files = target['dir1']['scan_dirs']['subdir']['files']
        self.assertEqual(len(files), 2)
        self.assertIn('file1.py', files)
        self.assertIn('file2.py', files)

    def test_deep_merge_handles_simple_assignment(self):
        """Test that non-overlapping keys are still simply assigned."""
        target = {'dir1': {}}
        source = {'dir2': {'files': {'file1.py': {}}}}

        self.app._deep_merge_scan_dirs(target, source)

        # dir2 should be simply assigned since it's new
        self.assertIn('dir2', target)
        self.assertEqual(target['dir2'], source['dir2'])


class TestRefactoringCodeQuality(unittest.TestCase):
    """Test that refactoring improves code quality metrics."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig(directories=['/test'])
        self.app = MetricMancerApp(config=self.config)

    def test_helper_methods_are_small(self):
        """Test that helper methods are smaller than original (< 15 lines each)."""
        import inspect

        def count_code_lines(source):
            lines = source.split('\n')
            return len([line for line in lines if line.strip() and not line.strip().startswith('#')])

        # Check _merge_files_at_level
        source = inspect.getsource(self.app._merge_files_at_level)
        self.assertLess(count_code_lines(source), 15, "_merge_files_at_level should be < 15 lines")

        # Check _merge_subdirectories
        source = inspect.getsource(self.app._merge_subdirectories)
        self.assertLess(count_code_lines(source), 15, "_merge_subdirectories should be < 15 lines")

        # Check _merge_other_keys
        source = inspect.getsource(self.app._merge_other_keys)
        self.assertLess(count_code_lines(source), 15, "_merge_other_keys should be < 15 lines")

    def test_deep_merge_has_reduced_complexity(self):
        """Test that _deep_merge_scan_dirs has lower complexity after refactoring."""
        import inspect

        # After refactoring, _deep_merge_scan_dirs should delegate to helpers
        source = inspect.getsource(self.app._deep_merge_scan_dirs)

        # Should call helper methods
        self.assertIn('_merge_files_at_level', source)
        self.assertIn('_merge_subdirectories', source)
        self.assertIn('_merge_other_keys', source)


if __name__ == '__main__':
    unittest.main()
