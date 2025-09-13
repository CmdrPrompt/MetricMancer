import re
from abc import ABC, abstractmethod

class ComplexityParser(ABC):
	"""
	Abstract base class for complexity parsers for different programming languages.
	Subclasses must implement compute_complexity().
	"""
	@abstractmethod
	def compute_complexity(self, code: str) -> int:
		"""
		Compute the cyclomatic complexity of the given code string.
		Must be implemented by subclasses.
		"""
		pass
	def count_functions(self, code: str) -> int:
		"""
		Count the number of functions in the given code string using the FUNCTION_PATTERN.
		"""
		pattern = getattr(self, 'FUNCTION_PATTERN', None)
		if pattern:
			return len(re.findall(pattern, code))
		return 0
