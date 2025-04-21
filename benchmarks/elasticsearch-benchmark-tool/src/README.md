# Elasticsearch Benchmark Tool - Source Code (`src`)

This directory contains the core Python source code for the Elasticsearch Benchmark Tool.

## Overview

The scripts in this directory provide the functionality to connect to an Elasticsearch instance, ingest data from a file, and optionally run search queries to benchmark performance. The tool is designed to be run via the command line, typically using the wrapper script provided in the `../utils` directory.

Client connection logic is handled by `es_client.py`, while the benchmark execution (ingestion, querying, timing) is implemented in `benchmark.py`. The `cli.py` script serves as the entry point, parsing arguments and orchestrating the calls to the client and benchmark functions.

## Files

-   **`__init__.py`**: Makes the `src` directory a Python package (may be empty).
-   **`cli.py`**: The main command-line interface entry point. It uses `argparse` to parse user arguments, initializes the `ElasticsearchClient`, and calls the benchmarking functions from `benchmark.py`.
-   **`es_client.py`**: Contains the `ElasticsearchClient` class, which handles the connection (including authentication and HTTPS options) and interactions with the Elasticsearch cluster using the official `elasticsearch` library.
-   **`benchmark.py`**: Contains the core logic for running the ingestion (`run_ingestion`) and query (`run_queries`) benchmarks. `run_ingestion` handles index creation, uses the `elasticsearch-py` bulk helpers, performs timing, counts successes/errors, and returns a dictionary of results. `run_queries` likely requires further implementation for parsing query files and detailed timing.
-   **`requirements.txt`**: Lists the Python dependencies.

## Dependencies

-   **`elasticsearch`**: The official Python client for Elasticsearch (ensure a compatible 8.x version is installed).
-   **`elastic-transport`**: Used by the `elasticsearch` client.
-   **`argparse`**: Used for command-line argument parsing (part of the standard Python library).
-   Standard libraries like `logging`, `json`, `time`, `pathlib`, `os`, `warnings`.

*Note:* The `requirements.txt` file might also list `requests`, `pandas`, and `numpy`. These are **not** currently used by the core benchmarking code (`cli.py`, `es_client.py`, `benchmark.py`). They might be intended for future enhancements or can potentially be removed if not needed for planned features.

## Running the Tool

While the tool can be executed directly as a module from the parent directory (`elasticsearch-benchmark-tool`), it's **recommended to use the `run-elasticsearch-benchmark.sh` wrapper script** located in the `../utils` directory. The wrapper script handles activating the virtual environment and passing necessary configuration (like credentials and HTTPS settings) via environment variables or command-line arguments.

**Direct Execution Example (Less Common):**

```bash
# Navigate to the elasticsearch-benchmark-tool directory
cd /home/brown/elastic-alternatives-benchmarks/benchmarks/elasticsearch-benchmark-tool

# Activate virtual environment
source src/.venv/bin/activate

# Run the CLI module (Requires manual setup of all options, including potentially modifying cli.py for auth/https)
python -m src.cli --host <your_es_host> --data-file <path_to_data.ndjson> [options]

```
# Elasticsearch Benchmark Tool - Source Code (`src`)

This directory contains the core Python source code for the Elasticsearch Benchmark Tool.

## Overview

The scripts in this directory provide the functionality to connect to an Elasticsearch instance, ingest data from a file, and optionally run search queries to benchmark performance. The tool is designed to be run via the command line, typically using the wrapper script provided in the `../utils` directory.

Client connection logic is handled by `es_client.py`, while the benchmark execution (ingestion, querying, timing) is implemented in `benchmark.py`. The `cli.py` script serves as the entry point, parsing arguments and orchestrating the calls to the client and benchmark functions.

## Files

-   **`__init__.py`**: Makes the `src` directory a Python package (may be empty).
-   **`cli.py`**: The main command-line interface entry point. It uses `argparse` to parse user arguments, initializes the `ElasticsearchClient`, and calls the benchmarking functions from `benchmark.py`.
-   **`es_client.py`**: Contains the `ElasticsearchClient` class, which handles the connection (including authentication and HTTPS options) and interactions with the Elasticsearch cluster using the official `elasticsearch` library.
-   **`benchmark.py`**: Contains the core logic for running the ingestion (`run_ingestion`) and query (`run_queries`) benchmarks. `run_ingestion` handles index creation, uses the `elasticsearch-py` bulk helpers, performs timing, counts successes/errors, and returns a dictionary of results. `run_queries` likely requires further implementation for parsing query files and detailed timing.
-   **`requirements.txt`**: Lists the Python dependencies.

## Dependencies

-   **`elasticsearch`**: The official Python client for Elasticsearch (ensure a compatible 8.x version is installed).
-   **`elastic-transport`**: Used by the `elasticsearch` client.
-   **`argparse`**: Used for command-line argument parsing (part of the standard Python library).
-   Standard libraries like `logging`, `json`, `time`, `pathlib`, `os`, `warnings`.

