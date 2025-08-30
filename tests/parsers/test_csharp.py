import unittest
from src.parsers.csharp import CSharpComplexityParser

class TestCSharpComplexityParser(unittest.TestCase):
    def test_compute_complexity(self):
        code = "public void foo() { if (x) return; }"
        parser = CSharpComplexityParser()
        self.assertEqual(parser.compute_complexity(code), 3)

    def test_count_functions(self):
        code = "public void foo() {} private int bar() {}"
        parser = CSharpComplexityParser()
        self.assertEqual(parser.count_functions(code), 2)
