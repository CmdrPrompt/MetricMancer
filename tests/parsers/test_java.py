import unittest
from src.languages.parsers.java import JavaComplexityParser

class TestJavaComplexityParser(unittest.TestCase):
    def test_compute_complexity(self):
        code = "public void foo() { if (x) return; }"
        parser = JavaComplexityParser()
        self.assertEqual(parser.compute_complexity(code), 3)

    def test_count_functions(self):
        code = "public void foo() {} private int bar() {}"
        parser = JavaComplexityParser()
        self.assertEqual(parser.count_functions(code), 2)
