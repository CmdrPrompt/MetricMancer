import os
from collections import defaultdict
from config import LANGUAGES
from analyzer import analyze_file, FileAnalyzer

def grade(value):
    if value <= 10: return "Low ✅"
    elif value <= 20: return "Medium ⚠️"
    else: return "High ❌"

def collect_results(directories):
    results = defaultdict(lambda: defaultdict(list))

    for root_dir in directories:
        if not os.path.isdir(root_dir):
            print(f"⚠️ Mappen '{root_dir}' finns inte – hoppar över.")
            continue

        for root, _, files in os.walk(root_dir):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in LANGUAGES:
                    full_path = os.path.join(root, file)
                    result = analyze_file(full_path, root_dir, ext)
                    if result:
                        result['grade'] = grade(result['complexity'])
                        results[result['language']][result['root']].append(result)

    return results
