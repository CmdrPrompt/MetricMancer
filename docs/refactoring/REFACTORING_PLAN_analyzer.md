# Refaktoreringsplan för app/analyzer.py

## Sammanfattning av Nuläge

**Fil:** `src/app/analyzer.py`  
**Komplexitet:** 121 (Mycket hög)  
**Code Churn:** 16 commits  
**Hotspot Score:** Kritisk (10/10)  
**Estimerad refaktoreringstid:** 4-8 timmar  

## Analys mot ARCHITECTURE.md

### Problem som identifierats

#### 1. **Bryter mot Single Responsibility Principle (SRP)**
`Analyzer`-klassen har för många ansvarsområden:
- Gruppera filer per repository
- Pre-bygga git cache
- Läsa filinnehåll
- Analysera funktionskomplexitet
- Beräkna Churn KPI
- Beräkna Ownership KPIs
- Beräkna Hotspot KPIs
- Aggregera KPIs för kataloghierarki
- Bygga hierarkisk datamodell

**ARCHITECTURE.md säger:** "Each class/module has one reason to change"

#### 2. **Monolit-funktion istället för Strategy Pattern**
`_process_file()` och `_analyze_repo()` är stora funktioner med hårdkodad logik för varje KPI.

**ARCHITECTURE.md säger:** Använd Strategy Pattern för utbytbara komponenter.

#### 3. **Blandad abstraktionsnivå**
Klassen blandar högnivå-orkestrering med lågnivå-implementationsdetaljer (fil-I/O, timing, etc).

**ARCHITECTURE.md säger:** "High-level modules don't depend on low-level modules"

#### 4. **Tight coupling med alla KPI-klasser**
Analyzer importerar och initierar alla KPI-klasser direkt:
```python
from src.kpis.codeownership import CodeOwnershipKPI
from src.kpis.codechurn import ChurnKPI
from src.kpis.complexity import ComplexityAnalyzer, ComplexityKPI
from src.kpis.hotspot import HotspotKPI
```

**ARCHITECTURE.md säger:** "Dependency Injection: Components receive dependencies rather than creating them"

#### 5. **Timing-logik blandat med affärslogik**
Varje KPI-beräkning har timing-kod inbäddad, vilket gör koden svårare att läsa och testa.

#### 6. **God-Class Anti-Pattern**
Analyzer är en "God Class" som vet för mycket och gör för mycket.

## Refaktoreringsförslag enligt ARCHITECTURE.md

### Fas 1: Extrahera hjälpklasser (2-3 timmar)

#### 1.1 Skapa `FileReader` klass
```python
# src/app/file_reader.py
class FileReader:
    """Handles file I/O operations with error handling."""
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """Read file content with UTF-8 encoding."""
        try:
            with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            debug_print(f"[WARN] Unable to read {file_path}: {e}")
            return None
```

**Motivering:** Single Responsibility - läsning av filer är ett eget ansvarsområde.

#### 1.2 Skapa `TimingTracker` klass
```python
# src/app/timing_tracker.py
from contextlib import contextmanager
import time

class TimingTracker:
    """Tracks execution time for different operations."""
    
    def __init__(self):
        self.timings = {
            'cache_prebuild': 0.0,
            'complexity': 0.0,
            'filechurn': 0.0,
            'hotspot': 0.0,
            'ownership': 0.0,
            'sharedownership': 0.0
        }
    
    @contextmanager
    def track(self, operation: str):
        """Context manager for timing operations."""
        start = time.perf_counter()
        yield
        elapsed = time.perf_counter() - start
        self.timings[operation] += elapsed
    
    def get_timings(self) -> dict:
        """Return copy of timing dictionary."""
        return self.timings.copy()
```

**Motivering:** Separation of Concerns - timing är ortogonalt till affärslogik.

