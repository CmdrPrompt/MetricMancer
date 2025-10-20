# Refactoring Plan: metric_mancer_app.py

**Status**: Draft
**Created**: 2025-10-20
**Target**: Reduce complexity from C:92, Cog:35 to C:<50, Cog:<15
**Risk Level**: CRITICAL (Hotspot Score: 1196)

---

## Executive Summary

`metric_mancer_app.py` is a critical orchestrator file with high complexity and frequent changes. This refactoring plan aims to:

1. **Reduce Cyclomatic Complexity**: 92 → <50 (-45%)
2. **Reduce Cognitive Complexity**: 35 → <15 (-57%)
3. **Improve Testability**: Better separation of concerns
4. **Maintain Backward Compatibility**: Use Adapter pattern during transition
5. **Reduce Hotspot Risk**: Lower churn impact by simplifying structure

---

## Current State Analysis

### Metrics
```
Cyclomatic Complexity: 92
Cognitive Complexity:  35
Churn:                 13 commits
Hotspot Score:         1196
Lines of Code:         409
Methods:               16
Average Method Length: 23.2 lines
```

### Responsibilities (Violation of SRP)
Current file handles:
1. ✅ Configuration management (good - uses Configuration Object Pattern)
2. ❌ Scanning orchestration
3. ❌ Analysis orchestration
4. ❌ Report generation orchestration
5. ❌ Hotspot analysis
6. ❌ Review strategy analysis
7. ❌ Delta review analysis
8. ❌ Timing management
9. ❌ File system operations

**Problem**: Too many responsibilities → High complexity, hard to test, frequent changes

### Code Smells Identified

1. **Long Parameter Lists** (Code Smell)
   - `__init__`: 20 parameters (before config refactor had 19)
   - `_initialize_config`: 19 parameters
   - Solution: ✅ Already using AppConfig, but need to clean up legacy parameters

2. **Feature Envy** (Code Smell)
   - Multiple methods just delegate to other classes
   - Example: `_run_hotspot_analysis` → `extract_hotspots_from_data`
   - Solution: Move to dedicated coordinator classes

3. **Long Methods**
   - `__init__`: 46 lines
   - `_initialize_config`: 40 lines
   - `run`: 40 lines
   - Solution: Extract methods, use composition

4. **Divergent Change** (Code Smell)
   - File changes for multiple reasons (hotspot features, review features, delta features)
   - Solution: Split into focused coordinators

---

## Refactoring Strategy

### Design Patterns to Apply

1. **Facade Pattern** (Primary)
   - `MetricMancerApp` becomes a simple facade
   - Delegates to specialized coordinators
   - Hides complexity from clients

2. **Strategy Pattern** (For Analysis Types)
   - `AnalysisStrategy` interface
   - Implementations: `HotspotAnalysis`, `ReviewAnalysis`, `DeltaAnalysis`
   - Enables adding new analysis types without modifying core

3. **Builder Pattern** (For Configuration)
   - Already using `AppConfig.from_cli_args()`
   - Can extend with `AppConfigBuilder` for programmatic construction

4. **Chain of Responsibility** (For Analysis Pipeline)
   - `AnalysisStep` interface with `execute()` and `next()`
   - Steps: Scan → Analyze → Report → PostProcess
   - Easy to add/remove/reorder steps

5. **Adapter Pattern** (For Backward Compatibility)
   - `LegacyMetricMancerAppAdapter` wraps new structure
   - Maintains old API during transition
   - Can be deprecated after migration period

---

## Refactoring Phases

### Phase 1: Extract Analysis Coordinators (Week 1)
**Goal**: Reduce file complexity by 30%
**Risk**: Low (extraction only, no logic changes)

#### 1.1 Create `AnalysisCoordinator` Base Class
```python
# src/app/coordination/analysis_coordinator.py
from abc import ABC, abstractmethod
from typing import List
from src.kpis.model import RepoInfo

class AnalysisCoordinator(ABC):
    """Base class for all analysis coordinators."""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def can_handle(self) -> bool:
        """Check if this coordinator should run."""
        pass

    @abstractmethod
    def execute(self, repo_infos: List[RepoInfo]) -> None:
        """Execute the analysis."""
        pass
```

