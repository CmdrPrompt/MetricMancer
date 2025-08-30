import unittest
from src.parsers.python import PythonComplexityParser

class TestPythonComplexityParser(unittest.TestCase):
    def test_compute_complexity(self):
        code = "def foo():\n    if True:\n        return 1\n"
        parser = PythonComplexityParser()
        self.assertEqual(parser.compute_complexity(code), 3)

    def test_count_functions(self):
        code = "def foo(): pass\ndef bar(): pass\n"
        parser = PythonComplexityParser()
        self.assertEqual(parser.count_functions(code), 2)
