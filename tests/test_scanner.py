# tests/test_scanner.py

import unittest
from unittest.mock import patch, MagicMock
from src.utilities.scanner import Scanner

class TestScanner(unittest.TestCase):
    
    @patch('src.utilities.scanner.os.path.isdir')
    @patch('src.utilities.scanner.os.walk')
    def test_scan(self, mock_os_walk, mock_isdir):
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
        
        # Assert that the scan result is correct
        expected_result = [{'path': '/mock/dir/file1.py', 'root': '/mock/dir', 'ext': '.py'}]
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
