

# Overview

- [App Run Flow](2_app_run_flow.md)
- [Scanner Flow](7_scanner_flow.md)
- [Analyzer Analyze Flow](3_analyzer_analyze_flow.md)
- [ReportGenerator Flow](6_report_generator_flow.md)
- [HTML Report Flow](4_html_report_flow.md)
- [CLI Report Flow](5_cli_report_flow.md)

```mermaid
flowchart TD
    App[MetricMancerApp] --> Scanner[Scanner]
    Scanner -->|"directories"| Files[File List]
    Files --> Analyzer[Analyzer]
    Analyzer -->|"per repo"| RepoInfo[RepoInfo Objects]
    Analyzer --> CodeChurn[CodeChurnAnalyzer]
    Analyzer --> Complexity[ComplexityAnalyzer]
    Analyzer --> Hotspot[HotspotAnalyzer]
    RepoInfo --> ReportGenerator[ReportGenerator]
    ReportGenerator -->|"format: CLI"| CLIReport[CLIReportGenerator]
    ReportGenerator -->|"format: HTML"| HTMLReport[HTMLReportGenerator]
    CLIReport --> CLIOutput[CLI Output]
    HTMLReport --> HTMLOutput[HTML File]
    ReportGenerator -->|"format: JSON"| JSONReport[JSONReportGenerator]
    JSONReport --> JSONOutput[JSON File]
    ReportGenerator --> ErrorHandling[Error & Edge Case Handling]
    ErrorHandling -.-> App

```
