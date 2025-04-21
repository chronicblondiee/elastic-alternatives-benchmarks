# Elasticsearch Benchmark Tool - Source Code (`src`)

This directory contains the core Python source code for the Elasticsearch Benchmark Tool.

## Overview

The scripts in this directory provide the functionality to connect to an Elasticsearch instance, ingest data from a file, and optionally run search queries to benchmark performance. The tool is designed to be run via the command line.

## Files

-   **`__init__.py`**: Makes the `src` directory a Python package.
-   **`cli.py`**: The main command-line interface entry point. It uses `argparse` to parse user arguments, initializes the Elasticsearch client, and calls the benchmarking functions.
-   **`es_client.py`**: Contains the `ElasticsearchClient` class, which handles the connection and interactions with the Elasticsearch cluster (creating indices, bulk ingestion, searching) using the official `elasticsearch` library. It supports basic authentication and API key authentication.
-   **`benchmark.py`**: (Requires Implementation) Intended to contain the core logic for running the ingestion and query benchmarks, including timing operations and calculating results (e.g., docs/sec, query latency). The `cli.py` script imports `run_ingestion` and `run_queries` from this module.
-   **`requirements.txt`**: Lists the Python dependencies.

## Dependencies

-   **`elasticsearch`**: The official Python client for Elasticsearch.
-   **`argparse`**: Used for command-line argument parsing (part of the standard Python library).

*Note:* The `requirements.txt` file also lists `requests`, `pandas`, and `numpy`. These are **not** currently used by the provided code snippets (`cli.py`, `es_client.py`). They might be intended for future enhancements or can be removed if not needed.

## Running the Tool

The tool should be executed as a module from the parent directory (`elasticsearch-benchmark-tool`).

```bash
# Navigate to the elasticsearch-benchmark-tool directory
cd /home/brown/elastic-alternatives-benchmarks/benchmarks/elasticsearch-benchmark-tool

# Run the CLI module
python -m src.cli --host <your_es_host> --data-file <path_to_data.ndjson> [options]

```markdown
# Elasticsearch Benchmark Tool - Source Code (`src`)

This directory contains the core Python source code for the Elasticsearch Benchmark Tool.

## Overview

The scripts in this directory provide the functionality to connect to an Elasticsearch instance, ingest data from a file, and optionally run search queries to benchmark performance. The tool is designed to be run via the command line.

## Files

-   **`__init__.py`**: Makes the `src` directory a Python package.
-   **`cli.py`**: The main command-line interface entry point. It uses `argparse` to parse user arguments, initializes the Elasticsearch client, and calls the benchmarking functions.
-   **`es_client.py`**: Contains the `ElasticsearchClient` class, which handles the connection and interactions with the Elasticsearch cluster (creating indices, bulk ingestion, searching) using the official `elasticsearch` library. It supports basic authentication and API key authentication.
-   **`benchmark.py`**: (Requires Implementation) Intended to contain the core logic for running the ingestion and query benchmarks, including timing operations and calculating results (e.g., docs/sec, query latency). The `cli.py` script imports `run_ingestion` and `run_queries` from this module.
-   **`requirements.txt`**: Lists the Python dependencies.

## Dependencies

-   **`elasticsearch`**: The official Python client for Elasticsearch.
-   **`argparse`**: Used for command-line argument parsing (part of the standard Python library).

*Note:* The `requirements.txt` file also lists `requests`, `pandas`, and `numpy`. These are **not** currently used by the provided code snippets (`cli.py`, `es_client.py`). They might be intended for future enhancements or can be removed if not needed.

## Running the Tool

The tool should be executed as a module from the parent directory (`elasticsearch-benchmark-tool`).

```bash
# Navigate to the elasticsearch-benchmark-tool directory
cd /home/brown/elastic-alternatives-benchmarks/benchmarks/elasticsearch-benchmark-tool

# Run the CLI module
python -m src.cli --host <your_es_host> --data-file <path_to_data.ndjson> [options]
```

## Command-Line Interface (`cli.py`)

The cli.py script accepts the following arguments:

| Argument           | Description                                                                                                | Default         | Required |
| :----------------- | :--------------------------------------------------------------------------------------------------------- | :-------------- | :------- |
| `--host HOST`      | Hostname or IP address of the Elasticsearch instance.                                                      | `None`          | **Yes**  |
| `--port PORT`      | Port number for the Elasticsearch instance.                                                                | `9200`          | No       |
| `--index-name IDX` | Name of the Elasticsearch index to use for ingestion/searching. Will be created if it doesn't exist.       | `logs`          | No       |
| `--data-file FILE` | Path to the **NDJSON** file containing log data for ingestion.                                             | `None`          | **Yes**  |
| `--queries-file QF`| (Optional) Path to a file with search queries (one per line). Enables the search benchmark after ingestion. | `None`          | No       |
| `--batch-size SIZE`| Number of documents per bulk indexing request.                                                             | `1000`          | No       |

## Authentication

The es_client.py class supports connecting using basic authentication (username/password) or an API key. However, the cli.py script **does not currently parse command-line arguments for these credentials**.

To enable authentication via the command line:

1.  **Modify cli.py:** Add arguments for `--user`, `--password`, and/or `--api-key` using `parser.add_argument(...)`.
2.  **Pass Credentials:** Update the `ElasticsearchClient` initialization in cli.py to pass the parsed arguments:
    ```python
    # Example modification in cli.py's main() function
    client = ElasticsearchClient(
        host=args.host,
        port=args.port,
        user=args.user,      # Pass the parsed user argument
        password=args.password, # Pass the parsed password argument
        api_key=args.api_key   # Pass the parsed api_key argument
    )
    ```

## Benchmark Logic (`benchmark.py`)

The actual benchmarking logic (timing ingestion and queries, calculating rates/latencies) resides in the `run_ingestion` and `run_queries` functions within `benchmark.py`. The provided cli.py calls these functions, but their implementation needs to be completed in `benchmark.py` to provide meaningful performance metrics beyond basic execution.

## Input Data

-   **`--data-file`**: Must point to a file in **NDJSON** format (one valid JSON object per line).
-   **`--queries-file`**: Should be a plain text file where each line contains a single query string. The `es_client.search` method currently expects a dictionary representing the Elasticsearch query body; the `run_queries` function in `benchmark.py` would need to parse the lines from this file and construct appropriate query dictionaries.

## Output

The cli.py script currently prints basic information about the results returned by the (partially implemented) `run_ingestion` and `run_queries` functions. A complete implementation in `benchmark.py` should return detailed metrics (e.g., total time, docs/sec, average latency) which can then be printed by cli.py.
