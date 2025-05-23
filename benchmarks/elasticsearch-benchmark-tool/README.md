# Elasticsearch Benchmark Tool

This tool provides a command-line interface to benchmark the indexing and search performance of an Elasticsearch instance. It allows you to ingest log data from a file and optionally run search queries against the indexed data, measuring the time taken for each operation.

## Features

-   Connects to a specified Elasticsearch instance (supports basic auth and API key via code modification).
-   Ingests log data from a provided file (**NDJSON format required**).
-   Performs bulk indexing with configurable batch sizes.
-   Optionally runs search queries from a file against the indexed data.
-   Measures and reports ingestion rate (docs/sec) and query latency (requires implementation in `benchmark.py`).

## Prerequisites

-   **Python:** Version 3.8 or higher (including `python3-venv` package or equivalent).
-   **Elasticsearch Instance:** An accessible Elasticsearch cluster (local or remote).
-   **Log Data File:** A file containing log data in **NDJSON format** (one valid JSON object per line).
-   **(Optional) Query File:** A text file containing search queries, one per line.

## Setup

1.  **Obtain the Code:** Clone the repository or download the source code files (`src/cli.py`, `src/benchmark.py`, `src/es_client.py`, etc.).
2.  **Navigate to Directory:** Open your terminal and change into the main directory of the tool:
    ```bash
    cd /path/to/elasticsearch-benchmark-tool
    ```
3.  **Create Virtual Environment:** Create an isolated Python environment for the tool's dependencies. This is recommended to avoid conflicts with other Python projects.
    ```bash
    python3 -m venv .venv
    ```
4.  **Activate Virtual Environment:** Activate the environment in your current shell session. Your prompt should change to indicate the active environment (e.g., `(.venv) your-prompt$`).
    ```bash
    source .venv/bin/activate
    # On Windows use: .\.venv\Scripts\activate
    ```
5.  **Install Dependencies:** Install the necessary Python libraries into the active virtual environment using the provided requirements file.
    ```bash
    pip install -r src/requirements.txt
    ```
    *(Note: The `src/requirements.txt` file might list additional libraries like `pandas` or `numpy`. Only `elasticsearch` and `argparse` (standard library) are strictly required by the core scripts provided. You can adjust `src/requirements.txt` if needed.)*

## Usage

**Important:** Ensure the virtual environment is activated (`source .venv/bin/activate`) before running the tool.

Execute the benchmark tool from its main directory using the Python module execution flag (`-m`).

### Basic Command Structure

```bash
python -m src.cli --host <your_es_host> --data-file <path_to_log_file.ndjson> [options]
```

### Command-Line Arguments

| Argument           | Description                                                                                                | Default         | Required |
| :----------------- | :--------------------------------------------------------------------------------------------------------- | :-------------- | :------- |
| `--host HOST`      | Hostname or IP address of the Elasticsearch instance.                                                      | `None`          | **Yes**  |
| `--port PORT`      | Port number for the Elasticsearch instance.                                                                | `9200`          | No       |
| `--index-name IDX` | Name of the Elasticsearch index to use for ingestion/searching. Will be created if it doesn't exist.       | `logs`          | No       |
| `--data-file FILE` | Path to the **NDJSON** file containing log data for ingestion.                                             | `None`          | **Yes**  |
| `--queries-file QF`| (Optional) Path to a file with search queries (one per line). Enables the search benchmark after ingestion. | `None`          | No       |
| `--batch-size SIZE`| Number of documents per bulk indexing request.                                                             | `1000`          | No       |

### Authentication

The underlying `es_client.py` supports basic authentication (`user`/`password`) and API key authentication. However, the main `cli.py` script **does not currently accept arguments for these credentials**.

To use authentication:

1.  **Modify `src/cli.py`:**
    *   Add arguments to the `argparse.ArgumentParser` for `--user`, `--password`, and/or `--api-key`.
    *   Example:
        ```python
        parser.add_argument("--user", help="Username for basic authentication")
        parser.add_argument("--password", help="Password for basic authentication")
        parser.add_argument("--api-key", help="API key for authentication")
        ```
