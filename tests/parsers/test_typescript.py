import unittest
from src.parsers.typescript import TypeScriptComplexityParser

class TestTypeScriptComplexityParser(unittest.TestCase):
    def test_compute_complexity(self):
        code = "function foo() { if (x) return; }"
        parser = TypeScriptComplexityParser()
        self.assertEqual(parser.compute_complexity(code), 3)

    def test_count_functions(self):
        code = "function foo() {} function bar() {}"
        parser = TypeScriptComplexityParser()
        self.assertEqual(parser.count_functions(code), 2)
