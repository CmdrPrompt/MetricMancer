import unittest
from src.languages.parsers.go import GoComplexityParser

class TestGoComplexityParser(unittest.TestCase):
    def test_compute_complexity(self):
        code = "func foo() { if x > 0 { return } }"
        parser = GoComplexityParser()
        self.assertEqual(parser.compute_complexity(code), 3)

    def test_count_functions(self):
        code = "func foo() {} func bar() {}"
        parser = GoComplexityParser()
        self.assertEqual(parser.count_functions(code), 2)
