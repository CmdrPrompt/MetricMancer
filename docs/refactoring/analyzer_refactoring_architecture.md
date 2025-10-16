# Analyzer Refactoring Architecture

## Current Architecture (Problematic)

```
┌─────────────────────────────────────────────────────────┐
│                    Analyzer (God Class)                 │
│                  Complexity: 121 🔴                      │
├─────────────────────────────────────────────────────────┤
│ Responsibilities:                                       │
│ • Group files by repository                            │
│ • Pre-build git cache                                  │
│ • Read file content                                    │
│ • Analyze function complexity                          │
│ • Calculate Churn KPI                                  │
│ • Calculate Ownership KPIs                             │
│ • Calculate Hotspot KPIs                               │
│ • Aggregate directory KPIs                             │
│ • Build hierarchy                                      │
│ • Track timing                                         │
├─────────────────────────────────────────────────────────┤
│ Direct Dependencies:                                    │
│ • ComplexityAnalyzer                                   │
│ • ChurnKPI                                             │
│ • HotspotKPI                                           │
│ • CodeOwnershipKPI                                     │
│ • SharedOwnershipKPI                                   │
│ • HierarchyBuilder                                     │
│ • Path, tqdm, time, defaultdict                       │
└─────────────────────────────────────────────────────────┘
                          ↓
              ❌ Tight Coupling
              ❌ Hard to Test
              ❌ High Complexity
              ❌ Many Responsibilities
```

## Proposed Architecture (SOLID Principles)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Analyzer (Orchestrator)                      │
│                     Complexity: 20-25 ✅                         │
├─────────────────────────────────────────────────────────────────┤
│ Single Responsibility: Orchestrate analysis workflow           │
│                                                                 │
│ Methods:                                                        │
│ • analyze(files) → summary                                     │
│ • _analyze_repository(repo_root, files) → RepoInfo           │
│ • _prebuild_git_cache(repo_root, files)                       │
│ • get_timing_info() → dict                                     │
└─────────────────────────────────────────────────────────────────┘
           │
           │ Delegates to ↓
           │
    ┌──────┴────────┬─────────────┬──────────────┬──────────────┐
    ↓               ↓             ↓              ↓              ↓
┌────────┐  ┌──────────────┐ ┌────────────┐ ┌──────────┐ ┌──────────────┐
│Repository│ │FileProcessor│ │KPI         │ │Hierarchy │ │Timing        │
│Grouper   │ │             │ │Orchestrator│ │Builder   │ │Tracker       │
│          │ │C: 15-20     │ │            │ │          │ │              │
│C: 5-10   │ │             │ │C: 10-15    │ │C: 10-15  │ │C: 5-10       │
└────────┘  └──────────────┘ └────────────┘ └──────────┘ └──────────────┘
                   │                │
                   │                │
         ┌─────────┴────────┐      │
         ↓                  ↓      ↓
    ┌──────────┐      ┌──────────────┐
    │FileReader│      │KPI           │
    │          │      │Aggregator    │
    │C: 5      │      │              │
    └──────────┘      │C: 20-25      │
                      └──────────────┘

Legend:
C = Cyclomatic Complexity
→ = Dependency
↓ = Delegates to
```

## Component Responsibilities

### 1. Analyzer (Orchestrator)
**Complexity:** 20-25  
**Responsibility:** High-level workflow orchestration  
```python
class Analyzer:
    def analyze(files):
        """Main entry point - coordinates entire analysis workflow"""
        groups = repository_grouper.group_by_repository(files)
        for repo in groups:
            repo_info = self._analyze_repository(repo)
        return summary
```

**Key Principles:**
- ✅ Single Responsibility: Only orchestration
- ✅ Dependency Injection: Components injected/created in constructor
- ✅ Open/Closed: Easy to add new steps without modifying
- ✅ Template Method Pattern: Defines workflow skeleton

---

### 2. RepositoryGrouper
**Complexity:** 5-10  
**Responsibility:** Group files by repository root  
```python
class RepositoryGrouper:
    def group_by_repository(files):
        """Groups files by repo root, returns (files_by_root, scan_dirs)"""
```

**Key Principles:**
- ✅ Single Responsibility: Only grouping logic
- ✅ Pure function: No side effects
- ✅ Easy to test: Simple input/output

---

### 3. FileProcessor
**Complexity:** 15-20  
**Responsibility:** Process individual files for analysis  
```python
class FileProcessor:
    def __init__(file_reader, kpi_orchestrator, complexity_analyzer):
        """Dependency Injection"""
    
    def process_file(file_info, repo_root, lang_config):
        """Process one file: read, analyze, calculate KPIs"""
        content = file_reader.read_file(path)
        functions, complexity = _analyze_functions(content)
        kpis = kpi_orchestrator.calculate_file_kpis(context)
        return File(...)
