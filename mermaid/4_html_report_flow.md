
## HTML Report Flow
This diagram shows the flow for generating an HTML report in MetricMancer. It covers initialization, rendering, filtering, and writing the HTML file, as well as cross-linking and potential edge cases. The color coding and legend are consistent with the rest of the documentation.

```mermaid
flowchart TD
StartHTML[Start ReportGenerator generate]
StartHTML --> InitFormat[Init HTMLReportFormat]
InitFormat --> PrintReport[HTMLReportFormat print report]
PrintReport --> InitRenderer[Init ReportRenderer]
InitRenderer --> Render[ReportRenderer render]
Render --> Filter[Collect and filter files]
Filter --> RenderHTML[Render HTML with template]
RenderHTML --> WriteHTML[ReportWriter write html]
WriteHTML --> EndNode[End HTML report created]
PrintReport --> ReportLinks[Report links crosslinking]
%% Edge cases and error handling can be added as needed
style StartHTML fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#212121
style EndNode fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#212121
style InitFormat fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121
style PrintReport fill:#fffde7,stroke:#fbc02d,stroke-width:2px,color:#212121
style InitRenderer fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a237e
style Render fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a237e
style Filter fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style RenderHTML fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style WriteHTML fill:#ede7f6,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
style ReportLinks fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c

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

