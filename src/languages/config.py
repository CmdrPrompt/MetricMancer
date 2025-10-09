"""
Defines supported programming languages and their associated complexity parser classes.
"""
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
    """
    Configuration class for language support in MetricMancer.
    Provides access to the supported languages and their parsers.
    """
    def __init__(self):
        self.languages = LANGUAGES
