import unittest
from unittest.mock import patch, MagicMock
from src.kpis.complexity.analyzer import ComplexityAnalyzer

class TestComplexityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ComplexityAnalyzer()
        self.dummy_code = "def foo():\n    pass"
        self.config = {"parser": "DummyComplexityParser", "name": "dummy"}

    @patch("importlib.import_module")
    def test_calculate_for_file_success(self, mock_import_module):
        # Mock parser class and its methods
        mock_parser = MagicMock()
        mock_parser.compute_complexity.return_value = 42
        mock_parser.count_functions.return_value = 3
        mock_class = MagicMock(return_value=mock_parser)
        mock_module = MagicMock()
        setattr(mock_module, "DummyComplexityParser", mock_class)
        mock_import_module.return_value = mock_module

        complexity, func_count = self.analyzer.calculate_for_file(self.dummy_code, self.config)
        self.assertEqual(complexity, 42)
        self.assertEqual(func_count, 3)
        mock_parser.compute_complexity.assert_called_once_with(self.dummy_code)
        mock_parser.count_functions.assert_called_once_with(self.dummy_code)

    @patch("importlib.import_module", side_effect=ImportError("fail"))
    def test_calculate_for_file_import_error(self, mock_import_module):
        complexity, func_count = self.analyzer.calculate_for_file(self.dummy_code, self.config)
        self.assertEqual(complexity, 0)
        self.assertEqual(func_count, 0)

    def test_calculate_for_file_no_parser(self):
        complexity, func_count = self.analyzer.calculate_for_file(self.dummy_code, {})
        self.assertEqual(complexity, 0)
        self.assertEqual(func_count, 0)

    @patch("importlib.import_module")
    def test_analyze_functions_success(self, mock_import_module):
        mock_parser = MagicMock()
        mock_parser.analyze_functions.return_value = [{"name": "foo", "complexity": 5}]
        mock_class = MagicMock(return_value=mock_parser)
        mock_module = MagicMock()
        setattr(mock_module, "DummyComplexityParser", mock_class)
        mock_import_module.return_value = mock_module

        result = self.analyzer.analyze_functions(self.dummy_code, self.config)
        self.assertEqual(result, [{"name": "foo", "complexity": 5}])
        mock_parser.analyze_functions.assert_called_once_with(self.dummy_code)

    @patch("importlib.import_module", side_effect=AttributeError("fail"))
    def test_analyze_functions_attribute_error(self, mock_import_module):
        result = self.analyzer.analyze_functions(self.dummy_code, self.config)
        self.assertEqual(result, [])

    def test_analyze_functions_no_parser(self):
        result = self.analyzer.analyze_functions(self.dummy_code, {})
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()
