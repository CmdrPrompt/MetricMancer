LANGUAGES = {
    '.js': {
        'name': 'JavaScript',
        'patterns': [r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b',
                     r'\bswitch\b', r'\bcase\b', r'\bcatch\b', r'\bthrow\b',
                     r'\breturn\b', r'&&', r'\|\|'],
        'function_pattern': r'function\s+\w+\s*\(.*?\)\s*\{'
    },
    '.ts': {
        'name': 'TypeScript',
        'patterns': [r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b',
                     r'\bswitch\b', r'\bcase\b', r'\bcatch\b', r'\bthrow\b',
                     r'\breturn\b', r'&&', r'\|\|'],
        'function_pattern': r'function\s+\w+\s*\(.*?\)\s*\{'
    },
    '.py': {
        'name': 'Python',
        'patterns': [r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
                     r'\btry\b', r'\bexcept\b', r'\breturn\b',
                     r'\band\b', r'\bor\b'],
        'function_pattern': r'def\s+\w+\s*\(.*?\)\s*:'
    },
    '.java': {
        'name': 'Java',
        'patterns': [r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\bswitch\b',
                     r'\bcase\b', r'\bcatch\b', r'\bthrow\b', r'\breturn\b',
                     r'&&', r'\|\|'],
        'function_pattern': r'(public|private|protected)?\s+\w+\s+\w+\s*\(.*?\)\s*\{'
    },
    '.cs': {
        'name': 'C#',
        'patterns': [r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\bswitch\b',
                     r'\bcase\b', r'\bcatch\b', r'\bthrow\b', r'\breturn\b',
                     r'&&', r'\|\|'],
        'function_pattern': r'(public|private|protected)?\s+\w+\s+\w+\s*\(.*?\)\s*\{'
    }
}
