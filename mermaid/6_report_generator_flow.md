
# ReportGenerator Flow

[← Back to Overview](1_overview.md)

**Related diagrams:**
- [Overview](1_overview.md)
- [App Run Flow](2_app_run_flow.md)
- [Analyzer Analyze Flow](3_analyzer_analyze_flow.md)
- [HTML Report Flow](4_html_report_flow.md)
- [CLI Report Flow](5_cli_report_flow.md)

```mermaid
graph TD
    A[Start: ReportGenerator] --> B[Select report format]
    B --> C1[CLIReportGenerator]
    B --> C2[HTMLReportGenerator]
    B --> C3[JSONReportGenerator]
    C1 --> D1[Generate CLI report]
    C2 --> D2[Generate HTML report]
    C3 --> D3[Generate JSON report]

    D1 --> E1[Output to terminal]
    D2 --> E2[Output to HTML file]
    D3 --> E3[Output to JSON file]
    E1 --> End[End]
    E2 --> End
    E3 --> End

    %% Edge cases
    style B fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style C1 fill:#e0f7fa,stroke:#00796b,stroke-width:2px
    style C2 fill:#ffe0b2,stroke:#e65100,stroke-width:2px
    style C3 fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    %% Error handling: unknown format, output errors
```
