import unittest
from src.languages.parsers.ada import AdaComplexityParser

class TestAdaComplexityParser(unittest.TestCase):
    def test_compute_complexity(self):
        code = "if A > B then null; end if;"
        parser = AdaComplexityParser()
        self.assertEqual(parser.compute_complexity(code), 2)
