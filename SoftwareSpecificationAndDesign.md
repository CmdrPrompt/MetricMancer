
# Requirements and Design

## Table of Contents

- [Requirements and Design](#requirements-and-design)
  - [Table of Contents](#table-of-contents)
  - [1. Introduction](#1-introduction)
  - [2. Glossary](#2-glossary)
    - [2.1. KPI Extension and Implementation Status](#21-kpi-extension-and-implementation-status)
  - [3. System Overview](#3-system-overview)
    - [3.1. Application Overview](#31-application-overview)
    - [3.2. Architecture](#32-architecture)
      - [3.2.1. Scanner Flow](#321-scanner-flow)
      - [3.2.2. App Run Flow](#322-app-run-flow)
      - [3.2.3. Analyzer Analyze Flow](#323-analyzer-analyze-flow)
      - [3.2.4. ReportGenerator Flow](#324-reportgenerator-flow)
      - [3.2.5. HTML Report Flow](#325-html-report-flow)
      - [3.2.6. CLI Report Flow](#326-cli-report-flow)
    - [3.3. Data Model](#33-data-model)
      - [3.3.1. UML Diagram](#331-uml-diagram)
  - [4. Detailed Requirements](#4-detailed-requirements)
    - [4.1 User Stories](#41-user-stories)
      - [4.1.1 Persona 1: Alice – The Senior Developer](#411-persona-1-alice--the-senior-developer)
      - [4.1.2 Persona 2: Bob – The DevOps Engineer](#412-persona-2-bob--the-devops-engineer)
      - [4.1.3 Persona 3: Carol – The Engineering Manager](#413-persona-3-carol--the-engineering-manager)
      - [4.1.4 Persona 4: Dave – The New Team Member](#414-persona-4-dave--the-new-team-member)
      - [4.1.5 Persona 5: Sam – The Software Quality Assurance Manager (SQAM)](#415-persona-5-sam--the-software-quality-assurance-manager-sqam)
      - [4.1.6 Persona 6: Erin – The Software Quality Assurance Engineer (SQAE)](#416-persona-6-erin--the-software-quality-assurance-engineer-sqae)
      - [4.1.7 Persona 7: Mia – The Executive Manager](#417-persona-7-mia--the-executive-manager)
    - [4.2 Functional Requirements](#42-functional-requirements)
      - [4.2.1 Core Functional Requirements](#421-core-functional-requirements)
        - [FR1: Calculate complexity](#fr1-calculate-complexity)
        - [FR2: Calculate churn](#fr2-calculate-churn)
      - [4.3.2 Mapping: Requirements to User Stories](#432-mapping-requirements-to-user-stories)
      - [4.3.3 Mapping: Requirements to test cases](#433-mapping-requirements-to-test-cases)
    - [5. Requirement Prioritization \& Risk Management](#5-requirement-prioritization--risk-management)
    - [6. Validation \& Verification](#6-validation--verification)
    - [7. Change Management](#7-change-management)
    - [8. Process \& Methodology](#8-process--methodology)

## 1. Introduction

[ToC](#table-of-contents)

MetricMancer is a software analytics tool designed to provide actionable insights into code quality, maintainability, and technical risk. Inspired by the principles and techniques from "Your Code as a Crime Scene" by Adam Tornhill, the project analyzes source code repositories to extract key performance indicators (KPIs) such as cyclomatic complexity, code churn, and hotspots.

The tool supports multi-language analysis and can generate reports in several formats, including CLI, HTML, and JSON. JSON reports are designed for integration with OpenSearch and dashboards. MetricMancer is built for extensibility, making it easy to add new metrics or adapt the tool to different codebases. The goal is to help teams identify refactoring candidates, monitor code health trends, and prioritize technical debt reduction—using real data from version control history and static analysis.

## 2. Glossary

[ToC](#table-of-contents)

**Temporal Coupling:**
Measures how often two or more files change together in the same commit. High temporal coupling can indicate hidden dependencies or poor modular design. *(Not implemented)*

**Change Coupling:**
Similar to temporal coupling but at the function level: which functions often change together? *(Not implemented)*

**Author Churn / Knowledge Map:**
Measures how many different developers have modified a file or module. Files with many different authors can be harder to maintain and have a higher risk of bugs. *(Not implemented)*

**Code Ownership:**
The proportion of code written by each developer. Low ownership can indicate a risk of knowledge spread or maintenance issues. *(Not implemented)*

**Defect Density:**
The number of bugs or defect reports linked to a file or module, often in relation to churn or complexity. *(Not implemented)*

**Hotspot Evolution:**
How do hotspots change over time? Do they grow, shrink, or remain stable? *(Not implemented)*

**Complexity Trend:**
Tracks whether the complexity of a file or module increases or decreases over time. *(Not implemented)*

**Code Age:**
How old is the code in a file or module? Newer code can be more unstable. *(Not implemented)*

**Test Coverage:**
The proportion of code covered by automated tests, ideally in relation to hotspots and churn. *(Not implemented)*

**Logical Coupling:**
Files or modules that often change together, even if they are not directly dependent in the code. *(Not implemented)*

**KPI (Key Performance Indicator):**
A measurable indicator used to evaluate code quality, maintainability, and risk. Examples: cyclomatic complexity, code churn, hotspots. (See "Your Code as a Crime Scene" for definitions and usage.)

**Cyclomatic Complexity:**
A measure of the logical complexity of a function/method, based on the number of independent paths through the code. High complexity indicates increased maintenance cost and testability risk. (Crime Scene: Chapter 2)

**Code Churn:**
The number of changes (commits) that have affected a file or function over time. High churn can indicate unstable or risky code. (Crime Scene: Chapter 3)

**Hotspot:**
A code section (file or function) that combines high complexity and high churn, making it a prioritized candidate for refactoring. (Crime Scene: Chapter 4)

**ScanDir:**
A node in the directory tree representing a directory and its contents, including aggregated KPIs. (Crime Scene: Chapter 5)

**RepoInfo:**
The root node in the analysis, representing an entire repository including metadata and KPIs at the repo level. (Crime Scene: Chapter 5)

**File:**
A single file in the analysis, with associated KPIs and analysis data. (Crime Scene: Chapter 5)

**Hotspot Score:**
A composite metric calculated as cyclomatic complexity × churn, used to identify risk zones in the code. (Crime Scene: Chapter 4)

**LOC (Lines of Code):**
The number of lines of code in a file or function. Used as a basis for several KPIs. (Crime Scene: Chapter 2)

**Parser:**
A component that parses source code to extract metric data, e.g., complexity or functions. (Crime Scene: Chapter 2)

**Dashboard:**
A visual overview of KPI results, often with charts and color coding to quickly identify risks. (Crime Scene: Chapter 6)

**Crime Scene Principles:**
The methodology and analysis models from the book "Your Code as a Crime Scene" by Adam Tornhill, which form the basis for the definitions and interpretations of KPIs in this project.

### 2.1. KPI Extension and Implementation Status

[ToC](#table-of-contents)

The following table summarizes the available and planned KPIs in MetricMancer, their implementation status, and extensibility notes:

| KPI Name                | Description                                                                 | Status           | Extensibility Notes                                  |
|-------------------------|-----------------------------------------------------------------------------|------------------|------------------------------------------------------|
| Cyclomatic Complexity   | Logical complexity of a function/method (McCabe)                             | Implemented      | New languages can be added via parser modules         |
| Code Churn              | Number of commits affecting a file/function                                  | Implemented      | Extendable to function-level churn with AST support   |
| Hotspot Score           | Composite: complexity × churn                                                | Implemented      | Thresholds/configuration can be adjusted              |
| Temporal Coupling       | How often files change together                                              | Not implemented  | Requires commit history analysis                      |
| Change Coupling         | How often functions change together                                          | Not implemented  | Requires fine-grained commit analysis                 |
| Author Churn/Knowledge Map | Number of unique authors per file/module                                  | Not implemented  | Needs author extraction from VCS                      |
| Code Ownership          | Proportion of code by each developer                                         | Not implemented  | Needs author and LOC analysis                         |
| Defect Density          | Number of bugs/defects per file/module                                       | Not implemented  | Needs integration with issue tracker                  |
| Hotspot Evolution       | How hotspots change over time                                                | Not implemented  | Requires historical KPI tracking                      |
| Complexity Trend        | Complexity increase/decrease over time                                       | Not implemented  | Requires historical analysis                          |
| Code Age                | Age of code in file/module                                                   | Not implemented  | Needs commit date analysis                            |
| Test Coverage           | Proportion of code covered by tests                                          | Not implemented  | Needs integration with test tools                     |
| Logical Coupling        | Files/modules that change together without direct dependency                 | Not implemented  | Requires commit and dependency analysis               |

To add a new KPI, implement a new KPI calculator module and register it in the configuration. The system is designed for easy extension with minimal coupling between components.

## 3. System Overview

[ToC](#table-of-contents)

MetricMancer is structured as a modular, layered system to maximize flexibility, maintainability, and extensibility. The architecture is divided into several key components:

- **Scanner:** Traverses the repository, identifies source files, and excludes hidden or irrelevant directories/files.
- **Parser:** Language-specific modules that extract functions, classes, and structural information from source files.
- **KPI Calculators:** Independent modules that compute metrics such as cyclomatic complexity, code churn, and hotspot scores. Each KPI is encapsulated as an object with its own calculation logic and metadata.
- **Data Model:** Central classes (e.g., RepoInfo, ScanDir, File) represent the hierarchical structure of the repository and aggregate KPI results at each level.
- **Report Generators:** Modules for producing output in various formats, including CLI, HTML, and JSON. These generators consume the data model and present results for different audiences and integrations.
- **Configuration & Extensibility:** The system is designed to allow easy addition of new languages, KPIs, or report formats by implementing new modules and registering them in the configuration.

The architecture supports both batch and incremental analysis, and is suitable for integration into CI/CD pipelines. By separating scanning, parsing, metric calculation, and reporting, MetricMancer enables teams to extend or adapt the tool to their specific needs with minimal coupling between components.

### 3.1. Application Overview

[ToC](#table-of-contents)

```mermaid
graph TD
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

**Figure: Application Overview.**
This diagram shows the high-level architecture and main data flow in MetricMancer. The application starts with the `MetricMancerApp`, which delegates scanning to the `Scanner`. The scanner produces a list of files, which are analyzed by the `Analyzer` using various KPI analyzers (e.g., code churn, complexity, hotspots). The results are aggregated into `RepoInfo` objects and passed to the `ReportGenerator`, which can output reports in CLI, HTML, or JSON format. Error and edge case handling is integrated throughout the process.

### 3.2. Architecture

#### 3.2.1. Scanner Flow

[ToC](#table-of-contents)

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

**Figure: Scanner Flow.**
This diagram details the scanning process. The scanner receives a list of directories, iterates through them, finds files, filters them by type, collects file paths, and returns the final file list. Edge cases such as empty directories, permission errors, and no files found are handled explicitly.

#### 3.2.2. App Run Flow

[ToC](#table-of-contents)

```mermaid
graph TD
  A[Start: MetricMancerApp run] --> B[Scanner scan directories]
  B --> C[Files scanned list]
  C --> D[Analyzer analyze files]
  D --> E[Summary per repo ready RepoInfo object]
  E --> F{Multiple repos?}
  F -- Yes --> G[Create report links for cross-linking]
  G --> H[Loop through each repo_info]
  F -- No --> H

  subgraph Report_generation_per_repo
    H --> I{Report format?}
    I -- HTML --> J[HTMLReportFormat/ReportGenerator generate]
    I -- CLI --> K[CLIReportGenerator generate]
  end

  J --> L[HTML report created]
  K --> M[CLI report in terminal]
  J -- Next repo --> H
  K -- Next repo --> H
  H -- Loop done --> N[End]

  %% Edge cases
  style B fill:#e0f7fa,stroke:#00796b,stroke-width:2px
  style D fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
  style I fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
  %% Error handling: empty directories, errors in scanner/analyzer, report generator
```

**Figure: App Run Flow.**
This diagram illustrates the main execution flow of the application. After scanning directories, files are analyzed and summarized per repository. For each repository, the appropriate report format is selected and generated. The flow handles multiple repositories and includes error handling for empty directories and failures in scanning, analysis, or report generation.

#### 3.2.3. Analyzer Analyze Flow

[ToC](#table-of-contents)

```mermaid
graph TD
  A[Start: Analyzer analyze files] --> B[Group files per repo root]
  B --> C[Loop through each repo root]

  subgraph Analysis_per_repo
    C --> D[Init RepoInfo object]
    D --> E[Collect Churn data CodeChurnAnalyzer]
    E --> F[Collect Complexity ComplexityAnalyzer]
    F --> G[Loop through files for detail analysis]
    G --> H[Analyze functions and complexity per file]
    H --> I[Calculate Hotspot churn times complexity]
    I --> J[Grade file]
    J --> K[Summarize results per language and directory]
    K --> G
    G -- Loop done --> L[Update RepoInfo with all data]
  end

  L -- Next repo --> C
  C -- Loop done --> M[Return summary of all RepoInfo objects]
  M --> RG[ReportGenerator]
  RG --> N[End]

  %% Edge cases
  style E fill:#e0f7fa,stroke:#00796b,stroke-width:2px
  style F fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
  style H fill:#ffe0b2,stroke:#e65100,stroke-width:2px
  %% Error handling: empty files, missing attributes, exceptions in KPI analyzers
```

**Figure: Analyzer Analyze Flow.**
This diagram describes how the analyzer processes files. Files are grouped per repository root, and for each repo, churn and complexity are collected, detailed analysis is performed per file, and hotspot scores are calculated. Results are summarized and aggregated into `RepoInfo` objects, which are then passed to the report generator. Edge cases such as empty files and exceptions in KPI analyzers are handled.

#### 3.2.4. ReportGenerator Flow

[ToC](#table-of-contents)

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

**Figure: ReportGenerator Flow.**
This diagram shows how the report generator selects the output format (CLI, HTML, or JSON), generates the report, and outputs it to the appropriate destination. It also highlights error handling for unknown formats and output errors.

#### 3.2.5. HTML Report Flow

[ToC](#table-of-contents)

```mermaid
graph TD
  A[Start: ReportGenerator generate] --> B[Init HTMLReportFormat]
  B --> C[HTMLReportFormat print_report]
  C --> D[Init ReportRenderer Jinja2]
  D --> E[ReportRenderer render]
  E --> F[Collect and filter files/problem files]
  F --> G[Render HTML with template]
  G --> H[ReportWriter write_html]
  H --> I[End: HTML report created]

  %% Edge cases
  style D fill:#e0f7fa,stroke:#00796b,stroke-width:2px
  style F fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
  style H fill:#ffe0b2,stroke:#e65100,stroke-width:2px
  %% Error handling: missing template, write error, empty repo_info/problem files
```

**Figure: HTML Report Flow.**
This diagram details the process of generating an HTML report. The report generator initializes the HTML format, prints the report, uses the renderer to prepare data, and writes the final HTML file. Edge cases include missing templates, write errors, and empty analysis results.

#### 3.2.6. CLI Report Flow

[ToC](#table-of-contents)

```mermaid
graph TD
  A[Start: MetricMancerApp run] --> B[Analyzer analyze files]
  B --> C[CLIReportGenerator generate]
  C --> D{output format?}
  D -- human --> E[CLIReportFormat print_report]
  D -- machine --> F[CLICSVReportFormat print_report]
  D -- other --> G[Raise exception]
  E --> H[Report written to terminal tree structure]
  F --> I[Report written to terminal CSV]
  G --> J[Error message]
  H --> K[End]
  I --> K
  J --> K

  %% Edge cases
  style D fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
  style G fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px
  %% Error handling: unknown format, empty analysis, terminal error
```

**Figure: CLI Report Flow.**
This diagram shows the flow for generating CLI reports. After analysis, the CLI report generator selects the output format (human-readable or CSV), prints the report, and handles errors such as unknown formats or empty analysis results.

### 3.3. Data Model

[ToC](#table-of-contents)

The MetricMancer data model is designed to represent the hierarchical structure of a source code repository and to aggregate KPI results at each level. The main classes are:

**BaseKPI**
Represents a single key performance indicator (KPI) calculated for a function, file, directory, or repository. All specific KPIs (e.g., Cyclomatic Complexity, Code Churn, Hotspot Score) inherit from this base class.

- Fields:
  - `name`: Name of the KPI (e.g., "Cyclomatic Complexity")
  - `description`: Short description of what the KPI measures
  - `value`: The calculated value for this KPI (type depends on the KPI)
- Functional requirements:
  - Store the KPI's name, description, and value
  - Provide a consistent interface for all KPIs, enabling aggregation and reporting
  - Allow extension for new KPIs by subclassing and implementing custom calculation logic

**Function**
Represents a single function or method within a file.

- Fields:
  - `name`: Name of the function or method
  - `kpis`: Dictionary of KPIs for the function (`Dict[str, BaseKPI]`)
- Functional requirements:
  - Store the function's name
  - Store KPIs relevant to the function (e.g., complexity, churn)

**File**
Represents a single file that has been analyzed.

- Fields:
  - `name`: Name of the file
  - `file_path`: Relative path from the parent directory
  - `kpis`: Dictionary of KPIs for the file (`Dict[str, BaseKPI]`)
  - `functions`: List of functions in the file (`List[Function]`)
- Functional requirements:
  - Store the file's name and relative path
  - Store KPIs relevant to the file (e.g., complexity, churn, LOC, hotspot score)
  - Store a list of analyzed functions with their KPIs
  - Be easy to serialize to JSON and integrate into report structures

**BaseDir**
Base class for directory-like objects.

- Fields:
  - `dir_name`: Name of the directory
  - `scan_dir_path`: Relative path from the repository root

**ScanDir (inherits BaseDir)**
Represents a scanned directory, which can contain files and subdirectories.

- Fields:
  - `files`: Dictionary of files in the directory (`Dict[str, File]`)
  - `scan_dirs`: Dictionary of subdirectories (`Dict[str, ScanDir]`)
  - `kpis`: Dictionary of KPIs aggregated at the directory level (`Dict[str, BaseKPI]`)
- Functional requirements:
  - Store the directory's name and relative path
  - Store a set of files as File objects, indexed by filename
  - Store subdirectories as ScanDir instances, indexed by directory name
  - Store KPIs at the directory level, e.g., average complexity or total churn
  - Support recursive traversal for reporting and visualization

**RepoInfo (inherits ScanDir)**
Represents the top-level object for an analyzed repository, including its structure and KPIs.

- Fields:
  - `repo_root_path`: Absolute path to the repository root
  - `repo_name`: Name of the repository
  - Inherits all fields and behaviors from ScanDir
- Functional requirements:
  - Inherit all fields and behaviors from ScanDir, including recursive directory structure, files, and KPIs
  - Store a unique name for the repository
  - Store the absolute path to the repository root
  - Serve as the top node in the data model and be serializable to JSON, HTML, and other report formats
  - Aggregate KPIs from underlying directories and files for repository-level summaries

#### 3.3.1. UML Diagram

[ToC](#table-of-contents)

![Data model](out/plantuml/datamodel_2025-09-16/datamodel_2025-09-16.png)

## 4. Detailed Requirements

### 4.1 User Stories

[ToC](#table-of-contents)

MetricMancer is intended for software development teams, technical leads, architects, and quality engineers who need actionable insights into code quality and technical debt. Key stakeholders include:

- **Developers:** Use the tool to identify refactoring candidates and monitor code health.
- **Technical Leads/Architects:** Use reports to guide technical debt reduction and architectural improvements.
- **Quality Engineers:** Integrate metrics into CI/CD pipelines and dashboards for continuous monitoring.
- **Managers:** Track trends and risks to inform resource allocation and process improvements.

#### 4.1.1 Persona 1: Alice – The Senior Developer

[ToC](#table-of-contents)

**Background:** Alice is responsible for maintaining a large Python codebase. She is experienced in refactoring and cares about code quality and technical debt.

**User Stories:**

- As a senior developer, I want to quickly identify files with high complexity and churn so that I can prioritize refactoring efforts.
- As a senior developer, I want to see hotspots and risk zones in the codebase so that I can plan technical debt reduction.
- As a senior developer, I want to generate HTML reports to share with my team during code review meetings.

#### 4.1.2 Persona 2: Bob – The DevOps Engineer

[ToC](#table-of-contents)

**Background:** Bob manages CI/CD pipelines and is responsible for integrating quality checks into the build process.

**User Stories:**

- As a DevOps engineer, I want to run MetricMancer as part of the CI pipeline so that code quality metrics are always up to date.
- As a DevOps engineer, I want to export JSON reports so that I can feed metrics into dashboards and monitoring tools.
- As a DevOps engineer, I want to receive alerts if code churn or complexity exceeds certain thresholds.

#### 4.1.3 Persona 3: Carol – The Engineering Manager

[ToC](#table-of-contents)

**Background:** Carol leads a distributed development team and is responsible for long-term code health and resource allocation.

**User Stories:**

- As an engineering manager, I want to track code quality trends over time so that I can identify areas of improvement and measure the impact of technical debt reduction initiatives.
- As an engineering manager, I want to receive summary dashboards and risk reports so that I can prioritize refactoring and allocate resources effectively.
- As an engineering manager, I want to identify files or modules with low code ownership so that I can encourage knowledge sharing and reduce maintenance risk.
- As an engineering manager, I want to correlate code quality metrics with business outcomes (e.g., defect rates, release stability) so that I can justify investments in code quality to stakeholders.
- As an engineering manager, I want to use MetricMancer reports to support planning and decision-making in sprint and release meetings.

#### 4.1.4 Persona 4: Dave – The New Team Member

[ToC](#table-of-contents)

**Background:** Dave recently joined the team and is onboarding to a large, unfamiliar codebase.

**User Stories:**

- As a new team member, I want to use MetricMancer’s reports to find the most complex or risky parts of the code so I can focus my learning.
- As a new team member, I want to see which files are hotspots so I can ask for help or code review when working in those areas.

#### 4.1.5 Persona 5: Sam – The Software Quality Assurance Manager (SQAM)

[ToC](#table-of-contents)

**Background:** Sam oversees the quality assurance strategy for the organization. He is responsible for defining quality standards, ensuring process compliance, and reporting on quality metrics to leadership. Sam coordinates with engineering, QA, and management to drive continuous improvement and risk mitigation.

**User Stories:**

- As a SQAM, I want to use MetricMancer to track organization-wide code quality trends so that I can report on progress and justify quality initiatives to leadership.
- As a SQAM, I want to set and monitor quality gates (e.g., maximum allowed complexity or churn) so that teams are held accountable to quality standards.
- As a SQAM, I want to receive summary dashboards and risk reports from MetricMancer so that I can prioritize audits and allocate resources effectively.
- As a SQAM, I want to correlate MetricMancer metrics with business outcomes (e.g., defect rates, release stability) so that I can demonstrate the value of quality improvements.

#### 4.1.6 Persona 6: Erin – The Software Quality Assurance Engineer (SQAE)

[ToC](#table-of-contents)

**Background:** Erin is responsible for ensuring the overall quality of the software product. She focuses on process compliance, risk identification, and continuous improvement. Erin collaborates with developers, managers, and DevOps to integrate quality metrics and drive quality initiatives.

**User Stories:**

- As a SQAE, I want to integrate MetricMancer into the quality assurance process so that I can monitor code quality trends and enforce quality gates.
- As a SQAE, I want to receive automated reports highlighting files or modules with high risk (e.g., high churn, complexity, or defect density) so that I can proactively address quality issues.
- As a SQAE, I want to correlate code metrics with defect data from issue trackers so that I can identify root causes and recommend targeted improvements.
- As a SQAE, I want to export MetricMancer results to quality dashboards and share them with stakeholders for transparency and compliance.

#### 4.1.7 Persona 7: Mia – The Executive Manager

[ToC](#table-of-contents)

**Background:** Mia is a senior executive responsible for multiple development teams and overall software delivery. She needs high-level insights to support strategic decisions and communicate with stakeholders.

**User Stories:**

- As an executive manager, I want to receive concise, high-level summaries of code quality and technical debt across all projects so that I can make informed decisions and report to upper management or the board.

### 4.2 Functional Requirements

#### 4.2.1 Core Functional Requirements

[ToC](#table-of-contents)

##### FR1: Calculate complexity

The tool shall calculate McCabe cyclomatic complexity for all functions/methods.

**Acceptance Criteria:**

- Complexity is reported for all functions in the report.

##### FR2: Calculate churn

| Req-ID | Type           | Group                    | Name                              | Description                                                                 | Rationale (Why?) | Implementation Status |
|--------|----------------|--------------------------|-----------------------------------|-----------------------------------------------------------------------------|------------------|----------------------|
| FR1    | Functional     | Core Analysis            | Calculate complexity              | The tool shall calculate cyclomatic complexity for all functions/methods.   | Identify complex code and refactoring needs | Implemented |
| FR2    | Functional     | Core Analysis            | Calculate churn                   | The tool shall calculate code churn for all files.                          | Find unstable/risky code | Implemented |
| FR3    | Functional     | Core Analysis            | Identify hotspots                 | The tool shall identify hotspots (high churn × high complexity).            | Focus improvement on risk zones | Implemented |
| FR4    | Functional     | Core Analysis            | Calculate code ownership          | The tool shall calculate code ownership per file.                           | Identify knowledge silos and risk | Planned |
| FR5    | Functional     | Core Analysis            | Calculate shared ownership        | The tool shall calculate shared ownership per file and function, and aggregate shared ownership up through directory/package to repository level. | Identify collaboration, knowledge spread, and risk | Planned |
| FR6    | Functional     | Core Analysis            | Calculate logical coupling        | The tool shall calculate logical coupling between files.                    | Find hidden dependencies | Planned |
| FR7    | Functional     | Core Analysis            | Calculate temporal coupling       | The tool shall calculate temporal coupling between files.                   | Find hidden dependencies | Planned |
| FR8    | Functional     | Core Analysis            | Quality trends                    | The tool shall track and visualize code quality over time.                  | Follow up on improvement work | Planned |
| FR9    | Functional     | Reporting & Visualization| Generate reports                  | The tool shall generate CLI, HTML, and JSON reports.                        | Different audiences and integrations | Implemented |
| FR10   | Functional     | Reporting & Visualization| Visualize KPIs                    | The tool shall visualize KPIs in HTML reports.                              | Facilitate interpretation and communication | Implemented |
| FR11   | Functional     | Reporting & Visualization| Dashboards for management         | The tool shall provide summary dashboards/reports for management.           | Facilitate management decisions | Planned |
| FR12   | Functional     | Reporting & Visualization| Export/integration with dashboards| The tool shall support export/integration with external dashboards.         | Enable further analysis | Planned |
| FR13   | Functional     | Integration & Automation | CI/CD support                     | The tool shall be able to run automatically in CI/CD pipelines.             | Enable continuous quality assurance | Implemented |
| FR14   | Functional     | Integration & Automation | Issue tracker integration         | The tool shall support integration with issue trackers.                     | Link code quality to defects | Planned |
| FR15   | Functional     | Integration & Automation | Alert on thresholds               | The tool shall alert if churn/complexity exceeds thresholds.                | Early warning of risks | Planned |
| FR16   | Functional     | Integration & Automation | Quality gates                     | The tool shall support quality gates (e.g., max churn/complexity).          | Ensure code standards | Planned |
| FR17   | Functional     | Usability & Extensibility| Multi-language support            | The tool shall support analysis of multiple languages in one run.           | Enable analysis of polyglot codebases | Implemented |
| FR18   | Functional     | Usability & Extensibility| Onboarding support                | The tool shall help new developers find complex/risky code.                 | Faster onboarding | Planned |
| FR19   | Functional     | Usability & Extensibility| Recommend knowledge sharing       | The tool shall suggest knowledge sharing for low-ownership files.           | Spread knowledge in the team | Planned |
| NFR1   | Non-Functional | Usability & Extensibility| Performance                       | Analysis of a medium-sized codebase (<10k files) shall take <5 min.         | Enable use in CI and daily operation | Implemented |
| NFR2   | Non-Functional | Usability & Extensibility| Extensibility                     | It shall be easy to add new KPIs and languages.                             | Future-proof and adapt the tool | Planned |
| NFR3   | Non-Functional | Usability & Extensibility| Platforms                         | The tool shall work on Windows, macOS, and Linux.                           | Support all common development environments | Implemented |
| NFR4   | Non-Functional | Usability & Extensibility| Error handling                    | The tool shall provide clear error messages for invalid input.               | Facilitate troubleshooting and usability | Planned |

#### 4.3.2 Mapping: Requirements to User Stories

| Requirement(s)                  | User Story / Persona Description                                 |
|----------------------------------|-----------------------------------------------------------------|
| FR1, FR2, FR3, FR10, FR15, FR18 | [Alice](#411-persona-1-alice--the-senior-developer): Identify complex/risky code, see hotspots, onboarding    |
| FR6, FR11, FR13, FR19, FR21     | [Bob](#412-persona-2-bob--the-devops-engineer): Export reports, dashboards, integration                    |
| FR7, FR15, FR20                 | [Carol](#413-persona-3-carol--the-engineering-manager): Link code quality to defects, trends, business goals     |
| FR4, NFR3                       | [Dave](#414-persona-4-dave--the-new-team-member): Multi-language analysis, platform support                 |
| FR12, NFR1                      | [Sam](#415-persona-5-sam--the-software-quality-assurance-manager-sqam): CI/CD, performance                                        |
| FR14, FR19                      | [Sam](#415-persona-5-sam--the-software-quality-assurance-manager-sqam): Alerts, quality gates                                      |
| FR9, FR10                       | [Erin](#416-persona-6-erin--the-software-quality-assurance-engineer-sqae): Couplings, QA process                                    |
| NFR4                            | All: Error handling                                             |

#### 4.3.3 Mapping: Requirements to test cases

| Requirement | Test Case(s)                                                                                                                        | Status       |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------|--------------|
| FR1         | tests/app/test_complexity_analyzer.py:test_calculate_for_file_success, test_analyze_functions_success, test_calculate_for_file_import_error, test_calculate_for_file_no_parser, test_analyze_functions_attribute_error, test_analyze_functions_no_parser, tests/app/test_complexity_analyzer_edge.py:test_calculate_for_file_empty_config, test_calculate_for_file_import_error, test_calculate_for_file_missing_methods, test_analyze_functions_empty_config, test_analyze_functions_attribute_error, test_analyze_functions_missing_method | Implemented  |
| FR2         | tests/app/test_code_churn_analyzer.py:test_analyze_churn_data, test_init_repo_scan_pairs, test_analyze_handles_exception, tests/app/test_code_churn_analyzer_edge.py:test_empty_repo_scan_pairs, test_find_git_repo_root_none, test_find_git_repo_root_exception, test_analyze_handles_pydriller_exception, test_analyze_no_churn_data | Implemented  |
| FR3         | tests/app/test_hotspot_kpi_edge.py:test_calculate_with_only_complexity, test_calculate_with_only_churn, test_calculate_with_zero, test_calculate_with_none, test_calculate_with_negative | Implemented  |
| FR4         | tests/kpis/test_code_ownership.py:test_calculate_ownership_basic, test_calculate_ownership_error, tests/kpis/test_code_ownership_kpi.py:test_file_does_not_exist, test_file_not_tracked_by_git, test_file_tracked_and_blame_works, test_blame_fails | Implemented  |
| FR5         |  | Planned |
| FR6         | tests/report/test_cli_report_generator.py:test_generate_human_calls_cli_report_format, test_generate_machine_calls_cli_csv_report_format, test_generate_unsupported_format_raises, test_init_sets_attributes, tests/report/test_report_writer.py:test_write_html_creates_file_and_writes_content | Implemented  |
| FR7         | tests/report/test_cli_report_format.py:test_get_repo_stats_with_files, test_get_repo_stats_no_files, test_format_file_stats, test_print_report_runs, tests/report/test_cli_cli_report_format.py:test_get_repo_stats_with_files, test_get_repo_stats_no_files, test_format_file_stats, test_print_report_runs | Implemented  |
| FR8         | tests/report/test_report_renderer.py:test_init_sets_env_and_thresholds, test_collect_all_files_nested, test_render_filters_problem_files_and_renders | Implemented  |
| FR9         | tests/report/test_cli_report_generator.py:test_generate_human_calls_cli_report_format | Implemented  |
| FR10        | tests/app/test_metric_mancer_app.py:test_run_single_repo, test_init_sets_attributes, test_run_multiple_repos | Implemented  |
| FR11        | tests/app/test_tree_printer.py:test_build_tree_single_file, test_build_tree_nested, test_sort_paths, test_split_files_folders, test_sort_items, test_print_tree_output | Implemented  |
| FR12        | tests/app/test_debug.py:test_debug_print_when_debug_false, test_debug_print_when_debug_true | Implemented  |
| FR13        | tests/app/test_scanner.py:test_scan_finds_supported_files, test_scan_multiple_directories, test_scan_ignores_hidden_files_and_dirs, test_scan_ignores_hidden_root_directory, test_scan_handles_non_existent_directory, test_scan_returns_empty_list_for_no_supported_files | Implemented  |
| FR14        | tests/app/test_analyzer.py:test_analyze_structure_and_kpis, test_skips_unsupported_extension_files, test_unreadable_file_is_skipped_and_warned, test_builds_nested_scandir_hierarchy, test_hotspot_kpi_includes_calculation_values, test_zero_functions_results_in_zero_complexity_and_hotspot, test_analyze_empty_list | Implemented  |
| NFR1        | tests/app/test_metric_mancer_app.py:test_run_single_repo, test_init_sets_attributes, test_run_multiple_repos | Implemented  |
| NFR2        | tests/app/test_metric_mancer_app_edge.py:test_run_with_empty_directories, test_run_with_none_report_generator_cls, test_run_with_report_generate_exception | Implemented  |
| NFR3        | tests/app/test_metric_mancer_app_edge.py:test_run_with_empty_directories, test_run_with_none_report_generator_cls, test_run_with_report_generate_exception | Implemented  |

### 5. Requirement Prioritization & Risk Management

[ToC](#table-of-contents)

Requirements are prioritized based on their impact on code quality, maintainability, and user value. Core analysis and reporting features are highest priority. Planned features (e.g., defect density, test coverage) are lower priority and scheduled for future releases.
Risks include:
  
- **Scalability:** Large repositories may impact performance. Mitigated by optimizing algorithms and supporting configuration.
- **Extensibility:** Risk of tight coupling is mitigated by modular architecture and plugin patterns.

### 6. Validation & Verification

Validation and verification are achieved through:
  
- **Automated Unit Tests:** Cover all major modules and KPIs.
- **Acceptance Criteria:** Each requirement includes acceptance notes for testability.
- **Continuous Integration:** Automated tests run on each commit to ensure ongoing quality.

### 7. Change Management

[ToC](#table-of-contents)

Requirements and design changes are managed via version control (Git). All changes are tracked, reviewed, and documented in the changelog. Major changes require stakeholder review and update of requirements tables.
  
### 8. Process & Methodology

[ToC](#table-of-contents)

MetricMancer is developed using an iterative, test-driven approach. The process emphasizes:
  
- **Modular Design:** Enables incremental development and easy extension.
- **Continuous Integration:** Ensures code quality and rapid feedback.
- **Documentation:** Requirements and design are updated alongside code.
- **Open Source Collaboration:** Contributions are reviewed and integrated via pull requests.

```text
```