#### 1.3 Skapa `KPIOrchestrator` klass
```python
# src/app/kpi_orchestrator.py
from typing import Dict, Any
from src.kpis.base_kpi import BaseKPI

class KPIOrchestrator:
    """Orchestrates KPI calculation with dependency injection."""
    
    def __init__(self, kpi_calculators: Dict[str, BaseKPI]):
        """
        Args:
            kpi_calculators: Dictionary mapping KPI names to calculator instances
        """
        self.calculators = kpi_calculators
    
    def calculate_file_kpis(self, file_context: Dict[str, Any]) -> Dict[str, BaseKPI]:
        """
        Calculate all KPIs for a file.
        
        Args:
            file_context: Context with file_path, content, complexity, etc.
            
        Returns:
            Dictionary of calculated KPI objects
        """
        kpis = {}
        for name, calculator in self.calculators.items():
            kpi = calculator.calculate(**file_context)
            kpis[kpi.name] = kpi
        return kpis
```

**Motivering:** Strategy Pattern + Dependency Injection - KPI-beräkningar blir utbytbara.

#### 1.4 Skapa `RepositoryGrouper` klass
```python
# src/app/repository_grouper.py
from collections import defaultdict
from typing import List, Dict, Set, Tuple

class RepositoryGrouper:
    """Groups files by repository root."""
    
    def group_by_repository(self, files: List[dict]) -> Tuple[Dict, Dict]:
        """
        Groups files by their repository root directory.
        
        Returns:
            Tuple of (files_by_root, scan_dirs_by_root)
        """
        files_by_root = defaultdict(list)
        scan_dirs_by_root = defaultdict(set)
        
        for file in files:
            repo_root = file.get('root', '')
            files_by_root[repo_root].append(file)
            scan_dirs_by_root[repo_root].add(repo_root)
        
        return files_by_root, scan_dirs_by_root
```

**Motivering:** Single Responsibility - gruppering är en separat operation.

### Fas 2: Extrahera File Processor (2-3 timmar)

#### 2.1 Skapa `FileProcessor` klass
```python
# src/app/file_processor.py
from pathlib import Path
from typing import Optional
from src.kpis.model import File, Function
from src.kpis.complexity import ComplexityAnalyzer, ComplexityKPI

class FileProcessor:
    """Processes individual files for analysis."""
    
    def __init__(self, file_reader, kpi_orchestrator, complexity_analyzer):
        self.file_reader = file_reader
        self.kpi_orchestrator = kpi_orchestrator
        self.complexity_analyzer = complexity_analyzer
    
    def process_file(self, file_info: dict, repo_root_path: Path, 
                     lang_config: dict) -> Optional[File]:
        """
        Process a single file and return File object with all KPIs.
        
        Args:
            file_info: Dictionary with file path and extension
            repo_root_path: Root path of repository
            lang_config: Language configuration
            
        Returns:
            File object with calculated KPIs, or None if processing fails
        """
        file_path = Path(file_info['path'])
        ext = file_info.get('ext')
        
        # Validate extension
        if ext not in lang_config:
            debug_print(f"Skipping file with unknown extension: {file_path}")
            return None
        
        # Read file content
        content = self.file_reader.read_file(file_path)
        if content is None:
            return None
        
        # Analyze functions and complexity
        functions, total_complexity = self._analyze_functions(
            content, lang_config[ext]
        )
        
        # Prepare context for KPI calculation
        file_context = {
            'file_path': str(file_path),
            'repo_root': str(repo_root_path.resolve()),
            'complexity': total_complexity,
            'function_count': len(functions)
        }
        
        # Calculate all KPIs
        kpis = self.kpi_orchestrator.calculate_file_kpis(file_context)
        
        # Create File object
        return File(
            name=file_path.name,
            file_path=str(file_path.relative_to(repo_root_path)),
            kpis=kpis,
            functions=functions
        )
    
    def _analyze_functions(self, content: str, lang_config: dict) -> tuple:
        """Analyze functions in file content."""
        functions_data = self.complexity_analyzer.analyze_functions(
            content, lang_config
        )
        
        function_objects = []
        total_complexity = 0
        
        for func_data in functions_data:
            complexity = func_data.get('complexity', 0)
            func_kpi = ComplexityKPI().calculate(
                complexity=complexity,
                function_count=1
            )
            total_complexity += func_kpi.value
            
            function_objects.append(
                Function(
                    name=func_data.get('name', 'N/A'),
                    kpis={func_kpi.name: func_kpi}
                )
            )
        
        return function_objects, total_complexity
```

