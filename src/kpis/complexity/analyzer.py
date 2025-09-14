from typing import List, Dict, Any
import importlib

class ComplexityAnalyzer:
    """
    A class dedicated to calculating complexity for file content.
    """
    def calculate_for_file(self, file_content: str, config: dict) -> tuple[int, int]:
        """
        Calculates cyclomatic complexity and number of functions for a given file content.

        Args:
            file_content: A string with the source code to be analyzed.
            config: A dictionary with language configuration, including parser.

        Returns:
            A tuple with (complexity, function_count).
        """
        complexity = 0
        function_count = 0

        if 'parser' in config:
            try:
                parser_class_name = config['parser']
                module_name = parser_class_name.replace('ComplexityParser', '').lower()
                parser_module = f"src.languages.parsers.{module_name}"
                imported_module = importlib.import_module(parser_module)
                parser_class = getattr(imported_module, parser_class_name)
                parser = parser_class()
                complexity = parser.compute_complexity(file_content)
                function_count = getattr(parser, 'count_functions', lambda code: 0)(file_content)
            except (ImportError, AttributeError) as e:
                print(f"[WARN] Could not load parser for config: {config.get('name')}. Error: {e}")

        return complexity, function_count

    def analyze_functions(self, file_content: str, config: dict) -> List[Dict[str, Any]]:
        """
        Analyzes file content and returns a list of functions with their complexity.

        Args:
            file_content: A string with the source code to be analyzed.
            config: A dictionary with language configuration, including parser.

        Returns:
            A list of dictionaries, where each dictionary represents a function.
            Example: [{'name': 'my_func', 'complexity': 5}]
        """
        functions = []
        if 'parser' in config:
            try:
                parser_class_name = config['parser']
                module_name = parser_class_name.replace('ComplexityParser', '').lower()
                parser_module = f"src.languages.parsers.{module_name}"
                imported_module = importlib.import_module(parser_module)
                parser_class = getattr(imported_module, parser_class_name)
                parser = parser_class()
                functions = getattr(parser, 'analyze_functions', lambda code: [])(file_content)
            except (ImportError, AttributeError) as e:
                print(f"[WARN] Could not load parser for function analysis: {config.get('name')}. Error: {e}")

        return functions