```

**Key Principles:**
- ✅ Single Responsibility: File-level processing
- ✅ Dependency Injection: All dependencies injected
- ✅ Testable: Mock dependencies easily

---

### 4. FileReader
**Complexity:** 5  
**Responsibility:** Read file content with error handling  
```python
class FileReader:
    def read_file(file_path):
        """Read file with UTF-8 encoding, return None on error"""
```

**Key Principles:**
- ✅ Single Responsibility: Only file I/O
- ✅ Error handling: Graceful failures
- ✅ Easy to mock: Simple interface

---

### 5. KPIOrchestrator
**Complexity:** 10-15  
**Responsibility:** Coordinate KPI calculations  
```python
class KPIOrchestrator:
    def __init__(kpi_calculators):
        """Strategy Pattern: KPI calculators are strategies"""
    
    def calculate_file_kpis(file_context):
        """Calculate all KPIs for a file context"""
        for name, calculator in calculators.items():
            kpis[name] = calculator.calculate(**file_context)
        return kpis
```

**Key Principles:**
- ✅ Strategy Pattern: KPIs are interchangeable strategies
- ✅ Open/Closed: Add new KPIs without modification
- ✅ Dependency Injection: KPI calculators injected

---

### 6. KPIAggregator
**Complexity:** 20-25  
**Responsibility:** Aggregate KPIs across directory hierarchy  
```python
class KPIAggregator:
    def aggregate_directory_kpis(scan_dir):
        """Recursively aggregate KPIs (Composite Pattern)"""
        values = _collect_from_files(scan_dir)
        for subdir in scan_dir.subdirs:
            sub_values = aggregate_directory_kpis(subdir)  # Recursive
            _merge_values(values, sub_values)
        scan_dir.kpis = _calculate_averages(values)
```

**Key Principles:**
- ✅ Composite Pattern: Treats files and dirs uniformly
- ✅ Single Responsibility: Only aggregation
- ✅ Recursive structure: Natural fit for directory trees

---

### 7. HierarchyBuilder
**Complexity:** 10-15  
**Responsibility:** Build hierarchical data model  
```python
class HierarchyBuilder:
    def add_file_to_hierarchy(repo_info, file_obj):
        """Add file to correct position in directory tree"""
```

**Key Principles:**
- ✅ Builder Pattern: Incremental construction
- ✅ Single Responsibility: Only hierarchy building
- ✅ Existing code: Already well-designed

---

### 8. TimingTracker
**Complexity:** 5-10  
**Responsibility:** Track execution time for operations  
```python
class TimingTracker:
    @contextmanager
    def track(operation):
        """Context manager for timing"""
        start = time.perf_counter()
        yield
        elapsed = time.perf_counter() - start
        timings[operation] += elapsed
```

**Key Principles:**
- ✅ Single Responsibility: Only timing
- ✅ Context Manager: Clean API
- ✅ Separation of Concerns: Timing is orthogonal

---

## Data Flow

```
Input: List of file paths
         ↓
   ┌─────────────────┐
   │RepositoryGrouper│
   └─────────────────┘
         ↓
   Files grouped by repo
         ↓
   For each repository:
         ↓
   ┌──────────────────┐
   │Git Cache Prebuild│ (Performance optimization)
   └──────────────────┘
         ↓
   For each file:
         ↓
   ┌──────────────┐
   │FileProcessor │
   └──────────────┘
         ↓
   ┌──────────────┐      ┌─────────────┐
   │FileReader    │─────→│File content │
   └──────────────┘      └─────────────┘
         ↓                      ↓
   ┌──────────────────┐        │
   │ComplexityAnalyzer│←───────┘
   └──────────────────┘
         ↓
   Functions + Complexity
         ↓
   ┌───────────────┐
   │KPIOrchestrator│
   └───────────────┘
         ↓
   All KPIs calculated
         ↓
   ┌────────────────┐
   │HierarchyBuilder│
   └────────────────┘
         ↓
   File added to hierarchy
         ↓
   End of file loop
         ↓
   ┌──────────────┐
   │KPIAggregator │
   └──────────────┘
         ↓
   Directory KPIs aggregated
         ↓
