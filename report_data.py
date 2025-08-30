from metrics import grade

class ReportDataBuilder:
    def __init__(self, results, threshold=20.0):
        self.results = results
        self.threshold = threshold

    def average_grade(self, files):
        if not files:
            return "No code"
        avg = sum(f['complexity'] for f in files) / len(files)
        return {
            'value': avg,
            'label': grade(avg),
            'formatted': f"{grade(avg)} ({avg:.1f})"
        }

    def prepare_structured_data(self):
        structured = []
        for language in sorted(self.results):
            language_section = {'name': language, 'roots': []}
            for root in sorted(self.results[language]):
                files = sorted(self.results[language][root], key=lambda x: x['path'])
                language_section['roots'].append({
                    'path': root,
                    'average': self.average_grade(files),
                    'files': files
                })
            structured.append(language_section)
        return structured

    def find_problematic_roots(self):
        summary = []
        for language, roots in self.results.items():
            for root, files in roots.items():
                if not files:
                    continue
                avg = sum(f['complexity'] for f in files) / len(files)
                # Problemfiler: de med komplexitet över threshold
                problem_files = [f for f in files if f['complexity'] > self.threshold]
                if avg > self.threshold:
                    summary.append({
                        'language': language,
                        'root': root,
                        'average': avg,
                        'grade': grade(avg),
                        'problem_files': problem_files
                    })
        return sorted(summary, key=lambda x: (-x['average'], x['language'], x['root']))
