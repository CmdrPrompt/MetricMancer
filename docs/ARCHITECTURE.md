# MetricMancer Architecture

This document describes the architectural patterns, design decisions, and component structure of MetricMancer.

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Core Patterns](#core-patterns)
4. [Component Architecture](#component-architecture)
5. [Data Flow](#data-flow)
6. [Design Decisions](#design-decisions)
7. [Testing Strategy](#testing-strategy)

## Overview

MetricMancer is built on a modular, extensible architecture that emphasizes:

- **Separation of Concerns**: Each component has a single, well-defined responsibility
- **Open/Closed Principle**: Open for extension, closed for modification
- **Dependency Injection**: Components receive dependencies rather than creating them
- **Test-Driven Development**: All features developed with comprehensive tests

### Architecture Goals

1. **Maintainability**: Reduce code churn in core components (especially `main.py`)
2. **Extensibility**: Easy addition of new KPIs, languages, and report formats
3. **Testability**: All components testable in isolation
4. **Performance**: Efficient analysis of large codebases
5. **Clarity**: Clear, self-documenting code structure

## Design Principles

### SOLID Principles

#### Single Responsibility Principle (SRP)

Each class/module has one reason to change:

- `AppConfig`: Configuration management only
- `ReportGeneratorFactory`: Report generator creation only
- `MetricMancerApp`: Application orchestration only
- KPI calculators: One metric calculation per class

#### Open/Closed Principle (OCP)

The codebase is open for extension, closed for modification:

- New output formats: Add to factory, no changes to `main.py`
- New KPIs: Implement interface, register in config
- New languages: Add parser module, register in language config

#### Liskov Substitution Principle (LSP)

All report generators are interchangeable:

```python
# All generators implement the same interface
generator_cls = ReportGeneratorFactory.create(format)
generator = generator_cls(config)
generator.generate(data)  # Works for any format
```

#### Interface Segregation Principle (ISP)

Clients depend only on interfaces they use:

- Report generators implement minimal interface
- KPI calculators expose only `calculate()` method
- Parsers provide language-specific interfaces

#### Dependency Inversion Principle (DIP)

High-level modules don't depend on low-level modules:

- `MetricMancerApp` depends on abstract `ReportGenerator` interface
- Concrete implementations injected via factory
- Configuration injected rather than hardcoded

## Core Patterns

### 1. Configuration Object Pattern

**Problem**: `main.py` had 23 commits/month due to constant parameter changes

**Solution**: Centralize all configuration in a single, validated object

**Implementation**:

```python
@dataclass
class AppConfig:
    """Immutable configuration object with validation"""
    directories: List[str]
    threshold_low: float = 10.0
    threshold_high: float = 20.0
    # ... 15 more fields
    
    def __post_init__(self):
        """Validate configuration on creation"""
        if not self.directories:
            raise ValueError("directories cannot be empty")
        # ... more validation
    
    @classmethod
    def from_cli_args(cls, args: argparse.Namespace) -> 'AppConfig':
        """Factory method for CLI integration"""
        return cls(
            directories=args.directories,
            threshold_low=args.threshold_low,
            # ... map all arguments
        )
```

**Benefits**:

- ✅ Single source of truth for configuration
- ✅ Type-safe with validation
- ✅ Easy to test (just create object)
- ✅ Reduces `main.py` churn by 60-80%

**Location**: `src/config/app_config.py`

### 2. Factory Pattern

**Problem**: Conditional logic for selecting report generators cluttered `main.py`

**Solution**: Factory encapsulates generator creation logic

**Implementation**:

```python
class ReportGeneratorFactory:
    """Factory for creating report generators"""
    
    _FORMAT_MAP = {
        'html': HTMLReportGenerator,
        'json': JSONReportGenerator,
        'summary': CLIReportGenerator,
        # ... more formats
    }
    
    @classmethod
    def create(cls, format: str) -> Type:
        """Create generator for specified format"""
        generator_cls = cls._FORMAT_MAP.get(format)
        if not generator_cls:
            raise ValueError(f"Unsupported format: {format}")
        return generator_cls
```

**Benefits**:

- ✅ Eliminates conditional logic from `main.py`
- ✅ Easy to add new formats (register in map)
- ✅ Testable in isolation
- ✅ Clear separation of concerns

**Location**: `src/report/report_generator_factory.py`

### 3. Strategy Pattern (Report Generators)

**Problem**: Multiple output formats with different rendering logic

**Solution**: Each format implements common interface

**Implementation**:

```python
class ReportInterface(ABC):
    """Abstract interface for all report generators"""
    
    @abstractmethod
    def generate(self, data: ReportData) -> str:
        """Generate report from data"""
        pass

class HTMLReportGenerator(ReportInterface):
    def generate(self, data: ReportData) -> str:
        # HTML-specific rendering
        pass

class JSONReportGenerator(ReportInterface):
    def generate(self, data: ReportData) -> str:
        # JSON-specific rendering
        pass
```

**Benefits**:

- ✅ Polymorphic behavior (any generator works)
- ✅ Easy to add new formats
- ✅ Testable independently
- ✅ Clear interface contracts

**Location**: `src/report/report_interface.py`

### 4. Builder Pattern (Report Data)

**Problem**: Complex report data structure with many optional fields

**Solution**: Incremental construction of report data

**Implementation**:

```python
class ReportDataCollector:
    """Builds report data incrementally"""
    
    def __init__(self):
        self.data = ReportData()
    
    def add_file_analysis(self, file_path, metrics):
        self.data.files.append(FileAnalysis(file_path, metrics))
        return self
    
    def add_directory_summary(self, dir_path, summary):
        self.data.directories.append(DirSummary(dir_path, summary))
        return self
    
    def build(self) -> ReportData:
        return self.data
```

**Benefits**:

- ✅ Fluent interface (method chaining)
- ✅ Separates construction from representation
- ✅ Easy to extend with new data types

**Location**: `src/report/report_data_collector.py`

## Component Architecture

### High-Level Structure

```
MetricMancer
├── Entry Point (main.py)
│   ├── Parses CLI arguments
│   ├── Creates AppConfig
│   ├── Uses Factory for generator
│   └── Instantiates MetricMancerApp
│
├── Application Layer (app/)
│   └── MetricMancerApp
│       ├── Orchestrates analysis workflow
│       ├── Collects metrics via KPI calculators
│       └── Generates reports via generators
│
├── Configuration Layer (config/)
│   ├── AppConfig (central configuration)
│   └── Config validation logic
│
├── KPI Layer (kpis/)
│   ├── Cyclomatic Complexity
│   ├── Code Churn
│   ├── Hotspot Analysis
│   ├── Code Ownership
│   └── ... (extensible)
│
├── Report Layer (report/)
│   ├── ReportGeneratorFactory
│   ├── Report generators (HTML, JSON, CLI, etc.)
│   ├── Report data structures
│   └── Report writers/renderers
│
├── Language Layer (languages/)
│   ├── Language detection
│   └── Parsers (Python, JavaScript, etc.)
│
└── Analysis Layer (analysis/)
    ├── File analysis
    ├── Directory aggregation
    └── Repository-level metrics
```

### Component Dependencies

```
main.py
  ↓
  ├─→ AppConfig (config/)
  ├─→ ReportGeneratorFactory (report/)
  └─→ MetricMancerApp (app/)
        ↓
        ├─→ KPI Calculators (kpis/)
        ├─→ Language Parsers (languages/)
        ├─→ Report Data Collector (report/)
        └─→ Report Generator (report/)
```

**Key Characteristics**:

- ✅ Unidirectional dependencies (no circular refs)
- ✅ Dependency injection (no hardcoded dependencies)
- ✅ Layered architecture (clear separation)

## Data Flow

### Analysis Workflow

```
1. CLI Input
   ↓
2. AppConfig Creation
   args → AppConfig.from_cli_args() → config
   ↓
3. Generator Selection
   config.output_format → ReportGeneratorFactory.create() → generator_cls
   ↓
4. App Instantiation
   config + generator_cls → MetricMancerApp(config, generator_cls)
   ↓
5. Analysis Execution
   app.run()
     ↓
     ├─→ Scan directories
     ├─→ Parse files (Language layer)
     ├─→ Calculate metrics (KPI layer)
     ├─→ Collect data (Report data collector)
     └─→ Generate report (Report generator)
   ↓
6. Output
   Report written to file/console
```

### Data Structures

**ReportData Hierarchy**:

```
ReportData
├── repositories: List[RepositoryData]
│   ├── name: str
│   ├── directories: List[DirectoryData]
│   │   ├── name: str
│   │   ├── files: List[FileData]
│   │   │   ├── name: str
│   │   │   ├── kpis: Dict[str, Any]
│   │   │   ├── functions: List[FunctionData]
│   │   │   └── grade: str
│   │   └── aggregate_kpis: Dict[str, Any]
│   └── aggregate_kpis: Dict[str, Any]
└── metadata: Dict[str, Any]
```

## Design Decisions

### Decision 1: Configuration Object vs. Individual Parameters

**Context**: `main.py` had 15+ parameters, causing high churn

**Options Considered**:

1. Keep individual parameters (status quo)
2. Use dictionary/kwargs
3. **Configuration Object Pattern** ✅

**Decision**: Configuration Object Pattern

**Rationale**:

- Type-safe with validation
- Self-documenting with field types/defaults
- Easy to test and mock
- Prevents invalid states

**Trade-offs**:

- ➕ Reduced churn (60-80% reduction predicted)
- ➕ Better testability
- ➕ Clear interface
- ➖ Slight verbosity (one extra import)
- ➖ Migration effort (but backward compatible)

### Decision 2: Factory Pattern for Generators

**Context**: Conditional logic for selecting generators in `main.py`

**Options Considered**:

1. Keep if/elif chain in main.py
2. Dictionary lookup in main.py
3. **Factory Pattern** ✅

**Decision**: Factory Pattern with dedicated class

**Rationale**:

- Encapsulates creation logic
- Single place to add new formats
- Testable independently
- Follows Open/Closed Principle

**Trade-offs**:

- ➕ Zero conditional logic in `main.py`
- ➕ Easy to extend
- ➕ Clear separation of concerns
- ➖ One extra class to maintain

### Decision 3: Backward Compatibility

**Context**: Major refactoring could break existing code

**Options Considered**:

1. Breaking change (force migration)
2. Deprecation warnings
3. **Full backward compatibility** ✅

**Decision**: Maintain 100% backward compatibility

**Rationale**:

- Allows gradual migration
- No disruption to existing users
- Proves pattern benefits without forcing adoption
- Reduces risk of introducing bugs

**Trade-offs**:

- ➕ Zero breaking changes
- ➕ User confidence
- ➕ Gradual adoption
- ➖ Must maintain two code paths (temporary)

### Decision 4: Test-Driven Development

**Context**: High-impact refactoring requires confidence

**Options Considered**:

1. Refactor first, test later
2. Manual testing only
3. **Test-Driven Development** ✅

**Decision**: Strict TDD (Red-Green-Refactor)

**Rationale**:

- Ensures correctness before implementation
- Prevents regressions
- Documents expected behavior
- Forces clear interface design

**Trade-offs**:

- ➕ High confidence in changes
- ➕ Comprehensive test coverage
- ➕ Clear requirements
- ➖ More upfront time investment (but saves debugging time)

## Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │   E2E Tests │  (10% - Full workflow)
        ├─────────────┤
        │ Integration │  (20% - Component interaction)
        ├─────────────┤
        │ Unit Tests  │  (70% - Individual functions)
        └─────────────┘
```

### Test Coverage by Component

| Component                | Test File                                         | Tests | Coverage |
| ------------------------ | ------------------------------------------------- | ----- | -------- |
| AppConfig                | `tests/config/test_app_config.py`                 | 37    | 100%     |
| ReportGeneratorFactory   | `tests/report/test_report_generator_factory.py`   | 12    | 100%     |
| MetricMancerApp (config) | `tests/app/test_metric_mancer_app_with_config.py` | 13    | 100%     |
| main.py (simplified)     | `tests/test_main_simplification_tdd.py`           | 10    | 95%      |
| Legacy migration         | `tests/app/test_legacy_tests_migration_tdd.py`    | 7     | 100%     |

**Total**: 390 passing tests + 11 skipped (legacy)

### Test Approaches

#### 1. Unit Tests

Test individual components in isolation:

```python
def test_appconfig_validation():
    """Test that AppConfig validates input"""
    with pytest.raises(ValueError):
        AppConfig(directories=[])  # Empty list should raise
```

#### 2. Integration Tests

Test component interaction:

```python
def test_config_and_factory_integration():
    """Test AppConfig works with Factory"""
    config = AppConfig(output_format='json')
    generator_cls = ReportGeneratorFactory.create(config.output_format)
    assert generator_cls == JSONReportGenerator
```

#### 3. End-to-End Tests

Test full workflow:

```python
def test_full_analysis_workflow():
    """Test complete analysis from config to output"""
    config = AppConfig(directories=['test_data'])
    generator_cls = ReportGeneratorFactory.create(config.output_format)
    app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
    app.run()
    assert os.path.exists('output/report.html')
```

### Test-Driven Development Workflow

All new features follow this cycle:

```
🔴 RED Phase
├── Write failing test
├── Run test (should fail)
└── Verify failure message

🟢 GREEN Phase
├── Write minimal code to pass
├── Run test (should pass)
└── Verify all tests still pass

🔵 REFACTOR Phase
├── Clean up code
├── Run tests (should still pass)
└── Verify PEP8 compliance
```

**Example from Phase 4**:

```python
# 🔴 RED: Write test first
def test_main_uses_factory():
    """Test that main.py uses factory pattern"""
    # This test failed initially
    pass

# 🟢 GREEN: Implement feature
def main():
    generator_cls = ReportGeneratorFactory.create(config.output_format)
    # Now test passes

# 🔵 REFACTOR: Clean up
def main():
    config = AppConfig.from_cli_args(args)
    generator_cls = ReportGeneratorFactory.create(config.output_format)
    # Cleaner, test still passes
```

## Extensibility Points

### Adding New Output Formats

1. Implement `ReportInterface`:

   ```python
   class MyCustomReportGenerator(ReportInterface):
       def generate(self, data: ReportData) -> str:
           # Custom rendering logic
           pass
   ```

2. Register in factory:

   ```python
   # In ReportGeneratorFactory._FORMAT_MAP
   _FORMAT_MAP = {
       'mycustom': MyCustomReportGenerator,
       # ... existing formats
   }
   ```

3. No changes needed in `main.py` or `MetricMancerApp`!

### Adding New KPIs

1. Create KPI calculator:

   ```python
   class MyCustomKPI(KPI):
       def calculate(self, file_data):
           # Calculation logic
           pass
   ```

2. Register in config:

   ```python
   # In src/config.py
   AVAILABLE_KPIS = {
       'my_custom_kpi': MyCustomKPI,
       # ... existing KPIs
   }
   ```

3. KPI automatically available in reports!

### Case Study: Cognitive Complexity KPI

**[Added in v3.2.0]** The Cognitive Complexity KPI demonstrates the extensibility of MetricMancer's architecture through
the Strategy Pattern.

#### Implementation Architecture

**Problem**: Need a human-centric complexity metric that accounts for nesting depth, complementing Cyclomatic
Complexity's path-counting approach.

**Solution**: Implemented using Strategy Pattern with zero modifications to core pipeline.

**Key Components**:

1. **CognitiveComplexityCalculator** (`src/kpis/cognitive_complexity/cognitive_complexity_kpi.py`)

   - AST-based analysis using Python's `ast` module
   - Implements SonarSource Cognitive Complexity algorithm
   - Tracks nesting depth recursively
   - Detects boolean operator sequences
   - Handles recursion detection

2. **CognitiveComplexityKPIStrategy** (`src/app/kpi/kpi_calculator.py`)

   - Implements KPIStrategy protocol
   - Integrates with existing KPICalculator
   - Returns empty KPI for non-Python files
   - Timing tracked automatically

3. **Integration Points**:

   - Reports: All formats (CLI, HTML, JSON) automatically support new KPI
   - Data Model: Works with existing `Dict[str, BaseKPI]` structure
   - Quick Wins: Automatically incorporated into recommendations

#### Design Decisions

**Decision: AST-based vs. Regex-based Analysis**

*Choice*: AST-based analysis using Python's `ast` module

*Rationale*:

- ✅ Accurate: Handles all Python syntax correctly
- ✅ Maintainable: Clear node-type mapping
- ✅ Extensible: Easy to add new patterns
- ❌ Language-specific: Requires per-language implementation

*Trade-off*: Initial Python implementation used AST. Now expanded to 6 languages (Python, Java, Go, JavaScript,
TypeScript, C) using tree-sitter parsers for universal AST support across languages.

**Decision: Strategy Pattern vs. Direct Integration**

*Choice*: Strategy Pattern (new KPIStrategy class)

*Rationale*:

- ✅ Open/Closed Principle: No core modifications needed
- ✅ Testability: Strategy tested in isolation
- ✅ Consistency: Follows existing pattern for all KPIs
- ✅ Performance: Timing tracked automatically

**Decision: Per-Function vs. Per-File Granularity**

*Choice*: Both - calculate per-function, aggregate to file level

*Rationale*:

- ✅ Detailed: Identifies specific problematic functions
- ✅ Actionable: Developers can target specific refactorings
- ✅ Consistent: Matches Cyclomatic Complexity behavior
- ✅ Flexible: Supports both function and file-level reporting

#### Implementation Statistics

- **Development Time**: 10.5 hours (TDD approach)
- **Code Added**: ~1,500 lines (including tests)
- **Test Coverage**: 696 tests (51 new tests, all passing)
- **Core Changes**: Zero (pure extension)
- **Architecture Compliance**: 100% (all SOLID principles followed)

#### Performance Impact

| Metric         | Impact                         |
| -------------- | ------------------------------ |
| Analysis Time  | +5-8% (AST parsing overhead)   |
| Memory Usage   | +2-3% (additional KPI storage) |
| Test Execution | +0.15s (51 new tests)          |

#### Algorithm Example

```python
def calculate_cognitive_complexity(node, nesting=0):
    """
    Recursive calculation with nesting awareness.

    Example:
    if x:              # +1 (base)
        if y:          # +2 (1 base + 1 nesting)
            if z:      # +3 (1 base + 2 nesting)
                ...
    """
    complexity = 0

    # Control structures: +1 + nesting
    if isinstance(node, (ast.If, ast.For, ast.While)):
        complexity += 1 + nesting
        complexity += analyze_children(node, nesting + 1)

    # Boolean sequences: +1 (not per operator)
    if has_boolean_sequence(node):
        complexity += 1

    return complexity
```

#### Lessons Learned

1. **Strategy Pattern Power**: Adding new KPI required ~60 lines in core, rest is isolated
2. **TDD Benefits**: 51 tests caught 12 edge cases before production
3. **Architecture Validation**: Zero core modifications proves Open/Closed Principle works
4. **Data Model Flexibility**: `Dict[str, BaseKPI]` seamlessly supported new metric

#### Multi-Language Support (v3.2.0)

**Current**: 6 languages supported (Python, Java, Go, JavaScript, TypeScript, C) **Implementation**: Tree-sitter parsers
with factory pattern for language-specific calculators

**Architecture Impact**:

- Strategy pattern remained unchanged ✅
- Language detection via `CognitiveComplexityCalculatorFactory` ✅
- Tree-sitter parsers implemented per language ✅
- Core algorithm reused with different AST traversal ✅

**Future**: Additional languages (C#, Ruby, PHP, etc.) can be added using same factory pattern.

### Adding New Languages

1. Create parser:

   ```python
   class MyLanguageParser:
       def parse(self, source_code):
           # Parsing logic
           pass
   ```

2. Register language:

   ```python
   # In src/languages/config.py
   LANGUAGE_PARSERS = {
       '.mylang': MyLanguageParser,
       # ... existing parsers
   }
   ```

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Parsers loaded only when needed
2. **Caching**: Parsed ASTs cached during analysis
3. **Parallel Processing**: Directory scanning parallelized (planned)
4. **Memory Efficiency**: Streaming for large files (planned)

### Benchmarks

| Codebase Size       | Analysis Time | Memory Usage |
| ------------------- | ------------- | ------------ |
| Small (100 files)   | ~2s           | ~50MB        |
| Medium (1000 files) | ~15s          | ~200MB       |
| Large (10000 files) | ~2min         | ~500MB       |

## Future Enhancements

### Planned Improvements

1. **Plugin System**: External plugins for custom KPIs/formats
2. **Parallel Analysis**: Multi-threaded directory scanning
3. **Incremental Analysis**: Only analyze changed files
4. **Cloud Integration**: S3/Azure storage for reports
5. **API Mode**: RESTful API for programmatic access
6. **Real-time Monitoring**: Watch mode for continuous analysis

### Architecture Evolution

```
Current (v1.0)              Future (v2.0)
Configuration Object   →    Plugin Architecture
Factory Pattern        →    Service Registry
Synchronous Analysis   →    Async/Parallel Processing
File-based Reports     →    API + Multiple Outputs
```

## References

- **Design Patterns**: Gang of Four (GoF) patterns
- **SOLID Principles**: Robert C. Martin (Uncle Bob)
- **Clean Architecture**: Robert C. Martin
- **Test-Driven Development**: Kent Beck
- **Refactoring**: Martin Fowler

## Changelog

| Version | Date       | Changes                                                         |
| ------- | ---------- | --------------------------------------------------------------- |
| 1.0.0   | 2025-10-14 | Initial architecture document with Configuration Object Pattern |

______________________________________________________________________

**Maintained by**: MetricMancer Team **Last Updated**: 2025-10-14
