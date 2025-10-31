# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2025-10-31

### Added

- **Multi-Language Cognitive Complexity (v3.2.0)**: Tree-sitter-based cognitive complexity analysis for multiple languages
  - Implemented cognitive complexity calculators for Java, Go, JavaScript, TypeScript, and C
  - Factory pattern for language-specific calculators via `CognitiveComplexityCalculatorFactory`
  - Abstract base class `CognitiveComplexityCalculatorBase` for consistent implementation
  - Refactored Python cognitive complexity calculator to use factory pattern
  - Added 135 comprehensive tests covering all languages and edge cases (total test suite: 839 tests)
  - SonarSource-compatible cognitive complexity rules (nesting penalties, boolean operators, etc.)
  - Integrated cognitive complexity in all report formats (HTML, JSON, CLI, Quick Wins)
  - Dependencies: `tree-sitter>=0.25.0`, `tree-sitter-language-pack>=0.10.0` (migrated from `tree-sitter-languages`)
- **Cognitive Hotspot KPI**: New KPI combining cognitive complexity with code churn
  - File: `src/kpis/hotspot/cognitive_hotspot_kpi.py`
  - Calculates `cognitive_complexity × churn` for identifying complex, frequently-changed code
  - Complements existing cyclomatic complexity-based hotspot analysis
- Improved HTML report templates with cognitive complexity display
- Enhanced JSON report format with cognitive complexity fields

### Fixed

- 17 PEP8 line length violations (E501) across src/ and tests/
- FutureWarning suppression for deprecated tree-sitter Language usage

### Changed

- Cognitive complexity now available for 6 languages: Python, Java, Go, JavaScript, TypeScript, C
- Report generation includes both cyclomatic and cognitive complexity metrics
- Factory pattern replaces conditional logic in cognitive complexity calculation
- **BREAKING**: Migrated from `tree-sitter-languages` to `tree-sitter-language-pack` for better maintainability and official support
  - Users building from source should run `pip install -r requirements.txt` to update dependencies
  - No user-facing functionality changes, but dependency update required for fresh installations

## [3.1.0] - 2025-10-15

### Added

- **Multi-Format Report Generation (v3.1.0)**: Generate multiple report formats in a single analysis run
  - New `--output-formats` CLI parameter (plural) accepting comma-separated format list
  - Example: `--output-formats html,json,summary,review-strategy` generates all formats in one run
  - **NEW:** Support for `review-strategy` and `review-strategy-branch` as output formats
    - `review-strategy`: Generate code review strategy for full repository
    - `review-strategy-branch`: Generate review strategy for changed files only (current branch vs main)
    - Can be combined with other formats: `--output-formats html,json,review-strategy-branch`
  - Eliminates redundant scanning and analysis for multiple formats
  - **Performance improvement**: 50-70% faster than separate runs (scan/analyze once, generate all formats)
  - AppConfig enhanced with `output_formats: List[str]` field and validation for review-strategy formats
  - MetricMancerApp loops over formats, reusing scan/analysis results, special handling for aggregate reports
  - main.py detects multi-format mode and delegates generator creation to app
  - 54 new TDD tests (23 AppConfig + 15 CLI + 9 MetricMancerApp + 7 main.py)
  - Maintains 100% backward compatibility with `--output-format` (singular) and `--review-strategy` flags
  - Implements functional requirement FR9.1 from SSD
  - 445 tests passing with full PEP8 compliance

### Fixed

- Generator selection bug in multi-format mode
- Markdown rendering for box-drawing characters in CLI reports

### Changed

- Default output format remains `summary` for backward compatibility
- All CLI formats use markdown for file output

### Planned / In Development

**Git/Bitbucket-based KPIs:**

