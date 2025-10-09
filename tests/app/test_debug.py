import unittest
from src.utilities import debug
from unittest.mock import patch


class TestDebug(unittest.TestCase):
    def test_debug_print_when_debug_false(self):
        debug.DEBUG = False
        # Should not print anything
        with patch('builtins.print') as mock_print:
            debug.debug_print('hej')
            mock_print.assert_not_called()

    def test_debug_print_when_debug_true(self):
        debug.DEBUG = True
        with patch('builtins.print') as mock_print:
            debug.debug_print('hej')
            mock_print.assert_called_once_with('hej')
        debug.DEBUG = False  # Reset for other tests


if __name__ == "__main__":
    unittest.main()