2.  **Update Client Initialization:** In `src/cli.py`, pass the parsed authentication arguments when creating the `ElasticsearchClient` instance:
    ```python
    # Inside main() function in cli.py
    client = ElasticsearchClient(
        host=args.host,
        port=args.port,
        user=args.user,      # Pass the parsed user
        password=args.password, # Pass the parsed password
        api_key=args.api_key   # Pass the parsed api_key
    )
    ```

### Examples

*(Ensure virtual environment is active before running)*

1.  **Basic Ingestion:** Ingest data into the default `logs` index on `localhost:9200`.
    ```bash
    python -m src.cli --host localhost --data-file ./data/sample_logs.ndjson
    ```

2.  **Ingestion with Custom Index and Batch Size:** Ingest data into the `my-app-logs` index on a specific host, using a batch size of 500.
    ```bash
    python -m src.cli \
        --host es.example.com \
        --port 9201 \
        --index-name my-app-logs \
        --data-file /path/to/your/logs.ndjson \
        --batch-size 500
    ```

3.  **Ingestion and Search Benchmark:** Ingest data and then run search queries from a file.
    ```bash
    python -m src.cli \
        --host localhost \
        --data-file ./data/logs.ndjson \
        --queries-file ./data/queries.txt \
        --index-name benchmark-run-01
    ```

4.  **Authenticated Ingestion (After Modifying `cli.py`):**
    ```bash
    python -m src.cli \
        --host secure-es.internal \
        --user elastic \
        --password yoursecurepassword \
        --data-file ./secure_logs.ndjson \
        --index-name secure-index
    ```

## Input Data Formats

-   **Log Data (`--data-file`):**
    *   **Format:** NDJSON (Newline Delimited JSON).
    *   **Requirement:** Each line *must* be a single, complete, valid JSON object.
    *   **Example (`logs.ndjson`):**
        ```json
        {"timestamp": "2025-04-21T10:00:01.123Z", "level": "INFO", "message": "User logged in", "user_id": "usr-123", "source_ip": "192.168.1.100"}
        {"timestamp": "2025-04-21T10:00:02.456Z", "level": "WARN", "message": "Disk space low", "service": "monitor", "free_gb": 5.2}
        {"timestamp": "2025-04-21T10:00:03.789Z", "level": "ERROR", "message": "Failed to connect to database", "service": "auth-service", "error_code": 503}
        ```

-   **Query Data (`--queries-file`):**
    *   **Format:** Plain text file.
    *   **Requirement:** Each line contains one search query string. The interpretation of this string depends on the `run_queries` implementation in `benchmark.py`. The current examples assume simple text searches.
    *   **Example (`queries.txt`):**
        ```
        "Disk space low"
        ERROR
        user_id:usr-123
        "Failed to connect"
        ```

## Output

The tool prints progress and results to the console:

-   Connection details.
-   Confirmation of index creation or existence check.
-   **Ingestion:**
    *   Progress messages (e.g., number of documents ingested).
    *   Total documents processed.
    *   Total errors encountered during ingestion.
    *   Total time taken for ingestion.
    *   Calculated ingestion rate (documents per second).
-   **Searching (if `--queries-file` is used):**
    *   Progress messages for each query executed.
    *   Total queries executed.
    *   Total errors encountered during search.
    *   Average, minimum, and maximum query latency in seconds.
    *   (Potentially) Percentile latencies (e.g., P95, P99) if implemented.

## Sample Data Generation

A utility script `scripts/generate_log_data.sh` is included to generate sample NDJSON data.

-   **Purpose:** Generates sample log lines in NDJSON format suitable for the `--data-file` argument.
-   **Usage:** See `scripts/README.md` for details.
    ```bash
    # Example: Generate 10000 lines into scripts/generated_logs.ndjson
    bash ./scripts/generate_log_data.sh -n 10000 -o ./scripts/generated_logs.ndjson
    ```

## Deactivating the Environment

When you are finished using the tool, you can deactivate the virtual environment:
```bash
deactivate
```
