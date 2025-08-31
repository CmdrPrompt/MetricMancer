import unittest
from src.languages.parsers.javascript import JavaScriptComplexityParser

class TestJavaScriptComplexityParser(unittest.TestCase):
    def test_compute_complexity(self):
        code = "function foo() { if (x) return; }"
        parser = JavaScriptComplexityParser()
        self.assertEqual(parser.compute_complexity(code), 3)

    def test_count_functions(self):
        code = "function foo() {} function bar() {}"
        parser = JavaScriptComplexityParser()
        self.assertEqual(parser.count_functions(code), 2)
