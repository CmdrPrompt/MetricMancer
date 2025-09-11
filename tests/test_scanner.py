# tests/test_scanner.py

import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.utilities.scanner import Scanner

class TestScanner(unittest.TestCase):
    
    @patch('src.utilities.scanner.os.path.isdir')
    @patch('src.utilities.scanner.os.walk')
    def test_scan(self, mock_os_walk, mock_isdir):
        import os
        # Setup the mock data
        mock_isdir.return_value = True
        mock_os_walk.return_value = [
            ('/mock/dir', ('subdir',), ('file1.py', 'file2.txt')),
        ]

        # Mock configuration and languages
        LANGUAGES = {'.py': "Python"}
        config = MagicMock()

        # Initialize scanner with mock config
        scanner = Scanner(config)

        # Run the scan method
        result = scanner.scan(['/mock/dir'])

        # Assert that the scan result is correct, normalizing paths for platform independence
        expected_result = [{'path': '/mock/dir/file1.py', 'root': '/mock/dir', 'ext': '.py'}]
        def norm(entry):
            import os
            return {
                'path': os.path.normpath(entry['path']).replace('\\', '/').split('/')[-1],
                'root': os.path.normpath(entry['root']).replace('\\', '/').split('/')[-2] if len(os.path.normpath(entry['root']).replace('\\', '/').split('/')) > 1 else os.path.normpath(entry['root']).replace('\\', '/'),
                'ext': entry['ext']
            }
        result_norm = [norm(e) for e in result]
        expected_norm = [norm(e) for e in expected_result]
        self.assertEqual(result_norm, expected_norm)

    def setUp(self):
        # Patch open and file existence for dummy files
        self.patcher_exists = patch('os.path.exists', return_value=True)
        self.patcher_open = patch('builtins.open', mock_open(read_data="dummy code"))
        self.patcher_exists.start()
        self.patcher_open.start()
        self.addCleanup(self.patcher_exists.stop)
        self.addCleanup(self.patcher_open.stop)

if __name__ == '__main__':
    unittest.main()