#### 1.2 Extract HotspotAnalysisCoordinator
Move methods:
- `_run_hotspot_analysis()` → `HotspotAnalysisCoordinator.execute()`
- `_extract_all_hotspots()` → `HotspotAnalysisCoordinator._extract_hotspots()`
- `_display_or_save_hotspots()` → `HotspotAnalysisCoordinator._save_output()`

**Expected Reduction**: -50 lines, -8 complexity points

```python
# src/app/coordination/hotspot_analysis_coordinator.py
class HotspotAnalysisCoordinator(AnalysisCoordinator):
    def can_handle(self) -> bool:
        return self.config.list_hotspots

    def execute(self, repo_infos: List[RepoInfo]) -> None:
        hotspots = self._extract_hotspots(repo_infos)
        if hotspots:
            self._save_output(hotspots)
        else:
            print(f"\n✅ No hotspots found above threshold.")
```

#### 1.3 Extract ReviewStrategyCoordinator
Move methods:
- `_run_review_strategy_analysis()` → `ReviewStrategyCoordinator.execute()`
- `_convert_and_merge_repo_data()` → `ReviewStrategyCoordinator._prepare_data()`
- `_get_changed_files_for_review()` → `ReviewStrategyCoordinator._get_changed_files()`
- `_generate_and_save_review_report()` → `ReviewStrategyCoordinator._save_report()`

**Expected Reduction**: -100 lines, -12 complexity points

#### 1.4 Update Tests
- Create `test_analysis_coordinator.py`
- Create `test_hotspot_analysis_coordinator.py`
- Create `test_review_strategy_coordinator.py`
- Update `test_metric_mancer_app.py` to use mocks for coordinators

**Testing Strategy**: RED-GREEN-REFACTOR
1. 🔴 RED: Write failing tests for new coordinators
2. 🟢 GREEN: Move code to coordinators, tests pass
3. 🔵 REFACTOR: Clean up and optimize

---

### Phase 2: Simplify Initialization (Week 2)
**Goal**: Reduce constructor complexity
**Risk**: Medium (affects public API)

#### 2.1 Remove Legacy Parameters
Currently `__init__` accepts both `config` and individual parameters for backward compatibility.

**Step 1**: Add deprecation warnings (1 release cycle)
```python
def __init__(self, config: Optional[AppConfig] = None, **kwargs):
    if kwargs and config is None:
        warnings.warn(
            "Passing individual parameters is deprecated. Use AppConfig instead.",
            DeprecationWarning,
            stacklevel=2
        )
        config = AppConfig(**kwargs)
    elif kwargs and config is not None:
        raise ValueError("Cannot pass both config and individual parameters")
```

**Step 2**: Remove legacy parameters (next major version)
```python
def __init__(self, config: AppConfig):
    """Initialize MetricMancerApp with configuration."""
    config.validate()
    self.config = config
    # ... simplified initialization
```

**Expected Reduction**: -30 lines, -5 complexity points

#### 2.2 Extract Dependency Initialization
```python
# src/app/infrastructure/dependency_factory.py
class DependencyFactory:
    """Factory for creating app dependencies."""

    @staticmethod
    def create_scanner(config: AppConfig) -> Scanner:
        lang_config = Config()
        return Scanner(lang_config.languages)

    @staticmethod
    def create_analyzer(config: AppConfig) -> Analyzer:
        lang_config = Config()
        return Analyzer(
            lang_config.languages,
            threshold_low=config.threshold_low,
            threshold_high=config.threshold_high,
            churn_period_days=config.churn_period
        )
```

**Usage in __init__**:
```python
def __init__(self, config: AppConfig):
    self.config = config
    self.scanner = DependencyFactory.create_scanner(config)
    self.analyzer = DependencyFactory.create_analyzer(config)
    self.coordinators = self._create_coordinators()
```

**Expected Reduction**: -15 lines, -3 complexity points

---

### Phase 3: Implement Analysis Pipeline (Week 3)
**Goal**: Make execution flow more maintainable
**Risk**: Medium (changes core execution logic)

#### 3.1 Create Pipeline Interface
```python
# src/app/pipeline/analysis_pipeline.py
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class PipelineStep:
    name: str
    execute: Callable
    timing_key: str

class AnalysisPipeline:
    """Orchestrates the analysis workflow."""

    def __init__(self, timing_reporter):
        self.steps = []
        self.timing = timing_reporter

    def add_step(self, name: str, execute_fn: Callable, timing_key: str):
        self.steps.append(PipelineStep(name, execute_fn, timing_key))
        return self  # Enable fluent interface

    def execute(self):
        results = {}
        for step in self.steps:
            self.timing.start(step.timing_key)
            results[step.name] = step.execute()
            self.timing.end(step.timing_key)
        return results
```

