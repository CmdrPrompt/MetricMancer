# MetricMancer

MetricMancer is a software analytics tool that provides actionable insights into code quality, maintainability, and
technical risk. Inspired by "Your Code as a Crime Scene" by Adam Tornhill, it analyzes source code repositories to
extract key performance indicators (KPIs) such as cyclomatic complexity, code churn, and hotspots. MetricMancer is
designed for extensibility, multi-language support, and integration with CI/CD pipelines.

For detailed requirements, architecture, and design, see the
[Software Specification and Design](docs/SoftwareSpecificationAndDesign.md) document.

## Features

- **Multi-language support:** Analyze Python, JavaScript, TypeScript, Java, C#, C, C++, Go, Ada, Shell scripts, JSON,
  YAML, and IDL files with extensible parser architecture for adding new languages.
- **Cognitive complexity** **[New in v3.2.0]:** Human-centric code understandability metric (SonarSource algorithm) for
  Python, Java, Go, JavaScript, TypeScript, and C. See [Cognitive Complexity Guide](docs/COGNITIVE_COMPLEXITY_USER_GUIDE.md)
- **Code churn:** Tracks commit frequency per file to identify frequently changing code.
- **Hotspot analysis:** Identifies high-risk files/functions with both high complexity and high churn.
- **Code review advisor:** Generates data-driven review recommendations based on complexity, churn, and ownership metrics.
- **Flexible reporting:** CLI, HTML, JSON formats, plus specialized hotspot and review strategy reports. Generate
  multiple formats in one run with `--output-formats` (50-70% faster). JSON output is OpenSearch/Elasticsearch-ready
  for historical trend analysis.
- **Configurable thresholds:** Customize complexity thresholds and severity grades.
- **Extensible architecture:** Easy to add new KPIs, languages, or report formats. See [CONTRIBUTING.md](CONTRIBUTING.md)
- **CI/CD ready:** Scriptable CLI with machine-readable JSON output.

## Usage

Run from the command line:

```sh
python -m src.main <directories> [options]
```

### Common Options

**Basic Options:**
- `<directories>`: One or more root folders to scan
- `--threshold-low <value>`: Low complexity threshold (default: 10.0)
- `--threshold-high <value>`: High complexity threshold (default: 20.0)
- `--report-folder <folder>`: Output folder (default: 'output')

**Output Formats:**
- `--output-formats <formats>`: Generate multiple formats in one run (comma-separated): 'html', 'json', 'summary',
  'quick-wins', 'tree', 'review-strategy', 'review-strategy-branch'. Scans once, 50-70% faster than separate runs

**Analysis Options:**
- `--list-hotspots`: Display high-risk files after analysis
- `--hotspot-output <file>`: Save hotspot list to file (.md or .txt)
- `--review-strategy`: Generate code review recommendations
- `--review-branch-only`: Review only changed files in current branch
- `--churn-period <days>`: Days to analyze for code churn (default: 30)

Run `python -m src.main --help` for all options.

### Examples

```sh
# Basic analysis
python -m src.main path/to/repo

# Multiple directories with custom thresholds
python -m src.main src/ tests/ --threshold-low 8 --threshold-high 15

# Generate multiple formats in one run (50-70% faster)
python -m src.main path/to/repo --output-formats html,json,summary

# Hotspot analysis
python -m src.main path/to/repo --list-hotspots --hotspot-output hotspots.md

# Code review strategy for changed files only
python -m src.main path/to/repo --review-strategy --review-branch-only
```

## Output

All reports are saved to the **`output/`** directory by default. This can be customized with the `--report-folder`
option.

### Terminal Output Formats

- **Executive Summary (default):** Actionable dashboard showing critical issues, health metrics, and recommendations
- **Quick Wins:** Prioritized improvement suggestions ranked by ROI (impact vs. effort ratio)
- **Detailed Tree:** Traditional tree-structured output per repository, showing complexity, churn, hotspot score, and
  grade for each file

### Report Files

- **HTML report:** Interactive, modern report with summary, details, and usage instructions
- **JSON report:** Machine-readable output for dashboards and integrations
- **Hotspot analysis:** Markdown or text file listing high-risk files
- **Code review strategy:** Markdown or text file with prioritized review recommendations

Clean output directory: `python scripts/clean_output.py` (use `--dry-run` to preview)

## Architecture

MetricMancer follows modern software design principles including SOLID principles and implements several proven design
patterns:

- **Configuration Object Pattern:** Centralized, type-safe configuration reduces code churn and improves maintainability
- **Factory Pattern:** Clean report generator creation without conditional logic
- **Strategy Pattern:** Polymorphic behavior for extensible report formats and KPI calculations
- **Builder Pattern:** Incremental construction of complex report data structures

The architecture emphasizes separation of concerns, dependency injection, and test-driven development. For complete
architectural details, design decisions, and component interactions, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Requirements

- Python 3.10+
- Dependencies managed via `pyproject.toml` (see [SETUP.md](docs/SETUP.md) for installation)

## Key KPIs

- Cyclomatic Complexity (per function/method)
- **Cognitive Complexity (per function/method)** - **[New in v3.2.0]** Human-centric complexity metric for Python, Java,
  Go, JavaScript, TypeScript, and C. See [Cognitive Complexity Guide](docs/COGNITIVE_COMPLEXITY_USER_GUIDE.md)
- Code Churn (per file)
- Hotspot Score (complexity × churn)
- Code Ownership (per file)
- Shared Ownership (per file/function, aggregation to directory/repo)

See [SoftwareSpecificationAndDesign.md](docs/SoftwareSpecificationAndDesign.md) for full KPI definitions and planned
features.

## Testing

MetricMancer has comprehensive test coverage with 839 tests covering all functionality.

```bash
# Quick test run
./scripts/run_tests.sh

# Manual test run with pytest
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ -v --cov=src --cov-report=html
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup and workflow
- Code quality standards and tools
- Testing guidelines
- How to extend MetricMancer (new KPIs, languages, report formats)
- License requirements for dependencies

## Future Plans

- **Issue tracker integration:** Correlate code metrics with defect data from Jira, GitHub Issues, etc.
- **Test coverage integration:** Relate code coverage to hotspots and churn.
- **Historical trend analysis:** Track complexity/churn/hotspot evolution over time.
- **Accessibility:** Improve HTML report accessibility (ARIA, color contrast, keyboard navigation).

## Documentation

- [Cognitive Complexity Guide](docs/COGNITIVE_COMPLEXITY_USER_GUIDE.md) - Understanding cognitive complexity metrics
- [OpenSearch Integration](docs/OPENSEARCH_INTEGRATION.md) - Historical trend analysis and quality dashboards
- [Software Specification](docs/SoftwareSpecificationAndDesign.md) - Complete requirements and KPI definitions
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines and extension guide
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture and design patterns
- [SETUP.md](docs/SETUP.md) - Detailed setup instructions
- [LICENSE_INFO.md](docs/LICENSE_INFO.md) - Complete licensing information

## License

MetricMancer is licensed under the [MIT License](LICENSE). All dependencies use permissive licenses. See
[LICENSE_INFO.md](docs/LICENSE_INFO.md) for details.