**Motivering:** Single Responsibility - filprocessering är ett väldefinierat ansvarsområde.

### Fas 3: Refaktorera Analyzer-klassen (2-3 timmar)

#### 3.1 Ny, smalare Analyzer-klass
```python
# src/app/analyzer.py (REFACTORED)
from pathlib import Path
from tqdm import tqdm
from src.app.repository_grouper import RepositoryGrouper
from src.app.file_processor import FileProcessor
from src.app.hierarchy_builder import HierarchyBuilder
from src.app.timing_tracker import TimingTracker
from src.app.kpi_aggregator import KPIAggregator
from src.kpis.model import RepoInfo
from src.utilities.debug import debug_print

class Analyzer:
    """
    Orchestrates code analysis workflow.
    
    Responsibilities:
    - Coordinate analysis of multiple repositories
    - Delegate file processing to FileProcessor
    - Delegate KPI aggregation to KPIAggregator
    - Track timing information
    
    This class follows the Single Responsibility Principle by focusing
    only on high-level orchestration and delegation.
    """
    
    def __init__(self, languages_config, threshold_low=10.0,
                 threshold_high=20.0, churn_period_days=30):
        """
        Initialize Analyzer with configuration.
        
        Uses Dependency Injection for all major components.
        """
        self.config = languages_config
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.churn_period_days = churn_period_days
        
        # Initialize components (Dependency Injection ready)
        self.timing_tracker = TimingTracker()
        self.repository_grouper = RepositoryGrouper()
        self.hierarchy_builder = HierarchyBuilder()
        
        # These could be injected later for better testability
        from src.app.file_reader import FileReader
        from src.app.kpi_orchestrator import KPIOrchestrator
        from src.kpis.complexity import ComplexityAnalyzer
        
        self.file_reader = FileReader()
        self.kpi_orchestrator = self._create_kpi_orchestrator()
        self.file_processor = FileProcessor(
            self.file_reader,
            self.kpi_orchestrator,
            ComplexityAnalyzer()
        )
        self.kpi_aggregator = KPIAggregator()
    
    def _create_kpi_orchestrator(self):
        """Factory method for creating KPI orchestrator with all calculators."""
        # This could be moved to a separate factory class
        from src.kpis.codechurn import ChurnKPI
        from src.kpis.hotspot import HotspotKPI
        from src.kpis.codeownership import CodeOwnershipKPI
        from src.kpis.sharedcodeownership.shared_code_ownership import SharedOwnershipKPI
        
        calculators = {
            'churn': ChurnKPI(),
            'hotspot': HotspotKPI(),
            'ownership': CodeOwnershipKPI,  # Factory pattern needed here
            'shared_ownership': SharedOwnershipKPI  # Factory pattern needed here
        }
        
        return KPIOrchestrator(calculators)
    
    def analyze(self, files):
        """
        Analyzes a list of files, groups them by repository.
        
        Main entry point following the Template Method pattern.
        """
        if not files:
            return {}
        
        # Step 1: Group files by repository
        files_by_root, scan_dirs_by_root = self.repository_grouper.group_by_repository(files)
        debug_print(f"[DEBUG] Found {len(files_by_root)} repositories to analyze.")
        
        # Step 2: Analyze each repository
        summary = {}
        for repo_root in sorted(files_by_root.keys()):
            repo_info = self._analyze_repository(
                repo_root,
                files_by_root[repo_root],
                list(scan_dirs_by_root[repo_root])
            )
            if repo_info is not None:
                summary[repo_root] = repo_info
        
        return summary
    
    def _analyze_repository(self, repo_root: str, files_in_repo: list, 
                           scan_dirs: list):
        """
        Analyzes a single repository's files.
        
        Uses Template Method pattern for consistent workflow.
        """
        debug_print(f"[DEBUG] Analyzing repo: {repo_root} with {len(files_in_repo)} files.")
        
        if not files_in_repo:
            debug_print(f"[DEBUG] No files to analyze for repo: {repo_root}")
            return None
        
        repo_root_path = Path(repo_root)
        
        # Step 1: Create repository info object
        repo_info = RepoInfo(
            repo_root_path=repo_root,
            repo_name=repo_root_path.name,
            dir_name=repo_root_path.name,
            scan_dir_path="."
        )
        
        # Step 2: Pre-build git cache for performance
        with self.timing_tracker.track('cache_prebuild'):
            self._prebuild_git_cache(repo_root_path, files_in_repo)
        
        # Step 3: Process each file
        for file_info in tqdm(files_in_repo, 
                             desc=f"Analyzing files in {repo_root_path.name}", 
                             unit="file"):
            file_obj = self.file_processor.process_file(
                file_info,
                repo_root_path,
                self.config
            )
            if file_obj:
                self.hierarchy_builder.add_file_to_hierarchy(repo_info, file_obj)
        
        # Step 4: Aggregate KPIs for directory hierarchy
        self.kpi_aggregator.aggregate_directory_kpis(repo_info)
        
        return repo_info
    
    def _prebuild_git_cache(self, repo_root_path: Path, files_in_repo: list):
        """Pre-build git cache for all files in repository."""
        from src.utilities.git_cache import get_git_cache
        
        git_cache = get_git_cache(churn_period_days=self.churn_period_days)
        
        file_paths = [
            str(Path(file_info['path']).relative_to(repo_root_path))
            for file_info in files_in_repo
        ]
        
        debug_print(f"[PREBUILD] Pre-building cache for {len(file_paths)} files")
        git_cache.prebuild_cache_for_files(str(repo_root_path.resolve()), file_paths)
    
    def get_timing_info(self):
        """Return timing information for analysis operations."""
        return self.timing_tracker.get_timings()
```

