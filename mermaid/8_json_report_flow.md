
## JSON Report Flow
This diagram shows the flow for generating a JSON report in MetricMancer, from data preparation and serialization to file writing. Edge cases such as serialization and file write errors are visualized, with color coding and legend matching the rest of the documentation.

```mermaid
flowchart TD
StartJSON[Start JSONReportGenerator]:::start
StartJSON --> Prepare[Prepare data]:::calc
Prepare --> Serialize[Serialize to JSON]:::agg
Serialize --> WriteFile[Write JSON file]:::agg
WriteFile --> EndNode[End]:::start

%% Edge cases
WriteFile -.-> WarnWrite[Warn: file write error]:::warn
Serialize -.-> WarnSer[Warn: serialization error]:::warn
Prepare -.-> WarnPrep[Warn: missing/invalid data]:::warn

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
