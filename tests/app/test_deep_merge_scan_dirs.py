"""Test deep merge functionality for scan_dirs."""
import unittest
from src.app.metric_mancer_app import MetricMancerApp
from src.config.app_config import AppConfig


class TestDeepMergeScanDirs(unittest.TestCase):
    """Test deep merge of scan_dirs when analyzing multiple directories."""

    def setUp(self):
        """Set up test app."""
        config = AppConfig(
            directories=['src/'],
            threshold_low=10,
            threshold_high=20
        )
        self.app = MetricMancerApp(config=config)

    def test_deep_merge_empty_target(self):
        """Test merging into empty target."""
        target = {}
        source = {
            'analysis': {
                'files': {'file1.py': {}},
                'scan_dirs': {}
            }
        }

        self.app._deep_merge_scan_dirs(target, source)

        self.assertIn('analysis', target)
        self.assertEqual(list(target['analysis']['files'].keys()), ['file1.py'])

    def test_deep_merge_non_overlapping_dirs(self):
        """Test merging non-overlapping directories."""
        target = {
            'app': {
                'files': {'app1.py': {}},
                'scan_dirs': {}
            }
        }
        source = {
            'analysis': {
                'files': {'file1.py': {}},
                'scan_dirs': {}
            }
        }

        self.app._deep_merge_scan_dirs(target, source)

        self.assertIn('app', target)
        self.assertIn('analysis', target)
        self.assertEqual(list(target['app']['files'].keys()), ['app1.py'])
        self.assertEqual(list(target['analysis']['files'].keys()), ['file1.py'])

    def test_deep_merge_overlapping_dirs(self):
        """Test merging overlapping directories (main use case)."""
        target = {
            'analysis': {
                'files': {'code_review_advisor.py': {'complexity': 50}},
                'scan_dirs': {}
            }
        }
        source = {
            'analysis': {
                'files': {'test_code_review_advisor.py': {'complexity': 20}},
                'scan_dirs': {}
            }
        }

        self.app._deep_merge_scan_dirs(target, source)

        self.assertIn('analysis', target)
        # Both files should be present after merge
        self.assertIn('code_review_advisor.py', target['analysis']['files'])
        self.assertIn('test_code_review_advisor.py', target['analysis']['files'])
        self.assertEqual(len(target['analysis']['files']), 2)

    def test_deep_merge_nested_scan_dirs(self):
        """Test merging nested scan_dirs."""
        target = {
            'analysis': {
                'files': {},
                'scan_dirs': {
                    'delta': {
                        'files': {'analyzer.py': {}},
                        'scan_dirs': {}
                    }
                }
            }
        }
        source = {
            'analysis': {
                'files': {},
                'scan_dirs': {
                    'delta': {
                        'files': {'test_analyzer.py': {}},
                        'scan_dirs': {}
                    }
                }
            }
        }

        self.app._deep_merge_scan_dirs(target, source)

        # Check nested structure is merged
        self.assertIn('delta', target['analysis']['scan_dirs'])
        delta_files = target['analysis']['scan_dirs']['delta']['files']
        self.assertIn('analyzer.py', delta_files)
        self.assertIn('test_analyzer.py', delta_files)
        self.assertEqual(len(delta_files), 2)


if __name__ == '__main__':
    unittest.main()
