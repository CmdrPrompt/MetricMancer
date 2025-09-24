
## Scanner Flow
This diagram describes the flow of the Scanner component in MetricMancer. It covers directory traversal, file filtering, and error handling for hidden files, permissions, and invalid directories. The color coding and legend are consistent with the rest of the documentation.

```mermaid
graph TD
    A[Start: Scanner] --> B[Receive directories]
    B --> C[ThreadPoolExecutor: parallel scan]
    C --> D[Iterate directories]
    D --> E[Skip hidden root dirs]
    E --> F[Find files in directory]
    F --> G[Skip hidden files/dirs]
    G --> H[Filter files by known extension]
    H --> I[Collect file paths]
    I --> J[Return file list]
    D --> K[Warn: not a directory/permission error]
    K --> J

    %% Edge cases
    style F fill:#e0f7fa,stroke:#00796b,stroke-width:2px
    style H fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style K fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px
    %% Error handling: empty directory, permission error, no files found
    
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
