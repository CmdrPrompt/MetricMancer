"""
Cognitive Complexity Calculator Factory.

Creates language-specific cognitive complexity calculators based on file extension.
Implements the Factory Pattern for multi-language support.
"""

from pathlib import Path
from typing import Optional
from .calculator_base import CognitiveComplexityCalculatorBase
from .calculator_python import PythonCognitiveComplexityCalculator
from .calculator_java import JavaCognitiveComplexityCalculator
from .calculator_go import GoCognitiveComplexityCalculator


class CognitiveComplexityCalculatorFactory:
    """
    Factory for creating language-specific cognitive complexity calculators.

    Uses file extension to determine which calculator to instantiate.
    """

    # Map file extensions to calculator classes
    # Will be expanded as new language calculators are implemented
    CALCULATORS = {
        '.py': PythonCognitiveComplexityCalculator,
        '.java': JavaCognitiveComplexityCalculator,
        '.go': GoCognitiveComplexityCalculator,
        # Future additions:
        # '.adb': AdaCognitiveComplexityCalculator,  # Requires custom tree-sitter build
        # '.ads': AdaCognitiveComplexityCalculator,  # Requires custom tree-sitter build
        # '.js': JavaScriptCognitiveComplexityCalculator,
        # '.jsx': JavaScriptCognitiveComplexityCalculator,
        # '.ts': TypeScriptCognitiveComplexityCalculator,
        # '.tsx': TypeScriptCognitiveComplexityCalculator,
        # ... etc
    }

    @classmethod
    def create(cls, file_path: str) -> Optional[CognitiveComplexityCalculatorBase]:
        """
        Create calculator for given file path.

        Args:
            file_path: Path to source file (absolute or relative)

        Returns:
            Calculator instance or None if language not supported

        Examples:
            >>> factory = CognitiveComplexityCalculatorFactory()
            >>> calc = factory.create('example.py')
            >>> isinstance(calc, PythonCognitiveComplexityCalculator)
            True
            >>> factory.create('unsupported.xyz')
            None
        """
        # Get file extension (lowercase for case-insensitive matching)
        ext = Path(file_path).suffix.lower()

        # Get calculator class for this extension
        calculator_class = cls.CALCULATORS.get(ext)

        if calculator_class:
            return calculator_class()

        return None

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        Check if file extension is supported.

        Args:
            file_path: Path to source file

        Returns:
            True if extension is supported, False otherwise

        Examples:
            >>> CognitiveComplexityCalculatorFactory.is_supported('test.py')
            True
            >>> CognitiveComplexityCalculatorFactory.is_supported('test.xyz')
            False
        """
        ext = Path(file_path).suffix.lower()
        return ext in cls.CALCULATORS

    @classmethod
    def get_supported_extensions(cls) -> list:
        """
        Get list of all supported file extensions.

        Returns:
            Sorted list of file extensions (e.g., ['.py', '.java', '.go'])

        Examples:
            >>> extensions = CognitiveComplexityCalculatorFactory.get_supported_extensions()
            >>> '.py' in extensions
            True
        """
        return sorted(cls.CALCULATORS.keys())
