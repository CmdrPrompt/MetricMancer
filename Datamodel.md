
## Kravspec med datamodell

### Kravspec
- KPI:er ska vara egna objekt för att kunna använda metadata. Varje KPI-klass ska implementera sin metod att beräkna KPIet. Komplettera de befintliga KPI-klasserna så att de också kan bära sina resultat och beräkningsvärden där så är relevant.

### RepoInfo
```python
class RepoInfo:
    repo_root_path: str  # Absolut sökväg till repo
    repo_name: str       # Namn på repo
    scan_dirs: Dict[str, ScanDir]  # dir_name -> ScanDir
    kpis: Dict[str, Any]           # KPI:er på repo-nivå (valfritt)
```

### ScanDir
```python
class ScanDir:
    scan_dir_path: str              # Relativ sökväg från repo_root
    dir_name: str                   # Namn på katalogen
    files: Dict[str, File]          # file_name -> File
    scan_dirs: Dict[str, ScanDir]   # dir_name -> ScanDir (rekursivt)
    kpis: Dict[str, Any]            # KPI:er på katalognivå (valfritt)
```

### File
```python
class File:
    file_path: str                  # Relativ sökväg från ScanDir
    name: str                       # Filnamn
    kpis: Dict[str, Any]            # KPI:er för filen
```

### KPI (valfri struktur för typning och metadata)
```python
class KPI:
    name: str
    value: Any
    unit: Optional[str] = None
    description: Optional[str] = None
```

### Exempel på datastruktur (JSON-liknande)
```json
{
  "repo_root_path": "/home/user/project",
  "repo_name": "project",
  "scan_dirs": {
    "src": {
      "scan_dir_path": "src",
      "dir_name": "src",
      "files": {
        "main.py": {
          "file_path": "main.py",
          "name": "main.py",
          "kpis": {"complexity": 7, "churn": 3}
        }
      },
      "scan_dirs": {},
      "kpis": {"avg_complexity": 5.2}
    },
    "tests": {
      "scan_dir_path": "tests",
      "dir_name": "tests",
      "files": {},
      "scan_dirs": {},
      "kpis": {}
    }
  },
  "kpis": {"total_files": 10}
}
```

**Kommentarer:**
- Dicts används för snabb lookup, men om ordning är viktig kan även en lista användas parallellt (t.ex. `scan_dirs_list: List[ScanDir]`).
- Modellen är lätt att serialisera till JSON och passar för rekursiv traversering och rapportering.