- Code Ownership: Measures how many different developers have modified a file. Identifies files with low ownership (high risk for bugs). Can be retrieved via `git log --pretty="%an" <file>`.
- Review Latency: Time from pull request creation to first comment. Highlights bottlenecks in the review process. Retrieved via Bitbucket API: `/pullrequests/{id}/comments`.
- Merge Time: Time from PR creation to merge. Measures collaboration and delivery speed. Bitbucket API: `/pullrequests/{id}` with timestamps.
- Comment Density: Number of comments per PR. Indicator of code review quality. Can be combined with Review Latency for a "Review Health Score".

**Jira-based KPIs:**

- Cycle Time: Time from "In Progress" to "Done". Measures delivery speed. Retrieved via Jira API: `issue.changelog` → status changes.
- Lead Time: Time from issue creation to delivery. Identifies bottlenecks in planning and prioritization.
- Issue Reopen Rate: How often issues are reopened after being closed. Indicator of solution quality and test coverage.
- Sprint Accuracy: Amount of planned work actually delivered. Measures team predictability.
- Flow Efficiency: Active time vs. waiting time in the issue flow. Identifies waste in the process.

**Combined Metric Ideas:**

- Risk Index = churn × complexity × ownership diversity
- Review Health Score = comment density ÷ review latency
- Delivery Score = sprint accuracy × flow efficiency
- Stability Score = low churn × high complexity × low reopen rate

## [2.0.2] - 2025-09-14

### Added

- New HTML report templates: `base.html`, `overview.html`, and `repo.html` for improved report rendering and maintainability.
- Robust, modern CSS and interactive file tree for HTML reports.
- UTF-8 output enforcement for CLI to support Unicode in all environments.

### Changed

- All warning and status messages now use `[WARN]` and `[OK]` prefixes for consistency in CLI and logs.
- Improved path normalization and cross-platform compatibility in code churn and scanner modules.
- Refactored test cases for code churn and scanner to use robust, normalized path comparisons.
- HTML report output now uses `[OK]` instead of emoji for status messages.

### Fixed

- Fixed bug where non-existent directories in scan would not print normalized warning messages.
- Fixed test failures on Windows/macOS due to inconsistent path handling in tests and code.
- Fixed edge cases in code churn analyzer for missing or invalid git roots.

### Removed

- Removed exclusion of `*.html` from `.gitignore` (now tracked for templates).
- Removed redundant/legacy code in test mocks and path handling.

### Security

- No security changes in this release.

### Deprecated

- No deprecations in this release.

## [2.0.1] - 2025-09-14

### Changed
- Updated and deduplicated persona/user story sections in SoftwareSpecificationAndDesign.md for clarity and structure.
- Rebuilt and corrected the Table of Contents to match the current document structure.
- Fixed mermaid diagram rendering by removing extraneous code block markers after mermaid blocks.
- Improved markdown lint compliance (headings, blank lines, link fragments).
- Updated traceability matrices and requirements tables for accuracy.
- README.md updated to reference the latest SSD structure and KPI definitions.

## [2.0.0] - 2025-09-14

### Added
- Major documentation overhaul: new Software Specification and Design (SSD) document with full requirements, architecture, data model, KPIs, traceability, and user stories/personas.
- HTML, CLI, and JSON report generators now fully modular and extensible.
- Aggregated KPIs at file, directory, and repository levels.
- Hotspot analysis: highlights files/functions with both high complexity and high churn.
- Robust error and edge case handling throughout the analysis and reporting pipeline.
- Test traceability: requirements mapped to test cases in documentation.
- User stories and personas included for stakeholder clarity.
- Mermaid and PlantUML diagrams for architecture and data model.
- Improved English language consistency and markdown lint compliance across all documentation.
- Link to SSD document added in README.md; README fully updated to match current state and SSD.

### Changed
- Refactored codebase for extensibility: new KPI modules, parser modules, and report format modules are pluggable.
- Improved CLI and HTML report output: clearer summaries, better error messages, and more actionable insights.
- Updated requirements and non-functional requirements to reflect current and planned features.
- Updated all documentation to follow Keep a Changelog and Semantic Versioning best practices.

### Fixed
- Fixed markdown lint errors in documentation and README.
- Fixed section numbering and formatting in SSD document.
- Fixed test robustness for edge cases and error handling.