#### 3.2 Refactor `run()` Method
**Before** (40 lines, complex):
```python
def run(self):
    timing_reporter = TimingReporter()
    timing_reporter.start_scan()
    files = self._scan_files()
    timing_reporter.end_scan()
    # ... 30 more lines
```

**After** (15 lines, simple):
```python
def run(self):
    timing_reporter = TimingReporter()

    # Build pipeline
    pipeline = (AnalysisPipeline(timing_reporter)
        .add_step('scan', self._scan_files, 'scan')
        .add_step('analyze', lambda: self._analyze_files(pipeline.get_result('scan')), 'analysis')
        .add_step('report', lambda: self._generate_reports(pipeline.get_result('analyze')), 'report')
    )

    # Execute
    results = pipeline.execute()

    # Run post-analysis coordinators
    self._run_post_analysis(results['analyze'])

    # Print summary
    timing_reporter.print_summary(self.analyzer.timing)
```

**Expected Reduction**: -25 lines, -8 complexity points

---

### Phase 4: Add Comprehensive Tests (Week 4)
**Goal**: Ensure refactoring didn't break anything
**Risk**: Low (testing phase)

#### 4.1 Test Coverage Targets
```
Current Coverage: Unknown
Target Coverage:  >85%

Critical paths to test:
- Configuration initialization (both new and legacy)
- Pipeline execution with all steps
- Coordinator execution and ordering
- Error handling in all coordinators
- Backward compatibility adapter
```

#### 4.2 Create Integration Tests
```python
# tests/integration/test_metric_mancer_app_integration.py
class TestMetricMancerAppIntegration:
    """End-to-end tests for MetricMancerApp."""

    def test_full_analysis_workflow(self):
        """Test complete analysis from scan to report."""
        # Given
        config = AppConfig(
            directories=['tests/fixtures/sample_repo'],
            output_format='json',
            report_folder='output/test'
        )
        app = MetricMancerApp(config)

        # When
        app.run()

        # Then
        assert os.path.exists('output/test/report.json')
        # ... verify report contents

    def test_hotspot_analysis_integration(self):
        """Test hotspot analysis with real data."""
        # ...

    def test_review_strategy_integration(self):
        """Test review strategy generation."""
        # ...
```

#### 4.3 Create Unit Tests for Each Coordinator
```python
# tests/app/coordination/test_hotspot_analysis_coordinator.py
class TestHotspotAnalysisCoordinator:
    def test_can_handle_returns_true_when_enabled(self):
        # Given
        config = AppConfig(directories=['.'], list_hotspots=True)
        coordinator = HotspotAnalysisCoordinator(config)

        # When/Then
        assert coordinator.can_handle() is True

    def test_execute_extracts_and_saves_hotspots(self, mock_repo_infos):
        # ...
```

---

### Phase 5: Documentation & Knowledge Transfer (Week 5)
**Goal**: Ensure team understands new architecture
**Risk**: Low

#### 5.1 Update Architecture Documentation
- Add UML class diagram for new structure
- Document coordinator pattern usage
- Add sequence diagrams for key workflows

#### 5.2 Update CLAUDE.md
Add section on new architecture:
```markdown
## Architecture: MetricMancerApp Refactoring (v4.0.0)

MetricMancerApp follows the **Facade Pattern** with specialized coordinators:

### Core Components:
1. **MetricMancerApp** (Facade)
   - Simple entry point
   - Delegates to coordinators
   - Manages pipeline execution

2. **AnalysisCoordinator** (Strategy Pattern)
   - HotspotAnalysisCoordinator
   - ReviewStrategyCoordinator
   - DeltaReviewCoordinator
   - ReportCoordinator (already exists)

3. **AnalysisPipeline** (Chain of Responsibility)
   - Scan → Analyze → Report → Post-Process
   - Each step is isolated and testable

### Adding New Features:
1. Create new coordinator extending AnalysisCoordinator
2. Register in MetricMancerApp._create_coordinators()
3. Add tests in tests/app/coordination/
```

