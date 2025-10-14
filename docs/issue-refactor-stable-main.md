# Issue: Refactor to Stabilize main.py Using Configuration Object Pattern

## 🎯 Problem Statement

`main.py` has high churn (23 commits/month) because it changes every time a new feature is added. The file currently contains:
- Hardcoded CLI argument to app configuration mapping
- Report generator selection logic  
- Feature flag handling with multiple `getattr()` calls
- 15+ parameters passed to `MetricMancerApp` constructor

This violates the Open/Closed Principle and makes the codebase harder to maintain and test.

## 📊 Current Metrics

From MetricMancer's own quick-wins analysis:
```
1. Add Tests: main.py
   Impact:  ██████░░░░ Medium (6/10)
   Effort:  █░░░░░░░░░ Low (1/10)
   Time:    30-60 min
   Reason:  High churn (Churn:23) - likely lacks test coverage
```

Current complexity:
- **Cyclomatic Complexity**: 11
- **Churn**: 23 commits/month
- **Hotspot Score**: 253 (Critical)

## 🎯 Goals

1. **Stabilize main.py**: Reduce churn from 23/month to ~2-3/year
2. **Improve testability**: Make configuration mockable and easy to test
3. **Enhance maintainability**: Clear separation of concerns
4. **Enable extensibility**: New features shouldn't require main.py changes

## 💡 Proposed Solution

Implement **Configuration Object Pattern** combined with **Factory Pattern**:

### Architecture Overview

```
Current Flow:
main.py (15+ params) → MetricMancerApp → Business Logic
↑ Changes for every new feature

Proposed Flow:
main.py → AppConfig → MetricMancerApp → Business Logic
          ↑ All configuration centralized
          ↑ Factory for report generators
```

### Key Components

#### 1. AppConfig Class (`src/config/app_config.py`)
```python
@dataclass
class AppConfig:
    """Central configuration object for MetricMancer."""
    directories: List[str]
    threshold_low: float = 10.0
    threshold_high: float = 20.0
    output_format: str = "summary"
    list_hotspots: bool = False
    review_strategy: bool = False
    # ... all other settings
    
    @classmethod
    def from_cli_args(cls, args) -> 'AppConfig':
        """Create config from parsed CLI arguments."""
        return cls(
            directories=args.directories,
            threshold_low=args.threshold_low,
            # ... map all arguments
        )
    
    def validate(self):
        """Validate configuration settings."""
        if self.threshold_low >= self.threshold_high:
            raise ValueError("Invalid thresholds")
```

#### 2. ReportGeneratorFactory (`src/report/report_generator_factory.py`)
```python
class ReportGeneratorFactory:
    """Factory for creating report generators."""
    
    @staticmethod
    def create(output_format: str) -> Optional[Type]:
        """Create appropriate generator based on format."""
        generators = {
            'json': JSONReportGenerator,
            'machine': CLIReportGenerator,
            'html': None,  # Default
        }
        return generators.get(output_format, CLIReportGenerator)
```

#### 3. Simplified main.py
```python
def main():
    """Main entry point - stable and rarely needs changes."""
    # Configure UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    if len(sys.argv) == 1:
        print_usage()
        return
    
    # Parse CLI arguments
    parser = parse_args()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    
    # Create configuration
    config = AppConfig.from_cli_args(args)
    src.utilities.debug.DEBUG = config.debug
    
    # Determine output file
    if config.output_format in ['html', 'json']:
        config.output_file = get_output_filename(args)
    
    # Validate and run
    config.validate()
    app = MetricMancerApp(config)
    app.run()
```

#### 4. Refactored MetricMancerApp
```python
class MetricMancerApp:
    def __init__(self, config: AppConfig):
        """Initialize with configuration object."""
        self.config = config
        self.scanner = Scanner(Config().languages)
        self.analyzer = Analyzer(
            Config().languages,
            threshold_low=config.threshold_low,
            threshold_high=config.threshold_high
        )
        self.report_generator_cls = ReportGeneratorFactory.create(
            config.output_format
        )
    
    def run(self):
        """Main execution flow."""
        files = self.scanner.scan(self.config.directories)
        summary = self.analyzer.analyze(files)
        repo_infos = list(summary.values())
        
        self._generate_reports(repo_infos)
        
        if self.config.list_hotspots:
            self._run_hotspot_analysis(repo_infos)
        
        if self.config.review_strategy:
            self._run_review_strategy(repo_infos)
```

## 📋 Implementation Plan

### Phase 1: Create New Components (Non-Breaking)
- [ ] Create `src/config/__init__.py`
- [ ] Create `src/config/app_config.py` with full configuration dataclass
- [ ] Create `src/report/report_generator_factory.py`
- [ ] Add unit tests for AppConfig
- [ ] Add unit tests for ReportGeneratorFactory
- [ ] **Estimated**: 2-3 hours

