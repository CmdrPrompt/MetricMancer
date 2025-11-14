# Refactor: Stabilize main.py using Configuration Object Pattern

Fixes #51

## 🎯 Overview

This PR refactors the MetricMancer application architecture to stabilize `main.py` and improve maintainability by
implementing the Configuration Object and Factory patterns.

## 📊 Current Problem

`main.py` currently has:

- **High Churn**: 23 commits/month
- **Complexity**: 11
- **Hotspot Score**: 253 (Critical)
- Changes required for every new feature
- 15+ parameters passed to `MetricMancerApp`

## 💡 Solution

Implement three design patterns:

1. **Configuration Object Pattern** - Centralize all settings in `AppConfig`
2. **Factory Pattern** - Encapsulate report generator creation
3. **Open/Closed Principle** - Open for extension, closed for modification

## 📋 Implementation Plan

This PR follows a phased approach to minimize risk:

### ✅ Phase 1: Create New Components (Non-Breaking)

- [x] Create branch and draft PR
- [ ] Create `src/config/__init__.py`
- [ ] Create `src/config/app_config.py`
- [ ] Create `src/report/report_generator_factory.py`
- [ ] Add unit tests for `AppConfig`
- [ ] Add unit tests for `ReportGeneratorFactory`

### ⏳ Phase 2: Refactor MetricMancerApp

- [ ] Update `MetricMancerApp.__init__()` to accept `AppConfig`
- [ ] Remove individual parameter passing
- [ ] Update internal methods to use `self.config`

### ⏳ Phase 3: Update Tests

- [ ] Update all tests that instantiate `MetricMancerApp`
- [ ] Add tests for configuration-based flow
- [ ] Verify all 334 tests pass

### ⏳ Phase 4: Simplify main.py

- [ ] Replace parameter construction with `AppConfig.from_cli_args()`
- [ ] Remove hardcoded report generator selection
- [ ] Add error handling for validation

### ⏳ Phase 5: Documentation

- [ ] Update README with new pattern
- [ ] Add configuration examples
- [ ] Update architecture diagrams
- [ ] Remove deprecated code

## 🎯 Expected Benefits

### Code Quality Improvements

| Metric        | Before   | After (Target) | Improvement |
| ------------- | -------- | -------------- | ----------- |
| Complexity    | 11       | \<10           | -10%+       |
| Churn         | 23/month | 2-3/year       | -92%        |
| Hotspot Score | 253      | \<50           | -80%        |
| Parameters    | 15+      | 1              | -93%        |

### Maintainability

- ✅ New features don't require `main.py` changes
- ✅ Clear separation of concerns
- ✅ Easy to test with mock configurations
- ✅ Foundation for config files and plugins

## 🧪 Testing Strategy

- All 334 existing tests must pass
- New tests for `AppConfig` class
- New tests for `ReportGeneratorFactory`
- Integration tests for refactored flow
- No CLI behavior changes for end users

## 📚 Architecture Changes

### Before

```python
main.py (15+ params) → MetricMancerApp → Business Logic
↑ Changes for every feature
```

### After

```python
main.py → AppConfig → MetricMancerApp → Business Logic
          ↑ All configuration
          ↑ Factory pattern
```

## 🔍 Code Examples

### New AppConfig Class

```python
@dataclass
class AppConfig:
    """Central configuration object."""
    directories: List[str]
    threshold_low: float = 10.0
    output_format: str = "summary"
    list_hotspots: bool = False
    # ... all settings
    
    @classmethod
    def from_cli_args(cls, args) -> 'AppConfig':
        """Create from CLI arguments."""
        return cls(
            directories=args.directories,
            threshold_low=args.threshold_low,
            # ...
        )
```

### Simplified main.py

```python
def main():
    args = parse_args().parse_args()
    config = AppConfig.from_cli_args(args)
    config.validate()
    app = MetricMancerApp(config)
    app.run()
```

### Refactored MetricMancerApp

```python
class MetricMancerApp:
    def __init__(self, config: AppConfig):
        self.config = config
        self.report_generator_cls = ReportGeneratorFactory.create(
            config.output_format
        )
```

## ⚠️ Breaking Changes

- `MetricMancerApp` constructor signature changes from 15+ parameters to 1 `AppConfig` object
- All tests that instantiate `MetricMancerApp` directly need updates
- Migration is straightforward - see examples in commits

## 🔗 Related Issues

- Closes #51
- Related to #40 (Cache optimization)
- Related to #49 (Code churn fix)

## 📝 Checklist

- [x] Branch created
- [x] Draft PR created
- [ ] Phase 1 implementation complete
- [ ] Phase 2 implementation complete
- [ ] Phase 3 implementation complete
- [ ] Phase 4 implementation complete
- [ ] Phase 5 implementation complete
- [ ] All tests passing (334/334)
- [ ] Documentation updated
- [ ] Self-analysis shows improved metrics
- [ ] Ready for review

## 🎯 Success Criteria

- [ ] All 334 existing tests pass
- [ ] New tests achieve >90% coverage
- [ ] `main.py` complexity < 10
- [ ] Zero CLI behavior changes
- [ ] Code review approved

## 👀 Review Notes

This is a **DRAFT PR** to track progress through the implementation phases.

**Review Focus Areas:**

1. Is the `AppConfig` design appropriate?
2. Should we use dataclass or regular class?
3. Do we need backward compatibility support?
4. Should config file support be added now or later?

**Do NOT merge** until:

- All phases complete
- All tests pass
- Documentation updated
- Code review approved

______________________________________________________________________

**Estimated Effort**: 8-11 hours **Priority**: Medium **Impact**: High (significantly reduces future maintenance)
