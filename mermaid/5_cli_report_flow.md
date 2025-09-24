
## CLI Report Flow
This diagram illustrates the CLI report generation flow in MetricMancer, including analysis, format selection, and output to terminal or CSV. It also shows error handling for unsupported formats and output errors, using the standard color coding and legend.

```mermaid
flowchart TD
StartCLI[Start MetricMancerApp run]
StartCLI --> Analyze[Analyzer analyze files]
Analyze --> CLIGen[CLIReportGenerator generate]
CLIGen --> FormatSel{Output format}
FormatSel -- human --> PrintReport[CLIReportFormat print report]
FormatSel -- machine --> PrintCSV[CLICSVReportFormat print report]
FormatSel -- other --> RaiseExc[Raise exception]
PrintReport --> ToTerminal[Report to terminal tree]
PrintCSV --> ToCSV[Report to terminal CSV]
RaiseExc --> ErrorMsg[Error message]
ToTerminal --> EndNode[End]
ToCSV --> EndNode
ErrorMsg --> EndNode
%% Edge cases and error handling can be added as needed
style StartCLI fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#212121
style EndNode fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#212121
style Analyze fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a237e
style CLIGen fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121
style FormatSel fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121
style PrintReport fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style PrintCSV fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style ToTerminal fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style ToCSV fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style RaiseExc fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c
style ErrorMsg fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c

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