#### 5.3 Create Migration Guide
```markdown
# Migration Guide: MetricMancerApp v3 → v4

## For Users
No changes needed if using CLI - backwards compatible.

## For Developers/Integrators

### Old API (Deprecated)
```python
app = MetricMancerApp(
    directories=['src/'],
    threshold_low=10,
    threshold_high=20,
    output_format='html'
)
```

### New API (Recommended)
```python
config = AppConfig(
    directories=['src/'],
    threshold_low=10,
    threshold_high=20,
    output_format='html'
)
app = MetricMancerApp(config)
```
```

---

## Expected Results

### Complexity Reduction
```
Metric                  | Before | After  | Change
------------------------|--------|--------|--------
Cyclomatic Complexity   | 92     | <50    | -45%
Cognitive Complexity    | 35     | <15    | -57%
Lines of Code           | 409    | ~250   | -39%
Number of Methods       | 16     | ~10    | -38%
Average Method Length   | 23.2   | <20    | -14%
Max Nesting Depth       | 2      | 1      | -50%
```

### Maintainability Improvements
- ✅ Single Responsibility: Each coordinator has one job
- ✅ Open/Closed: Easy to add new analysis types
- ✅ Testability: Each component can be tested in isolation
- ✅ Readability: Clear separation of concerns
- ✅ Extensibility: Pipeline-based architecture

### Risk Reduction
```
Hotspot Score: 1196 → <500 (target)
- Reduced complexity = less likely to introduce bugs
- Better separation = more localized changes
- Improved tests = faster bug detection
```

---

## Risk Management

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing integrations | Medium | High | Use Adapter pattern for backward compatibility |
| Introducing bugs during refactor | Medium | High | Comprehensive test suite, TDD approach |
| Team learning curve | Low | Medium | Documentation, pair programming sessions |
| Performance regression | Low | Low | Benchmark before/after, profile if needed |

### Rollback Plan
1. Keep old implementation in separate branch
2. Feature flag for new vs old implementation
3. Can toggle via environment variable:
   ```
   METRICMANCER_USE_LEGACY_APP=1 python -m src.main src/
   ```

---

## Success Metrics

### Quantitative
- [ ] Cyclomatic Complexity < 50
- [ ] Cognitive Complexity < 15
- [ ] Test Coverage > 85%
- [ ] All existing tests pass
- [ ] Performance within 5% of baseline

### Qualitative
- [ ] Code review approval from 2+ team members
- [ ] Documentation complete and reviewed
- [ ] Team training completed
- [ ] No critical bugs in first 2 weeks post-release

---

## Timeline

```
Week 1: Extract Coordinators
├── Days 1-2: Create base classes and HotspotAnalysisCoordinator
├── Days 3-4: Create ReviewStrategyCoordinator
└── Day 5: Tests and validation

Week 2: Simplify Initialization
├── Days 1-2: Add deprecation warnings
├── Days 3-4: Extract DependencyFactory
└── Day 5: Update tests

Week 3: Implement Pipeline
├── Days 1-2: Create AnalysisPipeline
├── Days 3-4: Refactor run() method
└── Day 5: Integration testing

Week 4: Comprehensive Testing
├── Days 1-3: Unit tests for all components
├── Day 4: Integration tests
└── Day 5: Performance testing

Week 5: Documentation & Release
├── Days 1-2: Update documentation
├── Day 3: Knowledge transfer session
├── Day 4: Code review
└── Day 5: Release preparation
```

**Total Effort**: 5 weeks (1 developer full-time, or 2 developers half-time)

---

## Next Steps

1. **Review this plan** with team
2. **Create GitHub issue** for tracking: "Refactor: Reduce MetricMancerApp complexity"
3. **Create branch**: `refactor/metric-mancer-app-simplification`
4. **Start Phase 1**: Extract coordinators
5. **Daily standups**: Track progress and blockers

---

## References

- **Martin Fowler - Refactoring**: Catalog of code smells and refactoring patterns
- **Clean Code (Robert Martin)**: Chapter on SRP and class design
- **ARCHITECTURE.md**: Current patterns and principles
- **Code Review Advisor**: Generated this recommendation based on metrics

---

**Status**: Ready for review
**Author**: Claude Code (AI-assisted)
**Reviewers**: [To be assigned]
**Approval Date**: [Pending]
