# Kombinera churn och cyklomatisk komplexitet med PyDriller
# Installera först: pip install pydriller

from pydriller import Repository
import os

# Anta att du har en funktion som beräknar cyklomatisk komplexitet för en fil
# Här är ett exempel på stub (byt ut mot din riktiga implementation)
def get_cyclomatic_complexity(filepath):
    # TODO: Anropa din scanner här
    return 10  # Dummyvärde

churn_per_file = {}

# Samla churn-data med PyDriller
for commit in Repository('.').traverse_commits():
    for mod in commit.modifications:
        path = mod.new_path or mod.old_path
        if path:
            churn_per_file.setdefault(path, 0)
            churn_per_file[path] += mod.added + mod.removed

# Kombinera med komplexitet
result = []
for filepath, churn in churn_per_file.items():
    if os.path.isfile(filepath):
        complexity = get_cyclomatic_complexity(filepath)
        result.append({
            'file': filepath,
            'churn': churn,
            'complexity': complexity
        })

# Exempel: hitta refaktoreringskandidater
for entry in result:
    if entry['churn'] > 100 and entry['complexity'] > 10:
        print(f"Refaktoreringskandidat: {entry['file']} (churn={entry['churn']}, komplexitet={entry['complexity']})")
    elif entry['churn'] < 10 and entry['complexity'] > 10:
        print(f"Stabil men riskabel kod: {entry['file']} (churn={entry['churn']}, komplexitet={entry['complexity']})")
