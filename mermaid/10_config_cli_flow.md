## Config Loading & CLI Argument Flow

This diagram describes how MetricMancer loads configuration and parses CLI arguments. The process starts at application launch, parses CLI arguments, loads the config file, merges both sources, and validates the resulting configuration. Edge cases such as missing config files, invalid CLI arguments, or validation errors are highlighted. The color coding and legend are consistent with the rest of the documentation.

```mermaid
flowchart TD
StartConfig[Start: App Launch]:::start
StartConfig --> CLIArgs[Parse CLI Arguments]:::calc
CLIArgs --> ConfigFile[Load Config File]:::calc
ConfigFile --> Merge[Merge CLI & Config]:::agg
Merge --> Validate[Validate Config]:::calc
Validate --> ConfigOK[Config Ready]:::agg
ConfigOK --> EndConfig[Continue App Flow]:::start

%% Edge cases
ConfigFile -.-> WarnConfig[Warn: config file missing/invalid]:::warn
CLIArgs -.-> WarnCLI[Warn: invalid CLI args]:::warn
Validate -.-> WarnVal[Warn: validation error]:::warn

%% Legend
LegendStart[Start/End]:::start
LegendCalc[Data collection/Computation]:::calc
LegendLoop[Loop/Grouping]:::loop
LegendAgg[Aggregation/Model]:::agg
LegendWarn[Warning/Error]:::warn

LegendStart -.-> LegendCalc
LegendCalc -.-> LegendLoop
LegendLoop -.-> LegendAgg
LegendAgg -.-> LegendWarn

classDef start fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#212121;
classDef calc fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a237e;
classDef loop fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121;
classDef agg fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c;
classDef warn fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c;

class LegendStart start;
class LegendCalc calc;
class LegendLoop loop;
class LegendAgg agg;
class LegendWarn warn;

```
