## KPI Module Flow

This diagram illustrates the typical flow of a KPI module in MetricMancer, such as CodeChurnAnalyzer, ComplexityAnalyzer, or HotspotAnalyzer. The process starts with receiving file or repository data, proceeds to KPI calculation, and returns the result. Edge cases like missing input or calculation errors are visualized. The color coding and legend match the conventions used throughout the documentation.

```mermaid
flowchart TD
StartKPI[Start KPI calculation]:::start
StartKPI --> Input[Receive file/repo data]:::calc
Input --> Calculate[Calculate KPI value]:::agg
Calculate --> Output[Return KPI result]:::agg
Output --> EndNode[End]:::start

%% Edge cases
Input -.-> WarnInput[Warn: missing/invalid input]:::warn
Calculate -.-> WarnCalc[Warn: calculation error]:::warn

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
