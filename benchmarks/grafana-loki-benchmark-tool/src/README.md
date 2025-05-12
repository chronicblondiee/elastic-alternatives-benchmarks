# Grafana Loki Benchmark Tool - Source Code (`src`)

This directory contains the core Python source code for the Grafana Loki Benchmark Tool.

## Overview

The scripts in this directory provide the functionality to connect to a Grafana Loki instance, push log data, and optionally run LogQL queries to benchmark performance. The tool is designed to be run via the command line.

Client connection logic is handled by `loki_client.py`, while the benchmark execution (ingestion, querying, timing) is implemented in `benchmark.py`. The `cli.py` script serves as the entry point, parsing arguments and orchestrating the calls to the client and benchmark functions.

## Files

-   **`__init__.py`**: Makes the `src` directory a Python package (may be empty).
-   **`cli.py`**: The main command-line interface entry point. It uses `argparse` to parse user arguments, initializes the `LokiClient`, and calls the benchmarking functions from `benchmark.py`.
-   **`loki_client.py`**: Contains the `LokiClient` class, which handles the connection and interactions with the Grafana Loki API using the `requests` library. Supports basic auth and API key authentication.
-   **`benchmark.py`**: Contains the core logic for running the ingestion (`run_ingestion`) and query (`run_queries`) benchmarks. `run_ingestion` receives a `LokiClient` instance, handles formatting data for Loki's push API, and sends it. `run_queries` receives a `LokiClient` instance and handles executing LogQL queries against the `query_range` endpoint.
-   **`requirements.txt`**: Lists the Python dependencies.

## Dependencies

-   **`requests`**: Used for making HTTP requests to the Loki API.
-   **`argparse`**: Used for command-line argument parsing (part of the standard Python library).
-   **`pandas`**: Used for data manipulation (check usage, might be optional or for future features).
-   **`numpy`**: Used for numerical operations (check usage, might be optional or for future features).
-   Standard libraries like `logging`, `json`, `time`, `pathlib`, `os`, `datetime`.

## Running the Tool

Execution requires Python 3 and installing dependencies from `requirements.txt`.

```bash
# Navigate to the grafana-loki-benchmark-tool directory
cd /benchmarks/grafana-loki-benchmark-tool

# (Optional) Create and activate a virtual environment
# python -m venv .venv
# source .venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt

# Run the CLI module (Example arguments)
python -m src.cli --loki-url http://localhost:3100 \
    --data-file ../../utils/bulk_test.ndjson \
    --queries-file ../../utils/generated_queries.txt \
    --labels job=benchmark,env=testing \
    --batch-size 1000 \
    --query-limit 500
```

## Command-Line Interface (`cli.py`)

The `cli.py` script accepts the following arguments:

-   `--loki-url`: (Required) Grafana Loki base URL (e.g., `http://localhost:3100`).
-   `--user`: Username for Loki basic authentication.
-   `--password`: Password for Loki basic authentication.
-   `--api-key`: API key for Loki authentication (used as a Bearer token).
-   `--no-verify-certs`: Disable SSL certificate verification.
-   `--timeout`: Request timeout in seconds (default: 30).
-   `--labels`: Comma-separated key=value labels for ingested logs (default: `job=benchmark_tool`). Example: `app=myapp,env=prod`
-   `--data-file`: Path to the NDJSON log file for ingestion (required unless `--query-only`).
-   `--queries-file`: Path to a file containing LogQL queries (one per line) for benchmarking.
-   `--batch-size`: Number of log lines per push request (default: 500).
-   `--query-only`: Run only the query benchmark (requires `--queries-file`).
-   `--query-limit`: Limit for number of results returned by Loki queries (default: 100).

## Authentication

The tool supports connecting to Loki:
-   Without authentication.
-   Using Basic Authentication (`--user`, `--password`).
-   Using an API Key (`--api-key`), sent as a Bearer token.

Authentication details are handled in `loki_client.py` and configured via `cli.py`.

## Benchmark Logic (`benchmark.py`)

- **`run_ingestion`**: Receives a `LokiClient` instance, labels dictionary, data file path, and batch size. It reads the NDJSON data, formats it into Loki's push API structure (streams with labels and timestamped log lines), and uses the client's `push_logs` method (indirectly via client calls within the function) to send data in batches.
- **`run_queries`**: Receives a `LokiClient` instance, queries file path, and query limit. It reads LogQL queries from the file, executes them against Loki's `/loki/api/v1/query_range` endpoint using the client's `query` method (indirectly), times the requests, and aggregates results. Note: The time range for queries is currently hardcoded or determined internally within the function, not set via CLI arguments.

## Input Data

-   **`--data-file`**: Must point to a file in **NDJSON** format. Each line should be a valid JSON object. Timestamps (`@timestamp`, `timestamp`, `time`) are parsed if present; otherwise, the current time is used.
-   **`--queries-file`**: Should be a plain text file where each line contains a single **LogQL** query string. Lines starting with `#` are ignored.

## Output

The `cli.py` script prints the results dictionary returned by `run_ingestion` and `run_queries` to standard output, including metrics like documents per second, average query latency, and error counts.