Output: RepoInfo with complete hierarchy
```

## Benefits of New Architecture

### Before
```
❌ Complexity: 121
❌ Responsibilities: 10+
❌ Testability: Difficult
❌ Extensibility: Hard
❌ Maintainability: Poor
❌ Coupling: Tight
```

### After
```
✅ Complexity: 20-25 per class (max)
✅ Responsibilities: 1 per class
✅ Testability: Easy (dependency injection)
✅ Extensibility: Easy (strategy pattern)
✅ Maintainability: Excellent (SOLID)
✅ Coupling: Loose (interfaces)
```

## SOLID Compliance Matrix

| Class              | SRP | OCP | LSP | ISP | DIP |
|-------------------|-----|-----|-----|-----|-----|
| Analyzer          | ✅  | ✅  | N/A | ✅  | ✅  |
| RepositoryGrouper | ✅  | ✅  | N/A | ✅  | ✅  |
| FileProcessor     | ✅  | ✅  | N/A | ✅  | ✅  |
| FileReader        | ✅  | ✅  | N/A | ✅  | ✅  |
| KPIOrchestrator   | ✅  | ✅  | ✅  | ✅  | ✅  |
| KPIAggregator     | ✅  | ✅  | N/A | ✅  | ✅  |
| HierarchyBuilder  | ✅  | ✅  | N/A | ✅  | ✅  |
| TimingTracker     | ✅  | ✅  | N/A | ✅  | ✅  |

Legend:
- **SRP**: Single Responsibility Principle
- **OCP**: Open/Closed Principle
- **LSP**: Liskov Substitution Principle
- **ISP**: Interface Segregation Principle
- **DIP**: Dependency Inversion Principle
- **N/A**: Not applicable (no inheritance/interface)

## Testing Strategy

### Unit Tests (Each Class Isolated)

```python
# test_file_reader.py
def test_file_reader_success():
    reader = FileReader()
    content = reader.read_file(Path("test.py"))
    assert content is not None

def test_file_reader_handles_missing_file():
    reader = FileReader()
    content = reader.read_file(Path("nonexistent.py"))
    assert content is None

# test_kpi_orchestrator.py
def test_orchestrator_calls_all_calculators():
    mock_calculators = {
        'test1': Mock(calculate=Mock(return_value=MockKPI())),
        'test2': Mock(calculate=Mock(return_value=MockKPI()))
    }
    orchestrator = KPIOrchestrator(mock_calculators)
    kpis = orchestrator.calculate_file_kpis({})
    
    assert len(kpis) == 2
    mock_calculators['test1'].calculate.assert_called_once()
    mock_calculators['test2'].calculate.assert_called_once()

# test_file_processor.py
def test_processor_returns_none_for_invalid_extension():
    processor = FileProcessor(mock_reader, mock_orchestrator, mock_analyzer)
    result = processor.process_file({'ext': '.unknown'}, Path('.'), {})
    assert result is None

def test_processor_creates_file_object():
    processor = FileProcessor(mock_reader, mock_orchestrator, mock_analyzer)
    result = processor.process_file(valid_file_info, Path('.'), lang_config)
    assert isinstance(result, File)
    assert result.kpis is not None
```

### Integration Tests (Components Together)

```python
def test_analyzer_with_real_components():
    """Test Analyzer with real FileProcessor and KPIOrchestrator"""
    analyzer = Analyzer(lang_config)
    files = [{'path': 'test.py', 'ext': '.py', 'root': '.'}]
    result = analyzer.analyze(files)
    assert len(result) > 0

def test_file_processor_integration():
    """Test FileProcessor with real FileReader and KPIOrchestrator"""
    reader = FileReader()
    orchestrator = KPIOrchestrator(real_calculators)
    processor = FileProcessor(reader, orchestrator, ComplexityAnalyzer())
    
    result = processor.process_file(file_info, repo_root, lang_config)
    assert result.kpis['complexity'].value > 0
```

### End-to-End Tests

```python
def test_full_analysis_workflow():
    """Test complete analysis from files to RepoInfo"""
    analyzer = Analyzer(Config().languages)
    files = scan_directory('test_data')
    summary = analyzer.analyze(files)
    
    assert len(summary) == 1
    repo_info = summary[list(summary.keys())[0]]
    assert repo_info.kpis is not None
    assert len(repo_info.files) > 0
```

## Migration Strategy

### Phase 1: Create New Classes (No Breaking Changes)
1. Add new classes alongside existing code
2. Write comprehensive unit tests for each
3. Ensure all tests pass

### Phase 2: Integrate New Classes
1. Modify Analyzer to use new classes
2. Keep old methods as fallback
3. Run all existing tests (should pass)

### Phase 3: Cleanup
1. Remove old helper functions
2. Simplify Analyzer class
3. Update documentation

### Phase 4: Optimize
1. Profile performance
2. Optimize hot paths if needed
3. Add caching if beneficial

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing tests | High | Keep old API temporarily |
| Performance regression | Medium | Profile before/after |
| Increased object creation overhead | Low | Use object pooling if needed |
| Team learning curve | Medium | Provide documentation & examples |
| Incomplete coverage | High | TDD - write tests first |

## Success Metrics

| Metric | Before | Target | Success Criteria |
|--------|--------|--------|------------------|
| Complexity (Analyzer) | 121 | 20-25 | ✅ <30 |
| Total Complexity (all classes) | 121 | 100-120 | ✅ <150 |
| Test Coverage | 80% | 95% | ✅ >90% |
| Number of Responsibilities (Analyzer) | 10+ | 1 | ✅ 1-2 |
| Lines per Class | 150+ | <100 | ✅ <150 |
| Performance (relative) | 1.0x | 0.9-1.1x | ✅ <1.2x |

---

**Document Version:** 1.0  
**Created:** 2025-10-16  
**Status:** Proposed  
**Estimated Implementation Time:** 6-9 hours
