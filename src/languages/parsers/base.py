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

	def analyze_functions(self, code: str) -> list[dict[str, any]]:
		"""
		Finds function definitions and calculates complexity for each.
		This is a basic implementation and may not be perfectly accurate for
		all languages, especially with nested functions. It assumes function
		bodies can be roughly identified between function signatures.
		"""
		functions = []
		pattern = getattr(self, 'FUNCTION_PATTERN', None)
		if not pattern:
			return []

		matches = list(re.finditer(pattern, code))
		
		for i, match in enumerate(matches):
			if not match.groups():
				continue
			func_name = match.group(1)
			start_pos = match.start()
			end_pos = matches[i+1].start() if i + 1 < len(matches) else len(code)
			func_code = code[start_pos:end_pos]
			complexity = self.compute_complexity(func_code)
			functions.append({'name': func_name, 'complexity': complexity})
		return functions

	def count_functions(self, code: str) -> int:
		"""
		Count the number of functions in the given code string using the FUNCTION_PATTERN.
		"""
		pattern = getattr(self, 'FUNCTION_PATTERN', None)
		if pattern:
			return len(re.findall(pattern, code))
		return 0