### Removed
- Removed outdated/duplicate documentation and legacy report templates.

### Security
- No security changes in this release.

### Deprecated
- No deprecations in this release.

## [Unreleased]

### Planned / In Development

**Git/Bitbucket-based KPIs:**

- Code Ownership: Measures how many different developers have modified a file. Identifies files with low ownership (high risk for bugs). Can be retrieved via `git log --pretty="%an" <file>`.
- Review Latency: Time from pull request creation to first comment. Highlights bottlenecks in the review process. Retrieved via Bitbucket API: `/pullrequests/{id}/comments`.
- Merge Time: Time from PR creation to merge. Measures collaboration and delivery speed. Bitbucket API: `/pullrequests/{id}` with timestamps.
- Comment Density: Number of comments per PR. Indicator of code review quality. Can be combined with Review Latency for a "Review Health Score".

**Jira-based KPIs:**

- Cycle Time: Time from "In Progress" to "Done". Measures delivery speed. Retrieved via Jira API: `issue.changelog` → status changes.
- Lead Time: Time from issue creation to delivery. Identifies bottlenecks in planning and prioritization.
- Issue Reopen Rate: How often issues are reopened after being closed. Indicator of solution quality and test coverage.
- Sprint Accuracy: Amount of planned work actually delivered. Measures team predictability.
- Flow Efficiency: Active time vs. waiting time in the issue flow. Identifies waste in the process.

**Combined Metric Ideas:**

- Risk Index = churn × complexity × ownership diversity
- Review Health Score = comment density ÷ review latency
- Delivery Score = sprint accuracy × flow efficiency
- Stability Score = low churn × high complexity × low reopen rate

## [1.2.0] - 2025-08-31

### Added
- CLI report now lists files in the root directory before all folders, improving readability of file trees.
- Debug output is now controlled by the debug flag for all CLI and app runs.
- Repo root name detection in CLI report is now accurate and robust.

### Changed
- Major refactoring: moved core modules to subfolders (`app`, `languages`, etc.) for better structure and maintainability.
- `collector.py`, `scanner.py`, and `config.py` relocated to logical subfolders; all imports updated accordingly.
- Improved modularity and separation of concerns throughout the codebase.
- All test files and mocks updated to reflect new module structure.

### Fixed
- Indentation and import errors in several modules after refactoring.
- All tests and CLI runs validated after each change to ensure stability.

### Removed
- Old/duplicate files in root (`collector.py`, `scanner.py`, `app.py`, `config.py`) deleted after migration to subfolders.

### Security
- No security changes in this release.

### Deprecated
- No deprecations in this release.

## [1.1.1] - 2025-08-31

### Fixed

- CI workflow now fetches full git history to prevent test failures on shallow clones.
- Tests for code churn and git operations now mock `pydriller.Repository` to avoid failures when git history is missing.
- All tests are robust to missing commits and run reliably in CI environments.

### Changed

- Updated dependencies in `pyproject.toml` for coverage and CI stability.

## [1.1.0] - 2025-08-30

### Added (features)

- Cyclomatic complexity support for Ada, C, C++, Go.
- Modular parser interface for all supported languages.
- Unittest test cases for all language parsers.
- Dynamic parser loading via config.
- GitHub Actions workflow now builds and tests all branches.

### Changed (codebase improvements)

- Refactored codebase for maintainability and testability.
- Improved Ada parser to avoid double-counting control keywords.
- Cleaned up template directories; only `src/templates` is used.

### Removed

- Deleted unused `templates/` folder from project root.

## [1.0.0] - 2025-08-30

### Added (initial release)

- Initial public release of ComplexityScanner.
- Cyclomatic complexity scanning for the following programming languages:
  - Python
  - JavaScript
  - TypeScript
  - Java
  - C#
- HTML report generation with summary and per-folder statistics.
- Support for thresholds and problematic file highlighting.
- SBOM generation instructions and workflow for GitHub Actions.
