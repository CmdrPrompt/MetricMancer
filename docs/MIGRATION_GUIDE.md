# Migration Guide: Configuration Object Pattern

This guide helps you migrate existing code to use MetricMancer's new Configuration Object Pattern, introduced to reduce
code churn and improve maintainability.

## Table of Contents

1. [Overview](#overview)
2. [Breaking Changes](#breaking-changes)
3. [Migration Steps](#migration-steps)
4. [Common Scenarios](#common-scenarios)
5. [Testing Migration](#testing-migration)
6. [FAQ](#faq)

## Overview

### Why Migrate?

The Configuration Object Pattern was introduced to address:

- **High churn in main.py**: Previously 23 commits/month
- **Repetitive parameter passing**: 15+ parameters manually constructed
- **Difficult testing**: Hard to mock individual settings
- **Poor extensibility**: Adding features required changes across multiple files

### What Changed?

**Before (Old Pattern):**

```python
from src.app.metric_mancer_app import MetricMancerApp

# Manual parameter construction
app = MetricMancerApp(
    directories=['src', 'tests'],
    threshold_low=10.0,
    threshold_high=20.0,
    problem_file_threshold=50.0,
    report_filename='report.html',
    report_folder='output',
    output_format='html',
    level='file',
    show_ownership=True,
    hierarchical=False,
    # ... 8 more parameters
)
app.run()
```

**After (Configuration Object Pattern):**

```python
from src.config.app_config import AppConfig
from src.report.report_generator_factory import ReportGeneratorFactory
from src.app.metric_mancer_app import MetricMancerApp

# Clean configuration object
config = AppConfig(
    directories=['src', 'tests'],
    threshold_low=10.0,
    threshold_high=20.0,
    problem_file_threshold=50.0,
    report_filename='report.html',
    report_folder='output',
    output_format='html',
    level='file',
    show_ownership=True,
    hierarchical=False
)

# Factory handles generator selection
generator_cls = ReportGeneratorFactory.create(config.output_format)

# Simple instantiation
app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
app.run()
```

## Breaking Changes

### ✅ Fully Backward Compatible

**Good news!** The new pattern maintains 100% backward compatibility. The old instantiation method still works:

```python
# This still works - no changes needed
app = MetricMancerApp(
    directories=['src'],
    threshold_low=10.0,
    # ... other parameters
)
```

However, we **strongly recommend** migrating to the new pattern for:

- Better testability
- Easier maintenance
- Future-proof code
- Access to new features

### ⚠️ Deprecation Notice

While the old pattern is currently supported, future versions may deprecate individual parameter passing. Migrate at
your earliest convenience.

## Migration Steps

### Step 1: Import AppConfig

Add the AppConfig import to your code:

```python
from src.config.app_config import AppConfig
```

### Step 2: Create Configuration Object

**Option A: Direct instantiation (for scripts/tests)**

```python
config = AppConfig(
    directories=['src', 'tests'],
    threshold_low=10.0,
    threshold_high=20.0,
    # ... other parameters
)
```

**Option B: From CLI args (for main.py style)**

```python
import argparse

parser = argparse.ArgumentParser()
# ... add arguments
args = parser.parse_args()

config = AppConfig.from_cli_args(args)
```

**Option C: From dictionary (for config files)**

```python
config_dict = {
    'directories': ['src', 'tests'],
    'threshold_low': 10.0,
    'threshold_high': 20.0,
    # ... other settings
}
config = AppConfig(**config_dict)
```

### Step 3: Use Factory for Report Generators

Replace conditional generator selection with factory:

**Before:**

```python
if output_format == 'json':
    from src.report.json_report_generator import JSONReportGenerator
    generator_cls = JSONReportGenerator
elif output_format == 'html':
    from src.report.html_report_format import HTMLReportGenerator
    generator_cls = HTMLReportGenerator
# ... more conditionals
```

**After:**

```python
from src.report.report_generator_factory import ReportGeneratorFactory

generator_cls = ReportGeneratorFactory.create(config.output_format)
```

### Step 4: Update App Instantiation

**Before:**

```python
app = MetricMancerApp(
    directories=dirs,
    threshold_low=low,
    # ... 13 more parameters
)
```

**After:**

```python
app = MetricMancerApp(
    config=config,
    report_generator_cls=generator_cls
)
```

### Step 5: Run Tests

Verify your migration works:

```bash
python -m pytest tests/ -v
```

## Common Scenarios

### Scenario 1: Simple Script

**Before:**

```python
from src.app.metric_mancer_app import MetricMancerApp

app = MetricMancerApp(
    directories=['src'],
    report_folder='my_reports',
    output_format='json'
)
app.run()
```

**After:**

```python
from src.config.app_config import AppConfig
from src.report.report_generator_factory import ReportGeneratorFactory
from src.app.metric_mancer_app import MetricMancerApp

config = AppConfig(
    directories=['src'],
    report_folder='my_reports',
    output_format='json'
)
generator_cls = ReportGeneratorFactory.create(config.output_format)
app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
app.run()
```

### Scenario 2: Testing

**Before:**

```python
def test_app_with_custom_thresholds():
    app = MetricMancerApp(
        directories=['test_data'],
        threshold_low=5.0,
        threshold_high=15.0,
        report_folder='test_output'
    )
    # ... test logic
```

**After:**

```python
def test_app_with_custom_thresholds():
    config = AppConfig(
        directories=['test_data'],
        threshold_low=5.0,
        threshold_high=15.0,
        report_folder='test_output'
    )
    generator_cls = ReportGeneratorFactory.create(config.output_format)
    app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
    # ... test logic
```

**Better: Use config for easier mocking**

```python
from unittest.mock import Mock

def test_app_with_mocked_config():
    # Easy to mock specific attributes
    config = Mock(spec=AppConfig)
    config.directories = ['test_data']
    config.threshold_low = 5.0
    config.output_format = 'json'
    
    generator_cls = ReportGeneratorFactory.create(config.output_format)
    app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
    # ... test logic
```

### Scenario 3: CI/CD Integration

**Before:**

```python
import os

report_folder = os.getenv('REPORT_FOLDER', 'output')
output_format = os.getenv('OUTPUT_FORMAT', 'json')

app = MetricMancerApp(
    directories=['src'],
    report_folder=report_folder,
    output_format=output_format,
    # ... more parameters
)
```

**After:**

```python
import os

config = AppConfig(
    directories=['src'],
    report_folder=os.getenv('REPORT_FOLDER', 'output'),
    output_format=os.getenv('OUTPUT_FORMAT', 'json')
)
generator_cls = ReportGeneratorFactory.create(config.output_format)
app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
```

### Scenario 4: Dynamic Configuration

**Before:**

```python
def create_app_for_environment(env):
    if env == 'production':
        threshold_low = 10.0
        report_folder = '/var/reports'
    else:
        threshold_low = 5.0
        report_folder = 'test_reports'
    
    return MetricMancerApp(
        directories=['src'],
        threshold_low=threshold_low,
        report_folder=report_folder,
        # ... more parameters
    )
```

**After:**

```python
def create_app_for_environment(env):
    if env == 'production':
        config = AppConfig(
            directories=['src'],
            threshold_low=10.0,
            report_folder='/var/reports'
        )
    else:
        config = AppConfig(
            directories=['src'],
            threshold_low=5.0,
            report_folder='test_reports'
        )
    
    generator_cls = ReportGeneratorFactory.create(config.output_format)
    return MetricMancerApp(config=config, report_generator_cls=generator_cls)
```

## Testing Migration

### Verify Backward Compatibility

Test that old code still works:

```python
def test_backward_compatibility():
    # Old style should still work
    app = MetricMancerApp(
        directories=['src'],
        threshold_low=10.0,
        output_format='json'
    )
    assert app.threshold_low == 10.0
    assert app.output_format == 'json'
```

### Test New Pattern

Verify the new pattern works correctly:

```python
def test_config_pattern():
    config = AppConfig(
        directories=['src'],
        threshold_low=10.0,
        output_format='json'
    )
    generator_cls = ReportGeneratorFactory.create(config.output_format)
    app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
    
    assert app.threshold_low == 10.0
    assert app.output_format == 'json'
```

### Integration Test

Full end-to-end test:

```python
def test_full_migration():
    # Create config
    config = AppConfig(
        directories=['test_data'],
        report_filename='test_report.json',
        output_format='json'
    )
    
    # Create generator
    generator_cls = ReportGeneratorFactory.create(config.output_format)
    
    # Create and run app
    app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
    app.run()
    
    # Verify output exists
    import os
    assert os.path.exists('output/test_report.json')
```

## FAQ

### Q: Do I need to migrate immediately?

**A:** No, the old pattern is fully supported. However, migrating now:

- Makes your code future-proof
- Improves testability
- Aligns with best practices
- Reduces maintenance burden

### Q: Will my existing code break?

**A:** No! Backward compatibility is 100% maintained. Your existing code will continue to work without changes.

### Q: What if I have custom extensions?

**A:** Custom KPIs, parsers, and report formats work with both patterns. The configuration object simply provides a
cleaner way to pass settings.

### Q: Can I mix old and new patterns?

**A:** Yes, but not recommended. Choose one pattern and use it consistently for better code clarity.

### Q: How do I migrate tests?

**A:** See [Scenario 2: Testing](#scenario-2-testing) above. The key is using `AppConfig` instead of individual
parameters.

### Q: What about configuration files (JSON/YAML)?

**A:** The `AppConfig` dataclass can be instantiated from a dictionary:

```python
import json

with open('config.json') as f:
    config_dict = json.load(f)
    config = AppConfig(**config_dict)
```

### Q: How do I validate configuration?

**A:** `AppConfig` has built-in validation. Invalid values raise `ValueError`:

```python
try:
    config = AppConfig(
        directories=[],  # Invalid: empty list
        threshold_low=10.0
    )
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Q: Can I extend AppConfig?

**A:** Yes! You can subclass it for custom needs:

```python
from dataclasses import dataclass
from src.config.app_config import AppConfig

@dataclass
class ExtendedConfig(AppConfig):
    my_custom_field: str = 'default_value'
```

### Q: Where can I find more examples?

**A:** Check the test files:

- `tests/test_main_simplification_tdd.py` - Main entry point examples
- `tests/app/test_metric_mancer_app_with_config.py` - App instantiation
- `tests/app/test_legacy_tests_migration_tdd.py` - Migration patterns

### Q: What if I find a bug in the new pattern?

**A:** Please report it on GitHub Issues. Include:

- Minimal reproducible example
- Expected vs. actual behavior
- Your configuration setup

### Q: Will performance be affected?

**A:** No. The Configuration Object Pattern has negligible performance overhead. Benefits far outweigh any minimal
costs.

## Support

For questions or issues:

- **GitHub Issues**: https://github.com/CmdrPrompt/MetricMancer/issues
- **Documentation**: See `README.md` and `SoftwareSpecificationAndDesign.md`
- **Examples**: Check `tests/` directory for comprehensive examples

______________________________________________________________________

**Last Updated:** 2025-10-14 **Version:** 1.0.0 (Configuration Object Pattern introduction)
