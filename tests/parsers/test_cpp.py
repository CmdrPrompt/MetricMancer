import unittest
from src.parsers.cpp import CppComplexityParser

class TestCppComplexityParser(unittest.TestCase):
    def test_compute_complexity(self):
        code = "int main() { if (x) return 0; }"
        parser = CppComplexityParser()
        self.assertEqual(parser.compute_complexity(code), 3)

    def test_count_functions(self):
        code = "int main() {} void foo() {}"
        parser = CppComplexityParser()
        self.assertEqual(parser.count_functions(code), 2)
