# OpenSearch Integration Guide

This guide shows how to integrate MetricMancer with OpenSearch (or Elasticsearch) to enable **historical trend analysis**,
**quality dashboards**, and **automated alerting** based on code quality metrics.

## Overview

MetricMancer's JSON output format is designed to be OpenSearch-compatible, with built-in support for:
- **Timestamps** - Track when each analysis was run
- **Repository metadata** - Repo name, component, team
- **All KPIs** - Complexity, cognitive complexity, churn, hotspot score, ownership
- **File and package levels** - Granular and aggregated metrics

By regularly exporting MetricMancer metrics to OpenSearch, you can:
- **Track quality trends** over weeks, months, or years
- **Identify degrading hotspots** before they become critical
- **Monitor team performance** and code ownership patterns
- **Set up alerts** when thresholds are exceeded
- **Create executive dashboards** for stakeholders

## Architecture

```
┌───────────────────┐
│   CI/CD Pipeline  │
│   (GitHub Actions,│
│    Jenkins, etc.) │
└────────┬──────────┘
         │
         │ Daily/Weekly
         ▼
┌──────────────────┐
│  MetricMancer    │
│  JSON Export     │
└────────┬─────────┘
         │
         │ HTTP POST
         ▼
┌──────────────────┐
│   OpenSearch     │
│   Time Series    │
│   Index          │
└────────┬─────────┘
         │
         │ Query
         ▼
┌──────────────────┐
│  Dashboards      │
│  (Kibana/OSD)    │
└──────────────────┘
```

## Quick Start

### 1. Generate MetricMancer JSON Report

```bash
# Single run with timestamp
python -m src.main src/ --output-formats json --report-folder output/

# Or schedule in CI/CD
python -m src.main src/ tests/ --output-formats json --report-filename "metrics-$(date +%Y%m%d).json"
```

The JSON output includes timestamps automatically:
```json
{
  "filename": "src/app/metric_mancer_app.py",
  "cyclomatic_complexity": 85,
  "cognitive_complexity": 42,
  "churn": 147,
  "hotspot_score": 12495,
  "code_ownership": {"alice@example.com": 65, "bob@example.com": 35},
  "shared_ownership": 2,
  "timestamp": "2025-11-14T12:30:00Z",
  "repo_name": "MetricMancer",
  "component": "app",
  "team": "platform"
}
```

### 2. Create OpenSearch Index

Create an index with proper mappings for time-series data:

```bash
curl -X PUT "localhost:9200/metricmancer-metrics" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "filename": { "type": "keyword" },
      "package": { "type": "keyword" },
      "repo_name": { "type": "keyword" },
      "component": { "type": "keyword" },
      "team": { "type": "keyword" },
      "timestamp": { "type": "date" },
      "cyclomatic_complexity": { "type": "integer" },
      "cognitive_complexity": { "type": "integer" },
      "churn": { "type": "integer" },
      "hotspot_score": { "type": "integer" },
      "shared_ownership": { "type": "integer" },
      "code_ownership": { "type": "object", "enabled": false }
    }
  },
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "index.lifecycle.name": "metricmancer-lifecycle",
    "index.lifecycle.rollover_alias": "metricmancer-metrics"
  }
}
'
```

### 3. Index MetricMancer Data

Upload the JSON report to OpenSearch:

```bash
# Direct bulk upload (for array of metrics)
curl -X POST "localhost:9200/metricmancer-metrics/_bulk" \
  -H 'Content-Type: application/x-ndjson' \
  --data-binary @output/report.json

# Or use a script to process the JSON
python scripts/upload_to_opensearch.py output/report.json
```

Example upload script (`scripts/upload_to_opensearch.py`):

