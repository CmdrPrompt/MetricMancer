
## ReportGenerator Flow
This diagram summarizes the flow of the ReportGenerator component, including format selection, report generation for CLI, HTML, and JSON, and error handling for unknown formats. The color coding and legend are consistent with the rest of the documentation.

```mermaid
graph TD
    A[Start: ReportGenerator] --> B{Select report format}
    B -- CLI --> C1[CLIReportGenerator.generate]
    B -- HTML --> C2[HTMLReportGenerator.generate]
    B -- JSON --> C3[JSONReportGenerator.generate]
    B -- Unknown --> F[Raise exception]
    C1 --> D1[Output to terminal]
    C2 --> D2[Output to HTML file]
    C3 --> D3[Output to JSON file]
    D1 --> End[End]
    D2 --> End
    D3 --> End
    F --> End

    %% Edge cases
    classDef start fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#212121;
    classDef loop fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121;
    classDef calc fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a237e;
    classDef agg fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c;
    classDef warn fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c;

    class A start;
    class B loop;
    class C1 agg;
    class C2 agg;
    class C3 agg;
    class F warn;
    class D1 calc;
    class D2 calc;
    class D3 calc;
    class End start;
    class F warn;
    %% Error handling: unknown format, output errors
    
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
