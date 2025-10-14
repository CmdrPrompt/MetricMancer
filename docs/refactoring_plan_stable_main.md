# Refactoring Plan: Stabilize main.py

## Problem Statement
`main.py` changes every time a new feature is added because it contains:
- Hardcoded CLI argument to app configuration mapping
- Report generator selection logic
- Feature flag handling with multiple `getattr()` calls

## Goal
Make `main.py` stable by:
1. Extracting configuration into a dedicated class
2. Using Factory pattern for report generator selection
3. Making features pluggable/extensible

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ main.py (STABLE - rarely changes)                           │
│  - Parse CLI args                                            │
│  - Create AppConfig from args                                │
│  - Create MetricMancerApp with config                        │
│  - Call app.run()                                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ AppConfig (Configuration Object)                             │
│  - Holds all application settings                            │
│  - Factory method: from_cli_args(args)                       │
│  - Validation logic                                          │
│  - Default values                                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ MetricMancerApp (Simplified)                                 │
│  - __init__(config: AppConfig)                               │
│  - run() - orchestrates workflow                             │
│  - Uses factories for report generation                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ ReportGeneratorFactory                                       │
│  - create(format: str, config: AppConfig)                    │
│  - Returns appropriate generator instance                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ FeatureRunner (Optional - for extensibility)                 │
│  - run_hotspot_analysis(config, data)                        │
│  - run_review_strategy(config, data)                         │
│  - Makes features pluggable                                  │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Phase 1: Create AppConfig class
**File**: `src/config/app_config.py`

```python
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class AppConfig:
    """Central configuration object for MetricMancer application."""
    
    # Directories to scan
    directories: List[str]
    
    # Threshold settings
    threshold_low: float = 10.0
    threshold_high: float = 20.0
    problem_file_threshold: Optional[float] = None
    
    # Output settings
    output_format: str = "summary"
    output_file: Optional[str] = None
    report_folder: str = "output"
    level: str = "file"
    hierarchical: bool = False
    
    # Hotspot analysis
    list_hotspots: bool = False
    hotspot_threshold: int = 50
    hotspot_output: Optional[str] = None
    
    # Review strategy
    review_strategy: bool = False
    review_output: str = "review_strategy.md"
    review_branch_only: bool = False
    review_base_branch: str = "main"
    
    # Debug
    debug: bool = False
    
    @classmethod
    def from_cli_args(cls, args) -> 'AppConfig':
        """Create AppConfig from parsed CLI arguments."""
        return cls(
            directories=args.directories,
            threshold_low=args.threshold_low,
            threshold_high=args.threshold_high,
            problem_file_threshold=args.problem_file_threshold,
            output_format=args.output_format,
            output_file=None,  # Determined later
            report_folder=getattr(args, 'report_folder', None) or 'output',
            level=args.level,
            hierarchical=args.hierarchical,
            list_hotspots=getattr(args, 'list_hotspots', False),
            hotspot_threshold=getattr(args, 'hotspot_threshold', 50),
            hotspot_output=getattr(args, 'hotspot_output', None),
            review_strategy=getattr(args, 'review_strategy', False),
            review_output=getattr(args, 'review_output', 'review_strategy.md'),
            review_branch_only=getattr(args, 'review_branch_only', False),
            review_base_branch=getattr(args, 'review_base_branch', 'main'),
            debug=getattr(args, 'debug', False)
        )
    
    def validate(self):
        """Validate configuration settings."""
        if self.threshold_low >= self.threshold_high:
            raise ValueError("threshold_low must be less than threshold_high")
        if not self.directories:
            raise ValueError("At least one directory must be specified")
```

### Phase 2: Create ReportGeneratorFactory
**File**: `src/report/report_generator_factory.py`

