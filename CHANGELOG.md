# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-08-31

### Fixed

- CI workflow now fetches full git history to prevent test failures on shallow clones.
- Tests for code churn and git operations now mock `pydriller.Repository` to avoid failures when git history is missing.
- All tests are robust to missing commits and run reliably in CI environments.

### Changed

- Updated dependencies in `pyproject.toml` for coverage and CI stability.

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