```python
#!/usr/bin/env python3
"""Upload MetricMancer JSON to OpenSearch."""

import json
import sys
from datetime import datetime
from opensearchpy import OpenSearch

def upload_metrics(json_file, opensearch_host="localhost:9200"):
    """Upload MetricMancer metrics to OpenSearch."""
    # Connect to OpenSearch
    client = OpenSearch(
        hosts=[opensearch_host],
        http_auth=('admin', 'admin'),  # Change in production!
        use_ssl=False,
        verify_certs=False
    )

    # Read MetricMancer JSON
    with open(json_file, 'r') as f:
        metrics = json.load(f)

    # Ensure timestamp exists
    timestamp = datetime.utcnow().isoformat()

    # Bulk upload
    bulk_data = []
    for metric in metrics:
        if 'timestamp' not in metric:
            metric['timestamp'] = timestamp

        # Index action
        bulk_data.append({"index": {"_index": "metricmancer-metrics"}})
        bulk_data.append(metric)

    # Upload
    response = client.bulk(body=bulk_data)

    if response['errors']:
        print(f"❌ Errors during upload: {response['errors']}")
        sys.exit(1)
    else:
        print(f"✅ Uploaded {len(metrics)} metrics to OpenSearch")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_to_opensearch.py <json_file> [opensearch_host]")
        sys.exit(1)

    json_file = sys.argv[1]
    opensearch_host = sys.argv[2] if len(sys.argv) > 2 else "localhost:9200"

    upload_metrics(json_file, opensearch_host)
```

Dependencies:
```bash
pip install opensearch-py
```

### 4. Query Metrics

Example queries using OpenSearch DSL:

**Get complexity trend for a specific file:**
```json
GET metricmancer-metrics/_search
{
  "query": {
    "term": { "filename.keyword": "src/app/metric_mancer_app.py" }
  },
  "sort": [{ "timestamp": "asc" }],
  "size": 100
}
```

**Find files with increasing hotspot scores:**
```json
GET metricmancer-metrics/_search
{
  "size": 0,
  "query": {
    "range": { "timestamp": { "gte": "now-90d" } }
  },
  "aggs": {
    "by_file": {
      "terms": { "field": "filename.keyword", "size": 100 },
      "aggs": {
        "hotspot_trend": {
          "date_histogram": { "field": "timestamp", "calendar_interval": "week" },
          "aggs": {
            "avg_hotspot": { "avg": { "field": "hotspot_score" } }
          }
        }
      }
    }
  }
}
```

**Identify top 10 current hotspots:**
```json
GET metricmancer-metrics/_search
{
  "size": 10,
  "query": {
    "range": { "timestamp": { "gte": "now-1d" } }
  },
  "sort": [{ "hotspot_score": "desc" }]
}
```

**Team performance comparison:**
```json
GET metricmancer-metrics/_search
{
  "size": 0,
  "query": {
    "range": { "timestamp": { "gte": "now-30d" } }
  },
  "aggs": {
    "by_team": {
      "terms": { "field": "team.keyword" },
      "aggs": {
        "avg_complexity": { "avg": { "field": "cyclomatic_complexity" } },
        "avg_cognitive": { "avg": { "field": "cognitive_complexity" } },
        "avg_hotspot": { "avg": { "field": "hotspot_score" } }
      }
    }
  }
}
```

## Dashboard Examples

### 1. Complexity Trend Dashboard

**Visualization:** Line chart
- X-axis: timestamp
- Y-axis: cyclomatic_complexity (avg)
- Group by: filename (top 10 files)

**Use case:** Track if complexity is increasing over time in critical files.

### 2. Hotspot Heatmap

**Visualization:** Heatmap
- Rows: filename
- Columns: timestamp (weekly buckets)
- Color: hotspot_score (red = high, green = low)

**Use case:** Identify files that consistently remain hotspots.

### 3. Team Quality Metrics

**Visualization:** Bar chart
- X-axis: team
- Y-axis: Average cognitive_complexity
- Filter: Last 30 days

**Use case:** Compare code quality across teams.

### 4. Cognitive Complexity Distribution

**Visualization:** Histogram
- Buckets: 0-10, 11-20, 21-50, 50+
- Count: Number of files in each bucket
- Trend line: Compare current vs. 3 months ago

**Use case:** See if code is becoming more understandable over time.

## Alerting

Set up OpenSearch alerts to notify when quality degrades:

### Example: Alert on High Hotspot Score

