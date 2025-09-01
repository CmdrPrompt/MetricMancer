# tests/test_cli_helpers.py

import unittest
import sys
from unittest.mock import patch
from io import StringIO
from src.utilities.cli_helpers import print_usage, parse_args, validate_and_parse_args

class TestCLIHelpers(unittest.TestCase):
    
    def test_parse_args(self):
        args = parse_args().parse_args(['src', 'test', '--threshold-low', '15', '--threshold-high', '30', '--cli-report'])
        self.assertEqual(args.directories, ['src', 'test'])
        self.assertEqual(args.threshold_low, 15.0)
        self.assertEqual(args.threshold_high, 30.0)
        self.assertIsNone(args.problem_file_threshold)
        self.assertFalse(args.auto_report_filename)
        self.assertTrue(args.cli_report)
        self.assertFalse(args.html_report)
        self.assertFalse(args.debug)
    
    def test_parse_args_html_report(self):
        args = parse_args().parse_args(['src', '--html-report'])
        self.assertEqual(args.directories, ['src'])
        self.assertFalse(args.cli_report)
        self.assertTrue(args.html_report)
        self.assertFalse(args.debug)
    
    def test_parse_args_debug_flag(self):
        args = parse_args().parse_args(['src', '--cli-report', '--debug'])
        self.assertTrue(args.cli_report)
        self.assertTrue(args.debug)
        
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_usage(self, mock_stdout):
        print_usage()
        output = mock_stdout.getvalue()
        self.assertIn("USAGE:", output)
        self.assertIn("PARAMETERS:", output)
        self.assertIn("EXAMPLE:", output)
        self.assertIn("--cli-report", output)
        self.assertIn("--html-report", output)
        self.assertIn("--debug", output)
        self.assertIn("You must specify exactly one", output)
    
    @patch('sys.argv', ['main.py', 'src', '--cli-report'])
    def test_validate_and_parse_args_cli_report(self):
        args = validate_and_parse_args()
        self.assertTrue(args.cli_report)
        self.assertFalse(args.html_report)
    
    @patch('sys.argv', ['main.py', 'src', '--html-report'])
    def test_validate_and_parse_args_html_report(self):
        args = validate_and_parse_args()
        self.assertFalse(args.cli_report)
        self.assertTrue(args.html_report)
    
    @patch('sys.argv', ['main.py', 'src', '--cli-report', '--html-report'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_and_parse_args_both_flags_error(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            validate_and_parse_args()
        self.assertEqual(cm.exception.code, 1)
        output = mock_stdout.getvalue()
        self.assertIn("You cannot specify both", output)
        self.assertIn("--cli-report and --html-report", output)
    
    @patch('sys.argv', ['main.py', 'src'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_validate_and_parse_args_no_flags_error(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            validate_and_parse_args()
        self.assertEqual(cm.exception.code, 1)
        output = mock_stdout.getvalue()
        self.assertIn("You must specify exactly one report type", output)
        self.assertIn("either --cli-report or --html-report", output)

if __name__ == '__main__':
    unittest.main()
