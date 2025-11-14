#!/usr/bin/env python3
"""
Validate MetricMancer JSON output against the official JSON Schema.

Usage:
    python scripts/validate_json_schema.py output/report.json
    python scripts/validate_json_schema.py output/report.json --schema schemas/metricmancer-v1.schema.json
"""

import json
import sys
from pathlib import Path
from typing import Optional

try:
    import jsonschema
    from jsonschema import validate, ValidationError, SchemaError
except ImportError:
    print("❌ Error: jsonschema package not installed")
    print("Install with: pip install jsonschema")
    sys.exit(1)


def load_json_file(file_path: Path) -> dict:
    """Load and parse JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def validate_metrics(metrics_file: Path, schema_file: Optional[Path] = None) -> bool:
    """
    Validate MetricMancer JSON output against schema.

    Args:
        metrics_file: Path to MetricMancer JSON output
        schema_file: Path to JSON schema (defaults to schemas/metricmancer-v1.schema.json)

    Returns:
        True if validation succeeds, False otherwise
    """
    # Default schema location
    if schema_file is None:
        repo_root = Path(__file__).parent.parent
        schema_file = repo_root / "schemas" / "metricmancer-v1.schema.json"

    print(f"📄 Loading metrics from: {metrics_file}")
    metrics = load_json_file(metrics_file)

    print(f"📋 Loading schema from: {schema_file}")
    schema = load_json_file(schema_file)

    print(f"🔍 Validating {len(metrics) if isinstance(metrics, list) else 1} metric items...")

    try:
        validate(instance=metrics, schema=schema)
        print(f"✅ Validation successful! All {len(metrics)} items conform to schema v{schema.get('version', 'unknown')}")
        return True

    except ValidationError as e:
        print(f"❌ Validation failed!")
        print(f"\nError at: {' -> '.join(str(p) for p in e.absolute_path)}")
        print(f"Message: {e.message}")

        if e.context:
            print("\nDetailed errors:")
            for idx, sub_error in enumerate(e.context, 1):
                print(f"  {idx}. {sub_error.message}")

        return False

    except SchemaError as e:
        print(f"❌ Schema error: {e.message}")
        print("The schema file itself is invalid.")
        return False


def print_schema_stats(schema: dict):
    """Print statistics about the schema."""
    print("\n📊 Schema Information:")
    print(f"  Version: {schema.get('version', 'unknown')}")
    print(f"  Title: {schema.get('title', 'N/A')}")
    print(f"  Description: {schema.get('description', 'N/A')}")

    if 'definitions' in schema and 'MetricItem' in schema['definitions']:
        props = schema['definitions']['MetricItem'].get('properties', {})
        required = schema['definitions']['MetricItem'].get('required', [])
        print(f"\n  Fields defined: {len(props)}")
        print(f"  Required fields: {', '.join(required)}")
        print(f"  Optional fields: {', '.join(set(props.keys()) - set(required))}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate MetricMancer JSON output against schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate with default schema
  python scripts/validate_json_schema.py output/report.json

  # Validate with custom schema
  python scripts/validate_json_schema.py output/report.json --schema custom-schema.json

  # Show schema information
  python scripts/validate_json_schema.py --schema-info
        """
    )

    parser.add_argument(
        'metrics_file',
        type=Path,
        nargs='?',
        help='Path to MetricMancer JSON output file'
    )

    parser.add_argument(
        '--schema',
        type=Path,
        help='Path to JSON schema (default: schemas/metricmancer-v1.schema.json)'
    )

    parser.add_argument(
        '--schema-info',
        action='store_true',
        help='Display schema information and exit'
    )

    args = parser.parse_args()

    # Schema info mode
    if args.schema_info:
        schema_file = args.schema or (Path(__file__).parent.parent / "schemas" / "metricmancer-v1.schema.json")
        schema = load_json_file(schema_file)
        print_schema_stats(schema)
        sys.exit(0)

    # Validation mode
    if not args.metrics_file:
        parser.error("metrics_file is required unless --schema-info is used")

    success = validate_metrics(args.metrics_file, args.schema)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
