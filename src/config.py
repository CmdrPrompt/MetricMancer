LANGUAGES = {
	'.js': {
		'name': 'JavaScript',
		'parser': 'JavaScriptComplexityParser'
	},
	'.ts': {
		'name': 'TypeScript',
		'parser': 'TypeScriptComplexityParser'
	},
	'.py': {
		'name': 'Python',
		'parser': 'PythonComplexityParser'
	},
	'.java': {
		'name': 'Java',
		'parser': 'JavaComplexityParser'
	},
	'.cs': {
		'name': 'C#',
		'parser': 'CSharpComplexityParser'
	},
	'.c': {
		'name': 'C',
		'parser': 'CComplexityParser'
	},
	'.cpp': {
		'name': 'C++',
		'parser': 'CppComplexityParser'
	},
	'.go': {
		'name': 'Go',
		'parser': 'GoComplexityParser'
	},
	'.adb': {
		'name': 'Ada',
		'parser': 'AdaComplexityParser'
	}
}

class Config:
	def __init__(self):
		self.languages = LANGUAGES