```json
{
  "name": "High Hotspot Alert",
  "type": "monitor",
  "monitor_type": "query_level_monitor",
  "enabled": true,
  "schedule": {
    "period": { "interval": 1, "unit": "DAYS" }
  },
  "inputs": [{
    "search": {
      "indices": ["metricmancer-metrics"],
      "query": {
        "size": 0,
        "query": {
          "bool": {
            "must": [
              { "range": { "timestamp": { "gte": "now-1d" } } },
              { "range": { "hotspot_score": { "gte": 5000 } } }
            ]
          }
        },
        "aggs": {
          "high_hotspots": {
            "terms": { "field": "filename.keyword", "size": 10 }
          }
        }
      }
    }
  }],
  "triggers": [{
    "name": "Hotspot threshold exceeded",
    "severity": "2",
    "condition": {
      "script": {
        "source": "ctx.results[0].hits.total.value > 0"
      }
    },
    "actions": [{
      "name": "Send Slack notification",
      "destination_id": "slack-webhook-id",
      "message_template": {
        "source": "High hotspot detected: {{ctx.results[0].hits.hits.0._source.filename}} (score: {{ctx.results[0].hits.hits.0._source.hotspot_score}})"
      }
    }]
  }]
}
```

### Example: Alert on Complexity Increase

```json
{
  "name": "Complexity Increase Alert",
  "type": "monitor",
  "enabled": true,
  "schedule": {
    "period": { "interval": 7, "unit": "DAYS" }
  },
  "inputs": [{
    "search": {
      "indices": ["metricmancer-metrics"],
      "query": {
        "size": 0,
        "aggs": {
          "by_file": {
            "terms": { "field": "filename.keyword", "size": 100 },
            "aggs": {
              "current_week": {
                "filter": { "range": { "timestamp": { "gte": "now-7d" } } },
                "aggs": { "avg_complexity": { "avg": { "field": "cyclomatic_complexity" } } }
              },
              "previous_week": {
                "filter": { "range": { "timestamp": { "gte": "now-14d", "lt": "now-7d" } } },
                "aggs": { "avg_complexity": { "avg": { "field": "cyclomatic_complexity" } } }
              },
              "complexity_change": {
                "bucket_script": {
                  "buckets_path": {
                    "current": "current_week>avg_complexity",
                    "previous": "previous_week>avg_complexity"
                  },
                  "script": "params.current - params.previous"
                }
              }
            }
          }
        }
      }
    }
  }],
  "triggers": [{
    "name": "Complexity increased by >20%",
    "condition": {
      "script": {
        "source": "ctx.results[0].aggregations.by_file.buckets.stream().anyMatch(bucket -> bucket.complexity_change.value > 20)"
      }
    }
  }]
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: MetricMancer Quality Tracking

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  push:
    branches: [main]

jobs:
  analyze-and-upload:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for churn analysis

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install MetricMancer
        run: |
          pip install -e .

      - name: Run MetricMancer Analysis
        run: |
          python -m src.main src/ tests/ \
            --output-formats json \
            --report-folder output/ \
            --report-filename "metrics-$(date +%Y%m%d-%H%M%S).json"

      - name: Upload to OpenSearch
        env:
          OPENSEARCH_HOST: ${{ secrets.OPENSEARCH_HOST }}
          OPENSEARCH_USER: ${{ secrets.OPENSEARCH_USER }}
          OPENSEARCH_PASSWORD: ${{ secrets.OPENSEARCH_PASSWORD }}
        run: |
          pip install opensearch-py
          python scripts/upload_to_opensearch.py \
            output/metrics-*.json \
            $OPENSEARCH_HOST

      - name: Archive metrics
        uses: actions/upload-artifact@v3
        with:
          name: metricmancer-metrics
          path: output/metrics-*.json
          retention-days: 90
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any

    triggers {
        cron('H 2 * * *')  // Daily at 2 AM
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Analyze Code Quality') {
            steps {
                sh '''
                    python3 -m venv .venv
                    source .venv/bin/activate
                    pip install -e .

                    python -m src.main src/ tests/ \
                        --output-formats json \
                        --report-folder output/ \
                        --report-filename "metrics-${BUILD_TIMESTAMP}.json"
                '''
            }
        }

        stage('Upload to OpenSearch') {
            environment {
                OPENSEARCH_HOST = credentials('opensearch-host')
                OPENSEARCH_CREDS = credentials('opensearch-credentials')
            }
            steps {
                sh '''
                    source .venv/bin/activate
                    pip install opensearch-py

                    python scripts/upload_to_opensearch.py \
                        output/metrics-*.json \
                        ${OPENSEARCH_HOST}
                '''
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'output/metrics-*.json', fingerprint: true
            }
        }
    }
}
```

## Best Practices

