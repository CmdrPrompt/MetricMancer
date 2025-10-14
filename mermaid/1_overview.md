

# Overview

- [Main Entry Point Flow](13_main_entry_flow.md)
- [Config & CLI Flow](10_config_cli_flow.md)
- [App Run Flow](2_app_run_flow.md)
- [Scanner Flow](7_scanner_flow.md)
- [Analyzer Analyze Flow](3_analyzer_analyze_flow.md)
- [KPI Dependencies & Status](12_kpi_dependencies_status.md)
- [HTML Report Flow](4_html_report_flow.md)
- [CLI Report Flow](5_cli_report_flow.md)
- [JSON Report Flow](8_json_report_flow.md)
- [KPI Module Flow](9_kpi_module_flow.md)
- [System Error Handling](11_system_error_handling_flow.md)

This overview diagram shows the main components and data flows in MetricMancer, from scanning directories to analyzing files and generating reports in different formats. Edge cases and error handling are visualized, and the color coding matches the legend for consistency across all diagrams.

**Note:** MetricMancer now uses the Configuration Object Pattern (see diagram 13) to centralize configuration and reduce code churn. The main entry point flow has been significantly simplified with the Factory Pattern for report generator selection.

```mermaid
flowchart TD
    App[MetricMancerApp]
    App --> Scanner[Scanner]
    Scanner -->|"directories"| Files[File List]
    Files --> Analyzer[Analyzer]
    Analyzer -->|"per repo"| RepoInfos[RepoInfo List]
    Analyzer --> CodeChurn[CodeChurnAnalyzer]
    Analyzer --> Complexity[ComplexityAnalyzer]
    Analyzer --> CodeOwnership[CodeOwnershipKPI]
    Analyzer --> SharedOwnership[SharedOwnershipKPI]
    Analyzer --> Hotspot[HotspotKPI]
    Analyzer -->|"edge cases"| AnalyzerWarn[Warn: unknown ext, read error, empty]
    RepoInfos -->|"loop repos"| ReportGenLoop[Loop: per repo]
    ReportGenLoop --> ReportGenerator[ReportGenerator]
    ReportGenerator -->|"format: CLI"| CLIReport[CLIReportGenerator]
    ReportGenerator -->|"format: HTML"| HTMLReport[HTMLReportGenerator]
    ReportGenerator -->|"format: JSON"| JSONReport[JSONReportGenerator]
    CLIReport --> CLIOutput[CLI Output]
    HTMLReport --> HTMLOutput[HTML File]
    JSONReport --> JSONOutput[JSON File]
    ReportGenerator -->|"cross-linking"| CrossLinks[Report Links]
    ReportGenerator --> ErrorHandling[Error & Edge Case Handling]
    ErrorHandling -.-> App
    Scanner -->|"warn: hidden/empty/perm"| ScannerWarn[Warn: hidden/empty/permission]

    %% Show KPI dependencies
    Hotspot -.->|"uses"| Complexity
    Hotspot -.->|"uses"| CodeChurn
    SharedOwnership -.->|"uses"| CodeOwnership

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

    %% Main node color coding
    class App,CLIOutput,HTMLOutput,JSONOutput start;
    class Scanner,Files,Analyzer,RepoInfos,CodeChurn,Complexity,CodeOwnership,SharedOwnership,Hotspot calc;
    class ReportGenLoop,ReportGenerator loop;
    class CLIReport,HTMLReport,JSONReport,CrossLinks agg;
    class AnalyzerWarn,ScannerWarn,ErrorHandling warn;
```

