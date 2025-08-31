import unittest
from src.languages.parsers.base import ComplexityParser

class DummyParser(ComplexityParser):
    pass

class TestBaseParser(unittest.TestCase):
    def test_abstract_method(self):
        with self.assertRaises(TypeError):
            DummyParser()