### 1. Index Lifecycle Management (ILM)

Configure ILM to manage index size and retention:

```bash
curl -X PUT "localhost:9200/_ilm/policy/metricmancer-lifecycle" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "30d"
          }
        }
      },
      "warm": {
        "min_age": "30d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 }
        }
      },
      "delete": {
        "min_age": "365d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
'
```

### 2. Sampling Strategy

For large repositories, consider:
- **Daily full scans** for critical paths (e.g., `src/core/`)
- **Weekly full scans** for entire repository
- **On-demand scans** for pull requests

### 3. Data Enrichment

Add metadata to MetricMancer runs:
```bash
python -m src.main src/ \
  --output-formats json \
  --component "payment-service" \
  --team "platform" \
  --report-folder output/
```

### 4. Query Performance

- Use `keyword` type for exact matches (filename, team, component)
- Add filters before aggregations
- Limit time ranges for better performance
- Use index aliases for rolling indices

## Troubleshooting

### Issue: Timestamps are missing

**Solution:** Ensure you're using MetricMancer v3.1.0+ which includes automatic timestamps.

### Issue: Bulk upload fails

**Solution:** Check JSON format - ensure it's an array of objects:
```json
[
  {"filename": "...", "timestamp": "...", ...},
  {"filename": "...", "timestamp": "...", ...}
]
```

### Issue: Queries are slow

**Solutions:**
- Add time range filters: `{ "range": { "timestamp": { "gte": "now-30d" } } }`
- Use index patterns: `metricmancer-metrics-2025-*`
- Enable index caching for repeated queries

### Issue: Dashboard shows duplicate data

**Solution:** Use aggregations with `top_hits` to get latest value per file:
```json
{
  "aggs": {
    "by_file": {
      "terms": { "field": "filename.keyword" },
      "aggs": {
        "latest": {
          "top_hits": {
            "sort": [{ "timestamp": "desc" }],
            "size": 1
          }
        }
      }
    }
  }
}
```

## Advanced Use Cases

### 1. Pull Request Quality Gates

Fail PR if hotspot score increases:
```bash
# In CI/CD
CURRENT_HOTSPOT=$(python -m src.main src/ --output-formats json | jq '[.[].hotspot_score] | max')
BASELINE_HOTSPOT=$(curl "localhost:9200/metricmancer-metrics/_search" | jq '.hits.hits[0]._source.hotspot_score')

if [ $CURRENT_HOTSPOT -gt $BASELINE_HOTSPOT ]; then
  echo "❌ Hotspot score increased from $BASELINE_HOTSPOT to $CURRENT_HOTSPOT"
  exit 1
fi
```

### 2. Technical Debt Tracking

Calculate total debt based on complexity:
```json
GET metricmancer-metrics/_search
{
  "size": 0,
  "query": { "range": { "timestamp": { "gte": "now-1d" } } },
  "aggs": {
    "total_complexity": { "sum": { "field": "cyclomatic_complexity" } },
    "total_cognitive": { "sum": { "field": "cognitive_complexity" } },
    "technical_debt_estimate": {
      "bucket_script": {
        "buckets_path": {
          "complexity": "total_complexity",
          "cognitive": "total_cognitive"
        },
        "script": "(params.complexity + params.cognitive) * 0.5"
      }
    }
  }
}
```

### 3. Code Review Prioritization

Export high-risk files for review:
```bash
curl "localhost:9200/metricmancer-metrics/_search" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"range": {"hotspot_score": {"gte": 1000}}}, "sort": [{"hotspot_score": "desc"}]}' \
  | jq -r '.hits.hits[]._source.filename' > high_risk_files.txt
```

## Resources

- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [OpenSearch Dashboards](https://opensearch.org/docs/latest/dashboards/index/)
- [OpenSearch Python Client](https://opensearch.org/docs/latest/clients/python/)
- [MetricMancer JSON Schema](../schemas/metricmancer-v1.schema.json)
- [JSON Schema Validation](../scripts/validate_json_schema.py)
- [OpenSearch Mapping Generator](../scripts/generate_opensearch_mapping.py)

## Support

For questions or issues with OpenSearch integration:
- Open an issue: https://github.com/YourOrg/MetricMancer/issues
- Contribute improvements: See [CONTRIBUTING.md](../CONTRIBUTING.md)
