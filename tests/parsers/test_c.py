import unittest
from src.parsers.c import CComplexityParser

class TestCComplexityParser(unittest.TestCase):
    def test_compute_complexity(self):
        code = "int main() { if (x) return 0; }"
        parser = CComplexityParser()
        self.assertEqual(parser.compute_complexity(code), 3)

    def test_count_functions(self):
        code = "int main() {} void foo() {}"
        parser = CComplexityParser()
        self.assertEqual(parser.count_functions(code), 2)
