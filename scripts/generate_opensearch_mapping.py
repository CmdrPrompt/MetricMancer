#!/usr/bin/env python3
"""
Generate OpenSearch/Elasticsearch index mapping from MetricMancer JSON Schema.

This script reads the JSON Schema and generates a corresponding OpenSearch mapping
that can be used to create an optimized index for MetricMancer metrics.

Usage:
    python scripts/generate_opensearch_mapping.py
    python scripts/generate_opensearch_mapping.py --schema schemas/metricmancer-v1.schema.json
    python scripts/generate_opensearch_mapping.py --output mappings/opensearch-mapping.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def json_type_to_opensearch_type(json_type: str, field_name: str, field_def: Dict[str, Any]) -> str:
    """
    Convert JSON Schema type to OpenSearch field type.

    Args:
        json_type: JSON Schema type (string, integer, etc.)
        field_name: Name of the field
        field_def: Full field definition from schema

    Returns:
        OpenSearch field type
    """
    # Handle date-time format
    if json_type == "string" and field_def.get("format") == "date-time":
        return "date"

    # Handle email patterns (use keyword for exact matching)
    if json_type == "string" and field_name in ["repo_name", "component", "team"]:
        return "keyword"

    # Filename should be keyword for exact matching and aggregations
    if field_name == "filename" or field_name == "package" or field_name == "function_name":
        return "keyword"

    # Standard type mappings
    type_mapping = {
        "string": "text",
        "integer": "integer",
        "number": "float",
        "boolean": "boolean",
        "object": "object",
        "array": "nested"
    }

    return type_mapping.get(json_type, "text")


def generate_mapping_from_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate OpenSearch mapping from JSON Schema.

    Args:
        schema: Loaded JSON Schema

    Returns:
        OpenSearch mapping dictionary
    """
    if 'definitions' not in schema or 'MetricItem' not in schema['definitions']:
        raise ValueError("Schema does not contain MetricItem definition")

    metric_item = schema['definitions']['MetricItem']
    properties = metric_item.get('properties', {})

    # Build OpenSearch mapping
    mapping = {
        "mappings": {
            "properties": {}
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "index": {
                "max_result_window": 10000
            }
        }
    }

    for field_name, field_def in properties.items():
        # Handle oneOf (code_ownership can be object or array)
        if 'oneOf' in field_def:
            # For code_ownership, disable indexing (just store as-is)
            if field_name == "code_ownership":
                mapping["mappings"]["properties"][field_name] = {
                    "type": "object",
                    "enabled": False  # Don't index, just store
                }
            continue

        # Handle nullable types (type: [X, "null"])
        if isinstance(field_def.get('type'), list):
            json_types = [t for t in field_def['type'] if t != 'null']
            if not json_types:
                continue
            json_type = json_types[0]
        else:
            json_type = field_def.get('type', 'string')

        # Generate OpenSearch field definition
        os_type = json_type_to_opensearch_type(json_type, field_name, field_def)

        field_mapping = {"type": os_type}

        # Add field-specific configurations
        if field_name == "timestamp":
            field_mapping["format"] = "strict_date_optional_time||epoch_millis"

        # For text fields, add keyword sub-field for aggregations
        if os_type == "text":
            field_mapping["fields"] = {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }

        # Add description as comment (OpenSearch 2.x+)
        if "description" in field_def:
            field_mapping["meta"] = {
                "description": field_def["description"]
            }

        mapping["mappings"]["properties"][field_name] = field_mapping

    return mapping


def format_for_opensearch_api(mapping: Dict[str, Any]) -> str:
    """
    Format mapping for direct use with OpenSearch API.

    Args:
        mapping: OpenSearch mapping

    Returns:
        Formatted JSON string with curl command
    """
    json_str = json.dumps(mapping, indent=2)

    curl_command = f"""
# Create OpenSearch index with MetricMancer mapping
curl -X PUT "localhost:9200/metricmancer-metrics" \\
  -H 'Content-Type: application/json' \\
  -d '{json_str}'

# Or using the mapping file:
curl -X PUT "localhost:9200/metricmancer-metrics" \\
  -H 'Content-Type: application/json' \\
  --data-binary @mappings/opensearch-mapping.json
"""

    return curl_command


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate OpenSearch mapping from MetricMancer JSON Schema",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--schema',
        type=Path,
        default=Path(__file__).parent.parent / "schemas" / "metricmancer-v1.schema.json",
        help='Path to JSON schema (default: schemas/metricmancer-v1.schema.json)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        help='Output file for mapping (default: print to stdout)'
    )

    parser.add_argument(
        '--with-curl',
        action='store_true',
        help='Include curl command in output'
    )

    args = parser.parse_args()

    # Load schema
    try:
        with open(args.schema, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in schema: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate mapping
    try:
        mapping = generate_mapping_from_schema(schema)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output mapping
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2)
        print(f"✅ Generated OpenSearch mapping: {args.output}")

        if args.with_curl:
            print(f"\n{format_for_opensearch_api(mapping)}")
    else:
        # Print to stdout
        print(json.dumps(mapping, indent=2))

        if args.with_curl:
            print(f"\n{format_for_opensearch_api(mapping)}", file=sys.stderr)


if __name__ == "__main__":
    main()