```python
from typing import Optional, Type
from src.report.report_generator import ReportGenerator
from src.report.cli.cli_report_generator import CLIReportGenerator
from src.report.json.json_report_generator import JSONReportGenerator

class ReportGeneratorFactory:
    """Factory for creating appropriate report generators based on output format."""
    
    @staticmethod
    def create(output_format: str) -> Optional[Type]:
        """
        Create and return the appropriate report generator class.
        
        Args:
            output_format: The desired output format (json, machine, html, etc.)
            
        Returns:
            Report generator class or None for default HTML generator
        """
        generators = {
            'json': JSONReportGenerator,
            'machine': CLIReportGenerator,
            'summary': CLIReportGenerator,
            'quick-wins': CLIReportGenerator,
            'human': CLIReportGenerator,
            'human-tree': CLIReportGenerator,
            'tree': CLIReportGenerator,
        }
        
        # Return None for HTML to use default generator
        if output_format == 'html':
            return None
            
        return generators.get(output_format, CLIReportGenerator)
```

### Phase 3: Refactor MetricMancerApp
**File**: `src/app/metric_mancer_app.py`

```python
class MetricMancerApp:
    def __init__(self, config: AppConfig):
        """Initialize app with configuration object."""
        self.config = config
        self.lang_config = Config()
        self.scanner = Scanner(self.lang_config.languages)
        self.analyzer = Analyzer(
            self.lang_config.languages,
            threshold_low=config.threshold_low,
            threshold_high=config.threshold_high
        )
        
        # Get report generator from factory
        self.report_generator_cls = ReportGeneratorFactory.create(config.output_format)
    
    def run(self):
        """Main execution flow."""
        # Scan
        files = self.scanner.scan(self.config.directories)
        
        # Analyze
        summary = self.analyzer.analyze(files)
        repo_infos = list(summary.values())
        
        # Generate reports
        self._generate_reports(repo_infos)
        
        # Run optional features
        if self.config.list_hotspots:
            self._run_hotspot_analysis(repo_infos)
        
        if self.config.review_strategy:
            self._run_review_strategy(repo_infos)
```

### Phase 4: Simplify main.py
**File**: `src/main.py`

```python
import sys
from src.utilities.cli_helpers import parse_args, print_usage
from src.config.app_config import AppConfig
from src.app.metric_mancer_app import MetricMancerApp
from src.report.report_helpers import get_output_filename
import src.utilities.debug

def main():
    """Main entry point - stable and rarely needs changes."""
    # Configure UTF-8 encoding
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Check for help
    if len(sys.argv) == 1:
        print_usage()
        return
    
    # Parse CLI arguments
    parser = parse_args()
    parser.add_argument('--debug', action='store_true', help='Show debug output')
    args = parser.parse_args()
    
    # Create configuration from CLI args
    config = AppConfig.from_cli_args(args)
    
    # Set debug mode globally
    src.utilities.debug.DEBUG = config.debug
    
    # Determine output file if needed
    if config.output_format in ['html', 'json']:
        config.output_file = get_output_filename(args)
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return
    
    # Run application
    app = MetricMancerApp(config)
    app.run()

if __name__ == "__main__":
    main()
```

## Benefits

### 1. Stability
- **main.py becomes stable**: Only changes for major architectural updates
- **New features don't require main.py changes**: Just add to AppConfig and cli_helpers

### 2. Testability
- Easy to test with different configurations
- Can create AppConfig directly in tests without CLI parsing
- Mock configuration for unit tests

### 3. Maintainability
- Clear separation of concerns
- Configuration logic in one place
- Easy to see all available options

### 4. Extensibility
- New output formats: Add to factory
- New features: Add to AppConfig
- Feature plugins: Implement FeatureRunner pattern

## Migration Strategy

### Step 1: Create new files (non-breaking)
1. Create `src/config/app_config.py`
2. Create `src/report/report_generator_factory.py`
3. Add tests for new components

### Step 2: Refactor MetricMancerApp (breaking change)
1. Update MetricMancerApp to accept AppConfig
2. Update all tests that instantiate MetricMancerApp
3. Verify all tests pass

### Step 3: Simplify main.py
1. Update main.py to use new architecture
2. Run integration tests
3. Verify CLI still works

### Step 4: Cleanup
1. Remove unused code
2. Update documentation
3. Add examples of new pattern

