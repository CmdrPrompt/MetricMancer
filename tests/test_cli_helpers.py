# tests/test_cli_helpers.py

import unittest
from unittest.mock import patch
from io import StringIO
from src.utilities.cli_helpers import print_usage, parse_args

class TestCLIHelpers(unittest.TestCase):
    
    def test_parse_args(self):
        args = parse_args().parse_args(['src', 'test', '--threshold-low', '15', '--threshold-high', '30'])
        self.assertEqual(args.directories, ['src', 'test'])
        self.assertEqual(args.threshold_low, 15.0)
        self.assertEqual(args.threshold_high, 30.0)
        self.assertIsNone(args.problem_file_threshold)
        self.assertFalse(args.auto_report_filename)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_usage(self, mock_stdout):
        print_usage()
        output = mock_stdout.getvalue()
        self.assertIn("USAGE:", output)
        self.assertIn("PARAMETERS:", output)
        self.assertIn("EXAMPLE:", output)

if __name__ == '__main__':
    unittest.main()