*Note:* The `requirements.txt` file might also list `requests`, `pandas`, and `numpy`. These are **not** currently used by the core benchmarking code (`cli.py`, `es_client.py`, `benchmark.py`). They might be intended for future enhancements or can potentially be removed if not needed for planned features.

## Running the Tool

While the tool can be executed directly as a module from the parent directory (`elasticsearch-benchmark-tool`), it's **recommended to use the `run-elasticsearch-benchmark.sh` wrapper script** located in the `../utils` directory. The wrapper script handles activating the virtual environment and passing necessary configuration (like credentials and HTTPS settings) via environment variables or command-line arguments.

**Direct Execution Example (Less Common):**

```bash
# Navigate to the elasticsearch-benchmark-tool directory
cd /home/brown/elastic-alternatives-benchmarks/benchmarks/elasticsearch-benchmark-tool

# Activate virtual environment
source src/.venv/bin/activate

# Run the CLI module (Requires manual setup of all options, including potentially modifying cli.py for auth/https)
python -m src.cli --host <your_es_host> --data-file <path_to_data.ndjson> [options]
```

## Command-Line Interface (`cli.py`)

The cli.py script accepts the following arguments when run directly:

| Argument           | Description                                                                                                | Default         | Required |
| :----------------- | :--------------------------------------------------------------------------------------------------------- | :-------------- | :------- |
| `--host HOST`      | Hostname or IP address of the Elasticsearch instance.                                                      | `None`          | **Yes**  |
| `--port PORT`      | Port number for the Elasticsearch instance.                                                                | `9200`          | No       |
| `--index-name IDX` | Name of the Elasticsearch index to use for ingestion/searching. Will be created if it doesn't exist.       | `logs`          | No       |
| `--data-file FILE` | Path to the **NDJSON** file containing log data for ingestion.                                             | `None`          | **Yes**  |
| `--queries-file QF`| (Optional) Path to a file with search queries (one per line). Enables the search benchmark after ingestion. | `None`          | No       |
| `--batch-size SIZE`| Number of documents per bulk indexing request.                                                             | `1000`          | No       |
| `--scheme SCHEME`  | Connection scheme ('http' or 'https').                                                                    | `http`          | No       |
| `--no-verify-certs`| Disable SSL certificate verification (use with caution). Sets `verify_certs` to `False`.                     | `False` (Action) | No       |
| `--user USER`      | Username for basic authentication.                                                                         | `None`          | No       |
| `--password PASS`  | Password for basic authentication.                                                                         | `None`          | No       |
| `--api-key KEY`    | API key for authentication.                                                                                | `None`          | No       |
| `--timeout SEC`    | Request timeout in seconds.                                                                                | `30`            | No       |


## Authentication and HTTPS

The es_client.py class supports connecting using:
- Basic authentication (`user`, `password`)
- API key (`api_key`)
- HTTPS (`scheme='https'`)
- Disabling certificate verification (`verify_certs=False`)

The cli.py script has been updated to accept arguments (`--user`, `--password`, `--api-key`, `--scheme`, `--no-verify-certs`) and pass them to the `ElasticsearchClient`. Using the `../utils/run-elasticsearch-benchmark.sh` script is often easier as it can source credentials from environment variables (e.g., set by `setup-elasticsearch-env-vars.sh`).

## Benchmark Logic (`benchmark.py`)

The core benchmarking logic resides in the `run_ingestion` and `run_queries` functions within benchmark.py.
- **`run_ingestion`**: Reads the NDJSON data file, creates the index if needed (ignoring errors if it exists), sends data in batches using `elasticsearch.helpers.bulk`, times the overall process, counts successful and failed documents, and returns a dictionary containing metrics like `total_docs_attempted`, `successful_docs`, `total_time`, `docs_per_sec`, `errors`, and `error_details`.
- **`run_queries`**: This function is called if `--queries-file` is provided but currently has minimal implementation. It would need to be enhanced to read queries from the file, parse them into the format expected by `client.search`, execute them, time each query, and aggregate latency results.

## Input Data

-   **`--data-file`**: Must point to a file in **NDJSON** format (one valid JSON object per line). Ensure the file has correct permissions and ends with a newline character if required by specific tools interacting with it.
-   **`--queries-file`**: Should be a plain text file where each line contains a single query string. The `run_queries` function in benchmark.py needs logic to parse these strings into valid Elasticsearch query dictionaries.

## Output

The cli.py script prints the results dictionary returned by `run_ingestion` and (if implemented) `run_queries`. This provides a summary of the benchmark execution, including performance metrics and error counts. Logging throughout the scripts provides additional detail on the process.