## Testing Strategy

```python
# tests/config/test_app_config.py
def test_app_config_from_cli_args():
    """Test creating config from CLI args."""
    
def test_app_config_validation():
    """Test configuration validation."""
    
def test_app_config_defaults():
    """Test default values are applied."""

# tests/report/test_report_generator_factory.py  
def test_factory_creates_correct_generator():
    """Test factory returns correct generator for format."""
    
def test_factory_handles_unknown_format():
    """Test factory handles unknown formats gracefully."""

# tests/app/test_metric_mancer_app_with_config.py
def test_app_runs_with_config():
    """Test app runs with AppConfig object."""
    
def test_app_runs_hotspot_when_configured():
    """Test hotspot feature runs when enabled in config."""
```

## Example Usage

```python
# Before (tight coupling)
app = MetricMancerApp(
    directories=['src'],
    threshold_low=10.0,
    threshold_high=20.0,
    problem_file_threshold=None,
    output_file='report.html',
    report_generator_cls=None,
    level='file',
    hierarchical=False,
    output_format='html',
    list_hotspots=True,
    hotspot_threshold=50,
    hotspot_output=None,
    # ... 10 more parameters
)

# After (clean and flexible)
config = AppConfig(
    directories=['src'],
    list_hotspots=True
)
app = MetricMancerApp(config)
app.run()

# Or from CLI args
config = AppConfig.from_cli_args(args)
app = MetricMancerApp(config)
app.run()
```

## Impact Analysis

### Files to Change
1. **New files** (3):
   - `src/config/__init__.py`
   - `src/config/app_config.py`
   - `src/report/report_generator_factory.py`

2. **Modified files** (3):
   - `src/main.py` - Simplified
   - `src/app/metric_mancer_app.py` - Accepts AppConfig
   - `src/utilities/cli_helpers.py` - No changes needed!

3. **Test files** (many):
   - All tests that instantiate MetricMancerApp directly

### Estimated Effort
- **Phase 1**: 2-3 hours (Create AppConfig)
- **Phase 2**: 1 hour (Create Factory)
- **Phase 3**: 2-3 hours (Refactor MetricMancerApp)
- **Phase 4**: 1 hour (Simplify main.py)
- **Testing**: 2-3 hours (Update and verify tests)

**Total**: ~8-11 hours

### Risk Assessment
- **Low risk**: Non-breaking changes first
- **Medium risk**: MetricMancerApp signature change affects tests
- **Mitigation**: Comprehensive test suite already exists

## Future Enhancements

Once this pattern is established, we can extend it:

### 1. Plugin System
```python
class FeaturePlugin:
    def should_run(self, config: AppConfig) -> bool:
        """Check if this plugin should run."""
        
    def run(self, config: AppConfig, repo_infos: List):
        """Execute the feature."""

# Register plugins
plugins = [
    HotspotAnalysisPlugin(),
    ReviewStrategyPlugin(),
    CustomMetricPlugin(),
]

for plugin in plugins:
    if plugin.should_run(config):
        plugin.run(config, repo_infos)
```

### 2. Configuration Files
```python
# Load from YAML/JSON
config = AppConfig.from_file('metricmancer.yaml')

# Load from environment
config = AppConfig.from_environment()

# Merge sources
config = AppConfig.from_cli_args(args)
config.merge_from_file('.metricmancer.yaml')
```

### 3. Profile Support
```yaml
# .metricmancer.yaml
profiles:
  quick:
    output_format: summary
    list_hotspots: true
  
  full:
    output_format: html
    list_hotspots: true
    review_strategy: true
    hierarchical: true
```

## Conclusion

This refactoring will:
- ✅ Make `main.py` stable (rarely changes)
- ✅ Improve testability
- ✅ Reduce complexity in MetricMancerApp
- ✅ Enable future extensions
- ✅ Follow SOLID principles (Single Responsibility, Open/Closed)

The main.py file will go from **23 commits/month** to potentially **2-3 commits/year**.
