# Architecture Class Diagram - Configuration Object Pattern (2025-10-14)

## Overview

This PlantUML class diagram illustrates the new MetricMancer architecture after the Configuration Object Pattern refactoring. It shows how the main entry point, configuration management, factory pattern, and application layer work together to reduce code complexity and churn.

## Key Components

### Entry Point Layer

**main.py**
- Simplified entry point (reduced from ~70 to 58 lines)
- No conditional logic for format selection
- Clean, linear flow using patterns below

### Configuration Layer

**AppConfig** (Configuration Object Pattern)
- **Purpose**: Centralize all application settings in a type-safe dataclass
- **Key Features**:
  - 18 fields with type hints and defaults
  - Built-in validation in `__post_init__`
  - Factory method `from_cli_args()` for CLI integration
  - Easy to test and mock
- **Benefits**:
  - Single source of truth for configuration
  - Type-safe with IDE support
  - Prevents invalid states
  - Reduces parameter passing across functions

### Factory Layer

**ReportGeneratorFactory** (Factory Pattern)
- **Purpose**: Encapsulate report generator creation logic
- **Key Features**:
  - Format mapping dictionary `_FORMAT_MAP`
  - `create()` method returns appropriate generator class
  - Support checking methods
- **Benefits**:
  - No conditional logic in main.py
  - Easy to add new output formats
  - Single responsibility principle
  - Open/Closed principle (open for extension, closed for modification)

### Application Layer

**MetricMancerApp**
- **Purpose**: Orchestrate the analysis workflow
- **Key Features**:
  - Accepts `AppConfig` as primary parameter (new pattern)
  - Maintains backward compatibility with individual parameters
  - Dependency injection for report generator
- **Responsibilities**:
  - Coordinate Scanner, Analyzer, and Report Generation
  - Handle hotspot analysis and code review generation
  - Manage output file creation

### Report Generation

**ReportInterface** (Strategy Pattern)
- Abstract interface defining `generate()` method
- Implemented by:
  - `HTMLReportGenerator` - Interactive HTML reports
  - `JSONReportGenerator` - Machine-readable JSON
  - `CLIReportGenerator` - Terminal output

### Analysis Layer

**Scanner**
- Scans directories and finds files to analyze
- Parallel processing with ThreadPoolExecutor

**Analyzer**
- Analyzes files for complexity, churn, ownership
- Calculates KPIs and builds hierarchical model

## Design Patterns

### 1. Configuration Object Pattern
```python
# Before: 15+ parameters
app = MetricMancerApp(
    directories=['src'],
    threshold_low=10.0,
    threshold_high=20.0,
    # ... 12 more parameters
)

# After: Single config object
config = AppConfig.from_cli_args(args)
app = MetricMancerApp(config=config)
```

**Benefits**:
- Reduced parameter passing
- Type safety
- Easy validation
- Clear documentation

### 2. Factory Pattern
```python
# Before: Conditional logic
if format == 'json':
    generator_cls = JSONReportGenerator
elif format == 'html':
    generator_cls = HTMLReportGenerator
# ... more conditionals

# After: Factory handles it
generator_cls = ReportGeneratorFactory.create(config.output_format)
```

**Benefits**:
- No conditionals in main code
- Easy to extend
- Single place to add formats
- Clear separation of concerns

### 3. Dependency Injection
```python
# Config and generator injected into app
app = MetricMancerApp(
    config=config,
    report_generator_cls=generator_cls
)
```

**Benefits**:
- Loose coupling
- Easy to test
- Clear dependencies
- Flexible configuration

## Architecture Benefits

### Reduced Code Churn
- **Before**: main.py had 23 commits/month (Hotspot score: 253)
- **After**: Predicted 60-80% reduction in future churn
- **Reason**: New features extend patterns, don't modify main.py

### Improved Maintainability
- **Code reduction**: 17% in main.py (70 → 58 lines)
- **Complexity reduction**: Eliminated conditional logic
- **Clear responsibilities**: Each component has one job

### Better Testability
- **AppConfig**: Easy to create test instances
- **Factory**: Testable in isolation
- **MetricMancerApp**: Easy to mock dependencies

### Future-Proof Design
- **Easy to extend**: Add new formats, KPIs, or features
- **Backward compatible**: Old code still works
- **Migration path**: Clear guide for users

## Backward Compatibility

The refactoring maintains 100% backward compatibility:

```python
# Old pattern still works
app = MetricMancerApp(
    directories=['src'],
    threshold_low=10.0,
    # ... individual parameters
)

# New pattern is preferred
config = AppConfig(directories=['src'], threshold_low=10.0)
app = MetricMancerApp(config=config)
```

## Related Documentation

- **Migration Guide**: `/MIGRATION_GUIDE.md`
- **Architecture Doc**: `/ARCHITECTURE.md`
- **Data Model**: `data_model_2025-09-24.puml` (unchanged by refactoring)
- **Mermaid Diagrams**: `/mermaid/13_main_entry_flow.md`

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-14 | 1.0 | Initial architecture diagram with Configuration Object Pattern |

---

**Note**: This diagram focuses on the **architecture** changes from the refactoring. The **data model** (RepoInfo, ScanDir, File, Function, BaseKPI) remains unchanged and is documented in `data_model_2025-09-24.puml`.