**Motivering:**
- ✅ Single Responsibility: Endast orkestrering
- ✅ Dependency Injection: Komponenter kan injiceras
- ✅ Open/Closed: Lätt att utöka med nya KPIs
- ✅ Testability: Varje komponent testbar isolerat
- ✅ Komplexitet reducerad från 121 till ~30-40

#### 3.2 Skapa `KPIAggregator` klass
```python
# src/app/kpi_aggregator.py
from src.kpis.model import ScanDir
from src.kpis.complexity import ComplexityKPI
from src.kpis.codechurn import ChurnKPI
from src.kpis.hotspot import HotspotKPI

class KPIAggregator:
    """Aggregates KPIs across directory hierarchies."""
    
    def aggregate_directory_kpis(self, scan_dir: ScanDir):
        """
        Recursively aggregate KPIs from files and subdirectories.
        
        Implements the Composite pattern for hierarchical aggregation.
        """
        # Collect KPI values from files
        kpi_values = self._collect_kpi_values(scan_dir)
        
        # Recursively aggregate from subdirectories
        for subdir in scan_dir.scan_dirs.values():
            sub_kpis = self.aggregate_directory_kpis(subdir)
            self._merge_kpi_values(kpi_values, sub_kpis)
        
        # Calculate averages
        avg_kpis = self._calculate_averages(kpi_values)
        
        # Store aggregated KPIs
        self._store_aggregated_kpis(scan_dir, avg_kpis, kpi_values)
        
        return avg_kpis
    
    def _collect_kpi_values(self, scan_dir: ScanDir) -> dict:
        """Collect KPI values from files in directory."""
        # Implementation moved from helper functions
        pass
    
    def _merge_kpi_values(self, target: dict, source: dict):
        """Merge KPI values from subdirectory."""
        # Implementation moved from helper functions
        pass
    
    def _calculate_averages(self, kpi_values: dict) -> dict:
        """Calculate average values for each KPI."""
        # Implementation moved from helper functions
        pass
    
    def _store_aggregated_kpis(self, scan_dir: ScanDir, avg_kpis: dict, 
                               kpi_values: dict):
        """Store aggregated KPIs in scan directory."""
        # Implementation moved from helper functions
        pass
```

**Motivering:** Separation of Concerns - aggregering är en komplex operation som förtjänar egen klass.

## Implementationsplan

