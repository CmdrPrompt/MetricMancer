"""
Defines supported programming languages and their associated complexity parser classes.
"""
LANGUAGES = {
    '.js': {
        'name': 'JavaScript',
        'parser': 'JavaScriptComplexityParser'
    },
    '.jsx': {
        'name': 'JavaScript (JSX)',
        'parser': 'JavaScriptComplexityParser'
    },
    '.ts': {
        'name': 'TypeScript',
        'parser': 'TypeScriptComplexityParser'
    },
    '.tsx': {
        'name': 'TypeScript (TSX)',
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
    },
    # Structured data files
    '.json': {
        'name': 'JSON',
        'parser': 'JSONComplexityParser'
    },
    '.yaml': {
        'name': 'YAML',
        'parser': 'YAMLComplexityParser'
    },
    '.yml': {
        'name': 'YAML',
        'parser': 'YAMLComplexityParser'
    },
    # Shell scripts
    '.sh': {
        'name': 'Shell Script',
        'parser': 'ShellComplexityParser'
    },
    '.bash': {
        'name': 'Bash Script',
        'parser': 'ShellComplexityParser'
    },
    # Interface Definition Language
    '.idl': {
        'name': 'IDL',
        'parser': 'IDLComplexityParser'
    }
}


class Config:
    """
    Configuration class for language support in MetricMancer.
    Provides access to the supported languages and their parsers.
    """

    def __init__(self):
        self.languages = LANGUAGES
