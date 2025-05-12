# Grafana Loki Benchmark Tool

This directory contains the source code for the Grafana Loki benchmark tool.

**Note:** The initial code structure has been copied from the Elasticsearch benchmark tool. It requires significant modification to work correctly with Grafana Loki's API and data model. The client interaction logic (currently in `src/es_client.py`) needs to be rewritten for Loki.

See the [main benchmark README](../README.md) for general usage patterns once implemented.
