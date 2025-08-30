# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Cyclomatic complexity support for Ada, C, C++, Go.
- Modular parser interface for all supported languages.
- Unittest test cases for all language parsers.
- Dynamic parser loading via config.
- GitHub Actions workflow now builds and tests all branches.

### Changed
- Refactored codebase for maintainability and testability.
- Improved Ada parser to avoid double-counting control keywords.
- Cleaned up template directories; only `src/templates` is used.

### Removed
- Deleted unused `templates/` folder from project root.

## [1.0.0] - 2025-08-30
### Added
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

