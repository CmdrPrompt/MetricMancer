"""
Abstract base class for cognitive complexity calculators.

Defines the interface that all language-specific calculators must implement.
This enables the Factory Pattern for multi-language support.
"""

from abc import ABC, abstractmethod
from typing import Dict


class CognitiveComplexityCalculatorBase(ABC):
    """
    Abstract base class for cognitive complexity calculators.

    Each language-specific calculator must implement this interface.

    Cognitive Complexity measures how difficult code is to understand,
    based on the SonarSource specification:
    https://www.sonarsource.com/docs/CognitiveComplexity.pdf

    Key principles:
    1. Basic control structures (if, for, while, except) add +1
    2. Nesting increases the penalty (+1 per nesting level)
    3. Boolean operator sequences count as +1 (not per operator)
    4. Recursion adds +1
    """

    @abstractmethod
    def calculate_for_file(self, file_content: str) -> Dict[str, int]:
        """
        Calculate cognitive complexity for all functions in a file.

        Args:
            file_content: Source code content as string

        Returns:
            Dict mapping function names to their complexity values
            Example: {'main': 5, 'helper': 3, 'process_data': 12}

        Raises:
            SyntaxError: If the code cannot be parsed
            Exception: For other parsing/calculation errors
        """
        pass

    @abstractmethod
    def get_language_name(self) -> str:
        """
        Get the name of the language this calculator supports.

        Returns:
            Language name (e.g., 'Python', 'JavaScript', 'Java', 'Ada', 'Go')
        """
        pass
