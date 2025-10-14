# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2025-10-14

### Added

- **Configuration Object Pattern**: Centralized configuration with AppConfig dataclass
  - Type-safe configuration with automatic validation
  - Single source of truth for all application settings
  - Factory method `AppConfig.from_cli_args()` for easy creation
  - 18 configuration fields with sensible defaults
  - Eliminated config file dependency
- **Factory Pattern**: ReportGeneratorFactory for report creation
  - Eliminates conditional logic in main.py
  - Easy addition of new report formats
  - Automatic generator selection based on format
  - Single responsibility for generator creation
- **Enhanced Architecture Documentation**: Comprehensive architecture documentation
  - `ARCHITECTURE.md`: 752 lines covering SOLID principles, design patterns, component architecture
  - `MIGRATION_GUIDE.md`: 428 lines with step-by-step migration instructions, scenarios, and FAQ
  - Updated `README.md` with Configuration Object Pattern section
- **Visual Documentation**: PlantUML and Mermaid diagrams
  - New PlantUML architecture diagram showing Configuration Object and Factory patterns
  - Updated Mermaid flow diagrams (main entry, config flow, system overview)
  - Comprehensive diagram documentation and indexes
- **Enhanced Testing**: Comprehensive test coverage for new patterns
  - Tests for AppConfig creation and validation
  - Tests for Factory Pattern
  - Tests for main.py error handling
  - 390 tests passing with >80% coverage
- **Code Review Strategy**: New `--review-strategy` feature generates data-driven code review recommendations
  - Risk classification (Critical, High, Medium, Low) based on complexity, churn, and ownership
  - Estimated review time per file based on metrics
  - Priority-based file lists with focus areas and checklists
  - Review templates for different risk levels
  - Resource allocation guidance
- **Branch-based Review Filtering**: New `--review-branch-only` flag to focus reviews on changed files
  - `--review-base-branch` option to specify comparison branch (default: main)
  - Shows current branch and base branch in report
  - Filters review strategy to only files changed in current branch
- **Enhanced Language Support**: Added complexity parsers for configuration and script files
  - **IDL (Interface Definition Language)**: Structural complexity for CORBA/COM interfaces (interfaces, operations, structs, unions, exceptions, inheritance)
  - **JSON**: Structural complexity (nesting depth, objects, arrays, keys)
  - **YAML**: Structural complexity + YAML-specific features (anchors, aliases, multi-line strings)
  - **Shell Scripts**: Cyclomatic complexity (control flow, loops, functions, logical operators)
- **Hotspot Analysis Interpretation Guide**: Added comprehensive guide to hotspot analysis reports
  - Hotspot score classification thresholds
  - Complexity thresholds with recommendations
  - Code churn thresholds with actions
  - Recommended actions by category
- **Complete Review Checklists**: Review strategy now shows all checklist items (no truncation)
- New documentation:
  - `docs/code_review_strategy.md`: Complete guide for code review strategy feature
  - `docs/language_support.md`: Comprehensive language and file type support matrix
  - `docs/future_enhancements.md`: Delta-based complexity analysis planning

### Changed

- **main.py Refactored**: Simplified main entry point
  - 17% complexity reduction (from 12 to 10)
  - 60-80% churn reduction through stable patterns
  - Eliminated config file loading logic
  - Eliminated conditional report generator selection
  - Uses dependency injection for MetricMancerApp
- **Improved Extensibility**: Factory Pattern makes it easier to add new report formats
- **Better Error Handling**: Configuration validation happens automatically at creation time
- **Test Quality**: Removed 11 legacy skipped tests, kept 6 critical behavior tests
- Review strategy checklists now display all items instead of truncating after 5
- Updated language support from 9 to 13 file types (added IDL, JSON, YAML, Shell)
- Enhanced git helpers with branch comparison functions

### Documentation

- Added comprehensive architecture documentation (ARCHITECTURE.md, MIGRATION_GUIDE.md)
- Updated SoftwareSpecificationAndDesign.md with new patterns and requirements
- Added PlantUML architecture diagrams
- Updated Mermaid flow diagrams
- Added document versioning and changelog to SSD
- Cross-referenced all major documentation

### Dependencies

- Added `PyYAML` for YAML file parsing and complexity analysis

### Technical Debt

- Reduced main.py cyclomatic complexity by 17%
- Reduced main.py churn by 60-80%
- Improved SOLID principles adherence
- Better separation of concerns
- More testable architecture

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

...existing code...
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