### Phase 2: Refactor MetricMancerApp (Breaking Change)
- [ ] Update `MetricMancerApp.__init__()` to accept `AppConfig`
- [ ] Remove individual parameter passing
- [ ] Update internal methods to use `self.config`
- [ ] **Estimated**: 2-3 hours

### Phase 3: Update Tests
- [ ] Update all tests that instantiate `MetricMancerApp`
- [ ] Add tests for new configuration-based flow
- [ ] Verify all 334 tests still pass
- [ ] **Estimated**: 2-3 hours

### Phase 4: Simplify main.py
- [ ] Replace parameter construction with `AppConfig.from_cli_args()`
- [ ] Remove hardcoded report generator selection
- [ ] Add error handling for validation
- [ ] **Estimated**: 1 hour

### Phase 5: Documentation and Cleanup
- [ ] Update README with new pattern
- [ ] Add configuration examples
- [ ] Update architecture diagrams
- [ ] Remove deprecated code
- [ ] **Estimated**: 1 hour

**Total Estimated Time**: 8-11 hours

## ✅ Benefits

### Immediate Benefits
1. **Stability**: main.py becomes stable, rarely needs changes
2. **Testability**: Easy to create test configurations without CLI parsing
3. **Readability**: Clear what configuration options exist
4. **Type Safety**: Dataclass provides type hints and validation

### Long-Term Benefits
1. **Extensibility**: New features just extend AppConfig
2. **Configuration Files**: Easy to add YAML/JSON config support
3. **Profiles**: Can add configuration profiles (quick, full, ci)
4. **Plugin System**: Foundation for feature plugins

### Code Quality Impact
- **Before**: Complexity: 11, Churn: 23, Hotspot: 253
- **After** (estimated): Complexity: 5, Churn: 2-3, Hotspot: 10-15

## 🧪 Testing Strategy

```python
# tests/config/test_app_config.py
def test_app_config_from_cli_args()
def test_app_config_validation()
def test_app_config_defaults()

# tests/report/test_report_generator_factory.py
def test_factory_creates_correct_generator()
def test_factory_handles_unknown_format()

# tests/app/test_metric_mancer_app_with_config.py
def test_app_runs_with_config()
def test_app_features_run_when_configured()
```

## 📚 References

### Design Patterns
- **Configuration Object Pattern**: Encapsulate configuration in a single object
- **Factory Pattern**: Encapsulate object creation logic
- **Open/Closed Principle**: Open for extension, closed for modification

### Similar Implementations
- Django Settings object
- Flask Config object
- pytest Config object

### MetricMancer Analysis
- See `docs/refactoring_plan_stable_main.md` for detailed plan
- See `output/review_strategy.md` for code review recommendations
- Self-analysis identified main.py as top quick-win opportunity

## ⚠️ Risks and Mitigation

### Risk 1: Breaking Changes
**Impact**: High - Changes MetricMancerApp signature
**Mitigation**: 
- Comprehensive test suite exists (334 tests)
- Phase implementation allows validation at each step
- Can maintain backward compatibility temporarily

### Risk 2: Migration Effort
**Impact**: Medium - Many test files need updates
**Mitigation**:
- Clear migration guide
- Update tests incrementally
- Run full test suite after each phase

### Risk 3: Learning Curve
**Impact**: Low - New pattern for team
**Mitigation**:
- Well-documented pattern
- Examples in PR
- Reference documentation

## 🎯 Success Criteria

- [ ] All 334 existing tests pass
- [ ] New tests achieve >90% coverage of new code
- [ ] main.py complexity reduced to <10
- [ ] Zero CLI behavior changes for end users
- [ ] Documentation updated
- [ ] Code review approved
- [ ] Metrics show reduced churn after 1 month

## 💬 Discussion Points

1. Should we support backward compatibility for one release?
2. Should AppConfig be a dataclass or regular class?
3. Do we want to add configuration file support immediately or later?
4. Should we implement plugin system in this PR or separate issue?

## 📎 Related Issues

- Issue #40: Cache pre-building optimization
- Issue #49: Code churn time-based fix
- Future: Configuration file support
- Future: Plugin system for extensible features

## 🔗 Pull Request Checklist

When implementing, the PR should include:
- [ ] All code changes
- [ ] Unit tests for new components
- [ ] Integration tests for refactored flow
- [ ] Updated documentation
- [ ] Migration guide for developers
- [ ] Performance benchmarks (no regression)
- [ ] Self-analysis showing improved metrics

---

**Labels**: `enhancement`, `refactoring`, `architecture`, `good-first-issue` (for Phase 1 only)
**Priority**: Medium (improves maintainability but not urgent)
**Effort**: Large (8-11 hours)
**Impact**: High (reduces future maintenance significantly)
