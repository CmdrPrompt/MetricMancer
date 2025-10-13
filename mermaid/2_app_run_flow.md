## App Run Flow (Simplified)
This diagram outlines the main application run flow in MetricMancer, from startup through scanning, analysis (including complexity, churn, ownership, and shared ownership KPIs), and report generation in various formats. It also highlights key edge cases and error handling at each stage, using the standard color coding and legend.

```mermaid
flowchart TD
    StartApp[Start MetricMancerApp run]
    StartApp --> Scan[Scanner scan directories]
    Scan --> Files[Files scanned list]
    Files --> Analyze[Analyzer analyze files]
    Analyze --> RepoInfos[RepoInfo list]
    RepoInfos --> FormatSel{Select report format}
    FormatSel -- HTML --> HTMLGen[HTMLReportGenerator generate]
    FormatSel -- CLI --> CLIGen[CLIReportGenerator generate]
    FormatSel -- JSON --> JSONGen[JSONReportGenerator generate]
    HTMLGen --> HTMLOut[HTML report created]
    CLIGen --> CLIOut[CLI report in terminal]
    JSONGen --> JSONOut[JSON report written]
    HTMLOut --> EndNode[End]
    CLIOut --> EndNode
    JSONOut --> EndNode

    %% Assign classes for color coding (one per line, no trailing commas)
    class StartApp start
    class EndNode start
    class Scan calc
    class Files calc
    class Analyze calc
    class RepoInfos calc
    class FormatSel loop
    class HTMLGen agg
    class CLIGen agg
    class JSONGen agg
    class HTMLOut agg
    class CLIOut agg
    class JSONOut agg
    class WarnScan warn
    class WarnAnalyze warn
    class WarnFormat warn
    class WarnHTML warn
    class WarnCLI warn
    class WarnJSON warn
    class WarnEnd warn

    %% Edge cases and error handling
    Scan -.-> WarnScan[Warn: empty/hidden/permission error]
    Analyze -.-> WarnAnalyze[Warn: analysis error]
    FormatSel -.-> WarnFormat[Warn: unknown format]
    HTMLGen -.-> WarnHTML[Warn: HTML write error]
    CLIGen -.-> WarnCLI[Warn: CLI output error]
    JSONGen -.-> WarnJSON[Warn: JSON write error]
    EndNode -.-> WarnEnd[Warn: incomplete output]

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

    class LegendStart start
    class LegendCalc calc
    class LegendLoop loop
    class LegendAgg agg
    class LegendWarn warn
```
