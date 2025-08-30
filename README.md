# ComplexityScanner

Analyze cyclomatic complexity in your codebase and generate a clear HTML report.

## Features
- Scans specified directories for Python, JavaScript, TypeScript, Java, and C# files
- Calculates cyclomatic complexity and function count per file
- Grades complexity (Low, Medium, High) and summarizes per language and root folder
- Highlights problematic folders and files exceeding configurable thresholds
- Generates a modern HTML report with summary, details, and usage instructions

## Usage

Run from the command line:

```sh
python main.py <directories> --threshold <value> --problem-file-threshold <value>
```

### Parameters
- `<directories>`: One or more root folders to scan for code complexity
- `--threshold`: Sets the threshold for average folder/root complexity (default: 20.0)
- `--problem-file-threshold`: Sets the threshold for individual file complexity (default: same as threshold)

### Example

```sh
python main.py src test --threshold 20 --problem-file-threshold 15
```

## Output
- The report is generated as `komplexitet_rapport.html` in the project root
- The summary section highlights folders and files exceeding the thresholds
- Usage instructions are included at the bottom of the report

## Extending
- Add support for more languages in `config.py`
- Customize the report appearance in `templates/report.html`

## Requirements
- Python 3.7+
- Jinja2 (`pip install jinja2`)

## License
MIT
