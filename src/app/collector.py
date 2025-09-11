import os
from collections import defaultdict
from src.languages.config import LANGUAGES
from src.complexity.fileanalyzer import FileAnalyzer
from src.complexity.metrics import grade

__all__ = ["collect_results"]

def collect_results(directories):
    results = defaultdict(lambda: defaultdict(list))

    # Hämta thresholds från miljövariabler eller default
    import os
    threshold_low = float(os.environ.get('THRESHOLD_LOW', 10.0))
    threshold_high = float(os.environ.get('THRESHOLD_HIGH', 20.0))

    for root_dir in directories:
        if not os.path.isdir(root_dir):
            print(f"⚠️ Folder '{root_dir}' doesn't exist – skipping.")
            continue

        for root, _, files in os.walk(root_dir):
            valid_files = (
                (file, os.path.splitext(file)[1])
                for file in files if os.path.splitext(file)[1] in LANGUAGES
            )
            for file, ext in valid_files:
                full_path = os.path.join(root, file)
                analyzer = FileAnalyzer(full_path, root_dir, LANGUAGES[ext])
                if analyzer.load():
                    result = analyzer.analyze()
                    result['grade'] = grade(result['complexity'], threshold_low, threshold_high)
                    results[result['language']][result['root']].append(result)

    # Skapa ett dynamiskt rapportfilnamn
    import datetime
    date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_str = "_".join([os.path.basename(os.path.normpath(d)) for d in directories])
    report_filename = f"report_{dir_str}_{date_str}.html"
    # Returnera både results och filnamn
    return results, report_filename
