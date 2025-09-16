# Scanner Flow

[← Back to Overview](1_overview.md)

**Related diagrams:**
- [Overview](1_overview.md)
- [App Run Flow](2_app_run_flow.md)
- [Analyzer Analyze Flow](3_analyzer_analyze_flow.md)
- [HTML Report Flow](4_html_report_flow.md)
- [CLI Report Flow](5_cli_report_flow.md)
- [ReportGenerator Flow](6_report_generator_flow.md)

```mermaid
graph TD
    A[Start: Scanner] --> B[Receive directories]
    B --> C[Iterate directories]
    C --> D[Find files in directory]
    D --> E[Filter files by type]
    E --> F[Collect file paths]
    F --> G[Return file list]

    %% Edge cases
    style D fill:#e0f7fa,stroke:#00796b,stroke-width:2px
    style E fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    %% Error handling: empty directory, permission error, no files found
```
