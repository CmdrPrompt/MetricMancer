## System Error Handling Flow

This diagram shows the system-level error handling flow in MetricMancer. The main operation is attempted, and on success, the flow continues as normal. If an exception occurs, it is caught, logged, and a user-facing error or warning is shown. Unhandled exceptions are also visualized as edge cases. The color coding and legend are consistent with the rest of the documentation.

```mermaid
flowchart TD
StartSys[Start: App/System Event]:::start
StartSys --> TryBlock[Try: Main Operation]:::calc
TryBlock --> Success[Success: Continue Flow]:::agg
TryBlock -->|Exception| CatchBlock[Catch: Handle Exception]:::warn
CatchBlock --> LogError[Log Error]:::warn
CatchBlock --> UserMsg[Show User Error/Warning]:::warn
UserMsg --> EndSys[End/Error Exit]:::start
Success --> EndSys

%% Edge cases
TryBlock -.-> WarnEdge[Warn: Unhandled Exception]:::warn

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