### Steg 1: Skapa tester först (TDD)
```python
# tests/app/test_file_reader.py
def test_file_reader_reads_valid_file():
    reader = FileReader()
    content = reader.read_file(Path("test_file.py"))
    assert content is not None

# tests/app/test_timing_tracker.py
def test_timing_tracker_context_manager():
    tracker = TimingTracker()
    with tracker.track('test'):
        time.sleep(0.1)
    assert tracker.timings['test'] >= 0.1

# tests/app/test_kpi_orchestrator.py
def test_kpi_orchestrator_calculates_all_kpis():
    calculators = {
        'test': MockKPI()
    }
    orchestrator = KPIOrchestrator(calculators)
    kpis = orchestrator.calculate_file_kpis({})
    assert 'test' in kpis
```

### Steg 2: Implementera nya klasser
1. `FileReader` (30 min)
2. `TimingTracker` (30 min)
3. `RepositoryGrouper` (30 min)
4. `KPIOrchestrator` (1 tim)
5. `FileProcessor` (2 tim)
6. `KPIAggregator` (2 tim)

### Steg 3: Refaktorera Analyzer
1. Skapa ny Analyzer som använder nya klasser (2 tim)
2. Kör alla befintliga tester (ska passera)
3. Lägg till nya tester för Analyzer (1 tim)

### Steg 4: Ta bort gamla helper-funktioner
1. Migrera logik till nya klasser
2. Ta bort modul-nivå funktioner
3. Uppdatera imports

## Förväntade Resultat

### Före Refaktorering
- **Komplexitet:** 121
- **Antal ansvarsområden:** ~10
- **Testbarhet:** Svår (många beroenden)
- **Utbyggbarhet:** Svår (tight coupling)

### Efter Refaktorering
- **Komplexitet:** 30-40 (totalt över alla klasser)
  - `Analyzer`: 20-25
  - `FileProcessor`: 15-20
  - `KPIOrchestrator`: 10-15
  - `KPIAggregator`: 20-25
  - Övriga: <10 vardera
- **Antal ansvarsområden per klass:** 1
- **Testbarhet:** Utmärkt (dependency injection)
- **Utbyggbarhet:** Utmärkt (open/closed principle)

### Fördelar
✅ Följer SOLID-principer från ARCHITECTURE.md  
✅ Enklare att testa (varje klass isolerat)  
✅ Lättare att underhålla (Single Responsibility)  
✅ Enklare att utöka (Dependency Injection + Strategy Pattern)  
✅ Bättre kodläsbarhet (Clear abstractions)  
✅ Reducerad komplexitet (från 121 till 30-40 per klass)  
✅ Minskad churn-risk (mindre påverkan vid ändringar)  

### Risker
⚠️ **Migration risk:** Måste säkerställa bakåtkompatibilitet  
⚠️ **Test coverage:** Måste ha 100% täckning innan refaktorering  
⚠️ **Performance:** Kan behöva optimera om många små objekt skapas  

### Mitigering
- Kör alla befintliga tester efter varje steg
- Använd TDD (Red-Green-Refactor)
- Behåll gamla API:er temporärt för bakåtkompatibilitet
- Profila prestanda efter refaktorering

## Nästa Steg

1. ✅ **Granska denna plan** med teamet
2. 🔴 **Skapa feature branch:** `refactor/analyzer-split`
3. 🔴 **Implementera Fas 1:** Helper-klasser (2-3 tim)
4. 🔴 **Implementera Fas 2:** FileProcessor (2-3 tim)
5. 🔴 **Implementera Fas 3:** Refaktorera Analyzer (2-3 tim)
6. 🔴 **Code review & merge**

## Referenser

- **ARCHITECTURE.md:** Design Principles & SOLID
- **Quick Wins Report:** Analyzer identified as highest priority
- **Test Strategy:** TDD with Red-Green-Refactor cycle
- **Design Patterns:** Strategy, Dependency Injection, Template Method, Composite

---
**Skapad:** 2025-10-16  
**Estimerad tid:** 6-9 timmar total  
**Prioritet:** Hög (Kritisk hotspot)  
**Impact:** 10/10, Effort: 7/10
