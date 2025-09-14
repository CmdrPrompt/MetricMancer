import unittest
from unittest.mock import patch, MagicMock
from src.kpis.complexity.analyzer import ComplexityAnalyzer

class TestComplexityAnalyzerEdgeCases(unittest.TestCase):
    def setUp(self):
        self.analyzer = ComplexityAnalyzer()
        self.dummy_code = "def foo():\n    pass"
        self.config = {"parser": "DummyComplexityParser", "name": "dummy"}

    def test_calculate_for_file_empty_config(self):
        complexity, func_count = self.analyzer.calculate_for_file(self.dummy_code, {})
        self.assertEqual(complexity, 0)
        self.assertEqual(func_count, 0)

    @patch("importlib.import_module", side_effect=ImportError("fail"))
    def test_calculate_for_file_import_error(self, mock_import):
        complexity, func_count = self.analyzer.calculate_for_file(self.dummy_code, self.config)
        self.assertEqual(complexity, 0)
        self.assertEqual(func_count, 0)

    @patch("importlib.import_module")
    def test_calculate_for_file_missing_methods(self, mock_import):
        # Parser saknar compute_complexity och count_functions
        mock_parser = MagicMock()
        mock_class = MagicMock(return_value=mock_parser)
        mock_module = MagicMock()
        setattr(mock_module, "DummyComplexityParser", mock_class)
        mock_import.return_value = mock_module
        # compute_complexity saknas
        del mock_parser.compute_complexity
        complexity, func_count = self.analyzer.calculate_for_file(self.dummy_code, self.config)
        self.assertEqual(complexity, 0)
        self.assertEqual(func_count, 0)

    def test_analyze_functions_empty_config(self):
        result = self.analyzer.analyze_functions(self.dummy_code, {})
        self.assertEqual(result, [])

    @patch("importlib.import_module", side_effect=AttributeError("fail"))
    def test_analyze_functions_attribute_error(self, mock_import):
        result = self.analyzer.analyze_functions(self.dummy_code, self.config)
        self.assertEqual(result, [])

    @patch("importlib.import_module")
    def test_analyze_functions_missing_method(self, mock_import):
        # Parser saknar analyze_functions
        mock_parser = MagicMock()
        mock_class = MagicMock(return_value=mock_parser)
        mock_module = MagicMock()
        setattr(mock_module, "DummyComplexityParser", mock_class)
        mock_import.return_value = mock_module
        # analyze_functions saknas
        del mock_parser.analyze_functions
        result = self.analyzer.analyze_functions(self.dummy_code, self.config)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()
