## Config Loading & CLI Argument Flow (Configuration Object Pattern)

This diagram describes how MetricMancer uses the Configuration Object Pattern to handle configuration. The process starts with CLI argument parsing, creates an AppConfig object using a factory method, validates it automatically, and then uses it throughout the application. This new pattern centralizes configuration and reduces code churn.

```mermaid
flowchart TD
StartConfig[Start: App Launch]:::start
StartConfig --> CLIArgs[Parse CLI Arguments]:::calc
CLIArgs --> CreateAppConfig[AppConfig.from_cli_args]:::agg
CreateAppConfig --> AutoValidate[Automatic validation<br/>in __post_init__]:::calc
AutoValidate --> ConfigOK[AppConfig instance ready]:::agg
ConfigOK --> UseFactory[ReportGeneratorFactory.create]:::agg
UseFactory --> CreateApp[Create MetricMancerApp]:::agg
CreateApp --> EndConfig[Continue App Flow]:::start

%% Edge cases
CLIArgs -.-> WarnCLI[Error: invalid CLI args]:::warn
CreateAppConfig -.-> WarnCreate[Error: missing required fields]:::warn
AutoValidate -.-> WarnVal[Error: validation failed<br/>empty dirs, invalid thresholds]:::warn
UseFactory -.-> WarnFactory[Error: unknown output format]:::warn

%% New pattern highlights
CreateAppConfig -.->|New Pattern!| PatternNote1[Configuration Object Pattern:<br/>Type-safe dataclass with defaults]:::note
AutoValidate -.->|Built-in!| PatternNote2[Validation in __post_init__:<br/>Immediate error detection]:::note
UseFactory -.->|New Pattern!| PatternNote3[Factory Pattern:<br/>No conditional logic]:::note

%% Legend
LegendStart[Start/End]:::start
LegendCalc[Data collection/Computation]:::calc
LegendLoop[Loop/Grouping]:::loop
LegendAgg[Aggregation/Model]:::agg
LegendWarn[Warning/Error]:::warn
LegendNote[Pattern/Note]:::note

LegendStart -.-> LegendCalc
LegendCalc -.-> LegendLoop
LegendLoop -.-> LegendAgg
LegendAgg -.-> LegendWarn
LegendWarn -.-> LegendNote

classDef start fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#212121;
classDef calc fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a237e;
classDef loop fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121;
classDef agg fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c;
classDef warn fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c;
classDef note fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#212121;

class LegendStart start;
class LegendCalc calc;
class LegendLoop loop;
class LegendAgg agg;
class LegendWarn warn;
class LegendNote note;

```

### Configuration Object Pattern Benefits

1. **Single Source of Truth**
   - All configuration in one `AppConfig` dataclass
   - No parameter passing across 5+ functions
   - Clear, documented fields with defaults

2. **Type Safety**
   - Type hints on all fields
   - IDE autocomplete support
   - Compile-time error detection

3. **Built-in Validation**
   - Validates in `__post_init__` automatically
   - Clear error messages
   - Prevents invalid states

4. **Easy Testing**
   - Create config directly: `AppConfig(directories=['test'])`
   - Easy to mock
   - No complex setup needed

### Example Usage

```python
# From CLI arguments (main.py)
config = AppConfig.from_cli_args(args)

# From dictionary (config files)
config_dict = {'directories': ['src'], 'threshold_low': 10.0}
config = AppConfig(**config_dict)

# Direct instantiation (tests)
config = AppConfig(
    directories=['test_data'],
    threshold_low=5.0,
    output_format='json'
)

# Validation happens automatically
try:
    config = AppConfig(directories=[])  # Invalid!
except ValueError as e:
    print(f"Config error: {e}")
```
