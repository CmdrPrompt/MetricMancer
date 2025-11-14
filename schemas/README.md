# MetricMancer JSON Schemas

This directory contains JSON Schemas for MetricMancer's export formats.

## Available Schemas

### metricmancer-v1.schema.json

Official JSON Schema for MetricMancer metrics export format (v1.0).

**Purpose:**
- Document the structure of MetricMancer JSON output
- Validate JSON exports for correctness
- Generate OpenSearch/Elasticsearch mappings
- Enable IDE auto-completion and type checking

**Schema Version:** 1.0.0
**MetricMancer Version:** 3.1.0+
**Specification:** JSON Schema Draft-07

## Usage

### Validate JSON Output

```bash
# Validate a MetricMancer JSON export
python scripts/validate_json_schema.py output/report.json

# Validate with custom schema
python scripts/validate_json_schema.py output/report.json --schema schemas/metricmancer-v1.schema.json

# Show schema information
python scripts/validate_json_schema.py --schema-info
```

### Generate OpenSearch Mapping

```bash
# Generate OpenSearch index mapping from schema
python scripts/generate_opensearch_mapping.py

# Save to file
python scripts/generate_opensearch_mapping.py --output mappings/opensearch-mapping.json

# Include curl command
python scripts/generate_opensearch_mapping.py --with-curl
```

### Use in Code

```python
import json
import jsonschema
from pathlib import Path

# Load schema
schema_path = Path("schemas/metricmancer-v1.schema.json")
with open(schema_path) as f:
    schema = json.load(f)

# Load metrics
with open("output/report.json") as f:
    metrics = json.load(f)

# Validate
try:
    jsonschema.validate(instance=metrics, schema=schema)
    print("✅ Valid!")
except jsonschema.ValidationError as e:
    print(f"❌ Invalid: {e.message}")
```

### IDE Integration

Most modern IDEs support JSON Schema for validation and auto-completion:

**VS Code:**
Add to `.vscode/settings.json`:
```json
{
  "json.schemas": [
    {
      "fileMatch": ["output/*.json", "metrics-*.json"],
      "url": "./schemas/metricmancer-v1.schema.json"
    }
  ]
}
```

**JetBrains IDEs (PyCharm, IntelliJ):**
Settings → Languages & Frameworks → Schemas and DTDs → JSON Schema Mappings

## Schema Structure

The schema defines an array of `MetricItem` objects. Each item represents:
- **File-level metrics** (when `function_name` is absent)
- **Function-level metrics** (when `function_name` is present)
- **Package-level metrics** (when `package` is present)

### Required Fields

- `filename`: Path to file or package

### Optional Fields

All KPI fields are optional (nullable) to support partial analysis:

**Complexity Metrics:**
- `cyclomatic_complexity` (integer): McCabe complexity
- `cognitive_complexity` (integer): SonarSource cognitive complexity

**Change Metrics:**
- `churn` (integer): Number of commits
- `hotspot_score` (integer): Complexity × churn

**Ownership Metrics:**
- `code_ownership` (object/array): Contributor percentages or list
- `shared_ownership` (integer): Number of significant contributors

**Metadata:**
- `repo_name` (string): Repository name
- `component` (string): Component/service name
- `team` (string): Owning team
- `timestamp` (string): ISO 8601 timestamp

**Function-Level Only:**
- `function_name` (string): Name of function/method

**Package-Level Only:**
- `package` (string): Directory path

## Example Data

### File-Level Metric

```json
{
  "filename": "src/app/metric_mancer_app.py",
  "cyclomatic_complexity": 85,
  "cognitive_complexity": 42,
  "churn": 147,
  "hotspot_score": 12495,
  "code_ownership": {
    "alice@example.com": 65.5,
    "bob@example.com": 34.5
  },
  "shared_ownership": 2,
  "repo_name": "MetricMancer",
  "component": "app",
  "team": "platform",
  "timestamp": "2025-11-14T12:30:00Z"
}
```

### Function-Level Metric

```json
{
  "filename": "src/app/metric_mancer_app.py",
  "function_name": "run",
  "cyclomatic_complexity": 12,
  "cognitive_complexity": 8,
  "churn": 147,
  "hotspot_score": 1764,
  "code_ownership": {
    "alice@example.com": 100.0
  },
  "shared_ownership": 1,
  "repo_name": "MetricMancer",
  "timestamp": "2025-11-14T12:30:00Z"
}
```

### Package-Level Metric

```json
{
  "filename": "src/app/",
  "package": "src/app/",
  "cyclomatic_complexity": 423,
  "cognitive_complexity": 215,
  "churn": 892,
  "hotspot_score": 377316,
  "code_ownership": [
    "alice@example.com",
    "bob@example.com",
    "charlie@example.com"
  ],
  "shared_ownership": 5,
  "repo_name": "MetricMancer",
  "timestamp": "2025-11-14T12:30:00Z"
}
```

## Schema Versioning

Schema versions follow Semantic Versioning (SemVer):

- **Major version** (X.0.0): Breaking changes to schema structure
- **Minor version** (0.X.0): Backward-compatible additions (new optional fields)
- **Patch version** (0.0.X): Documentation or non-functional changes

### Version History

- **v1.0.0** (2025-11-14): Initial schema release
  - Supports file, function, and package-level metrics
  - All MetricMancer v3.1.0+ KPIs included
  - OpenSearch/Elasticsearch-compatible

## Compatibility

| MetricMancer Version | Schema Version | Status |
|---------------------|----------------|--------|
| 3.2.0+ | v1.0.0 | ✅ Current |
| 3.1.0 - 3.1.x | v1.0.0 | ✅ Compatible |
| < 3.1.0 | N/A | ❌ No schema support |

## Related Documentation

- [OpenSearch Integration Guide](../docs/OPENSEARCH_INTEGRATION.md)
- [JSON Report Format Source](../src/report/json/json_report_format.py)
- [Software Specification](../docs/SoftwareSpecificationAndDesign.md)

## Contributing

When proposing schema changes:

1. **Minor changes** (new optional fields): Increment minor version
2. **Breaking changes** (remove/rename fields, change types): Create new major version
3. **Update examples** in schema and this README
4. **Test validation** with actual MetricMancer output
5. **Update OpenSearch mapping** generator if needed

## License

Same as MetricMancer: [MIT License](../LICENSE)
