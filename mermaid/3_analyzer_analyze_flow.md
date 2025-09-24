
## Analyzer Analyze Flow
This diagram details the flow of the Analyzer component in MetricMancer. It shows how files are grouped, analyzed for churn and complexity, and how results are aggregated per repository. Edge cases such as unknown extensions, read errors, and empty files are visualized, with color coding matching the legend.

```mermaid
flowchart TD
StartAnalyze[Start Analyzer analyze files]
StartAnalyze --> GroupFiles[Group files by repo root]
GroupFiles --> RepoLoop[Loop for each repo root]
RepoLoop --> InitRepo[Init RepoInfo]
InitRepo --> Churn[Collect churn data]
Churn --> Complexity[Collect complexity]
Complexity --> FileLoop[Loop for each file]
FileLoop --> AnalyzeFunc[Analyze functions calc complexity]
AnalyzeFunc --> Hotspot[Calc hotspot churn times complexity]
Hotspot --> Grade[Grade file]
Grade --> Hierarchy[Build hierarchical model]
Hierarchy --> FileLoop
FileLoop -- Loop done --> UpdateRepo[Update RepoInfo with all data]
UpdateRepo -- Next repo --> RepoLoop
RepoLoop -- Loop done --> ReturnDict[Return repo_root to RepoInfo]
ReturnDict --> ReportGen[ReportGenerator]
ReportGen --> EndNode[End]

%% Edge cases
StartAnalyze -.-> WarnExt[Warn unknown extension]
AnalyzeFunc -.-> WarnRead[Warn read error]
FileLoop -.-> WarnEmpty[Warn empty file]

%% Färgkodning
style StartAnalyze fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#212121
style EndNode fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#212121
style Churn fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a237e
style Complexity fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a237e
style Hotspot fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a237e
style RepoLoop fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121
style FileLoop fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121
style GroupFiles fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121
style Hierarchy fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style UpdateRepo fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style ReturnDict fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style WarnExt fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c
style WarnRead fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c
style WarnEmpty fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c
%% Error handling: empty files, missing attributes, exceptions in KPI analyzers

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
