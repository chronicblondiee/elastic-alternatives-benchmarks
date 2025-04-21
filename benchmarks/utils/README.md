# Benchmark Utility Scripts

This directory contains utility scripts to help set up the environment and run benchmarks, particularly for Elasticsearch deployed via ECK (Elastic Cloud on Kubernetes).

## `setup-elasticsearch-env-vars.sh`

This script automates the process of retrieving connection details for an Elasticsearch cluster managed by ECK and exporting them as environment variables in your current shell session.

### Purpose

-   Retrieves the default `elastic` user password from its Kubernetes secret.
-   Retrieves the LoadBalancer IP/Hostname assigned to the Elasticsearch HTTP service.
-   Retrieves the port number for the Elasticsearch HTTP service.
-   Exports the following environment variables:
    -   `ELASTIC_USER` (set to `elastic`)
    -   `ELASTIC_PASSWORD` (the retrieved password)
    -   `ES_HOST` (the LoadBalancer IP or Hostname)
    -   `ES_PORT` (the service port)

### Prerequisites

-   `kubectl` installed and configured to access your Kubernetes cluster.
-   An Elasticsearch cluster deployed using ECK, with its associated secrets and services created.

### How to Use

1.  **Navigate** to the `utils` directory:
    ```bash
    cd /home/brown/elastic-alternatives-benchmarks/benchmarks/utils
    ```
2.  **Source the script:** You **must** use the `source` command (or the `.` shortcut) for the exported variables to be available in your current shell.
    *   **Using defaults** (Namespace: `elastic`, Cluster Name: `elasticsearch`, Timeout: 180s):
        ```bash
        source ./setup-elasticsearch-env-vars.sh
        ```
    *   **Specifying namespace, cluster name, and timeout:**
        ```bash
        source ./setup-elasticsearch-env-vars.sh -n my-elastic-namespace -c my-es-cluster -t 300
        ```
3.  **Verify:** Check if the environment variables are set:
    ```bash
    echo $ELASTIC_USER
    echo $ELASTIC_PASSWORD
    echo $ES_HOST
    echo $ES_PORT
    ```

Now you can use these variables in subsequent commands, such as the `run-elasticsearch-benchmark.sh` script.

## `run-elasticsearch-benchmark.sh`

This script acts as a wrapper to execute the Python-based Elasticsearch benchmark tool located in `../elasticsearch-benchmark-tool`. It simplifies running benchmarks by utilizing environment variables for configuration, while also allowing command-line overrides.

### Purpose

-   Reads connection details (`ES_HOST`, `ES_PORT`, `ELASTIC_USER`, `ELASTIC_PASSWORD`, `ES_API_KEY`, `ES_SCHEME`, `ES_VERIFY_CERTS`) and benchmark parameters (`ES_INDEX_NAME`, `ES_DATA_FILE`, `ES_QUERIES_FILE`, `ES_BATCH_SIZE`) from environment variables.
-   Allows overriding these settings via command-line arguments (e.g., `--scheme`, `--no-verify-certs`).
-   Supports different modes:
    -   **Default:** Runs data ingestion, followed by query benchmarking (if a queries file is provided).
    -   **Query Only (`--query-only`):** Skips ingestion and runs only the query benchmark (requires a queries file).
-   Constructs and executes the `python -m src.cli` command with the appropriate arguments.
-   Requires the Python virtual environment for the benchmark tool to be activated.

### Prerequisites

-   The Python virtual environment for the `elasticsearch-benchmark-tool` must be set up (see `../elasticsearch-benchmark-tool/README.md`).
-   The `elasticsearch-benchmark-tool/src/cli.py` script must support the arguments passed by this wrapper (including `--query-only`, `--user`, `--password`, `--api-key`, etc.).

### How to Use

1.  **Activate Python Environment:** Navigate to the benchmark tool directory and activate its virtual environment.
    ```bash
    cd /home/brown/elastic-alternatives-benchmarks/benchmarks/elasticsearch-benchmark-tool
    source .venv/bin/activate
    ```
2.  **Navigate back to `utils`:**
    ```bash
    cd ../utils
    ```
3.  **Set Environment Variables (Recommended):**
    *   **Using the setup script (Recommended for ECK):**
        ```bash
        source ./setup-elasticsearch-env-vars.sh # Use options if needed (-n, -c, -t)
        # Optionally set other benchmark parameters
        export ES_INDEX_NAME="my_benchmark_run"
        export ES_DATA_FILE="../elasticsearch-benchmark-tool/scripts/generated_logs.ndjson"
        export ES_QUERIES_FILE="../elasticsearch-benchmark-tool/scripts/generated_queries.txt"
        # export ES_BATCH_SIZE=500
        # Note: For ECK with default certs, you'll likely need --scheme https --no-verify-certs
        ```
    *   **Or set manually:**
        ```bash
        export ES_HOST="manual-host.example.com"
        export ES_PORT="9200"
        export ES_SCHEME="https" # Set scheme if not http
        export ES_VERIFY_CERTS="false" # Set if using self-signed certs
        export ELASTIC_USER="myuser"
        export ELASTIC_PASSWORD="mypassword"
        export ES_INDEX_NAME="manual_index"
        export ES_DATA_FILE="/absolute/path/to/data.ndjson"
        export ES_QUERIES_FILE="/path/to/queries.txt"
        # export ES_API_KEY="myapikey"
        # export ES_BATCH_SIZE=1000
        ```
4.  **Run the Benchmark Script:**
    *   **Default Mode (Ingestion + Queries, Example for ECK with HTTPS/Self-Signed Certs):**
        ```bash
        # Assumes ES_DATA_FILE and ES_QUERIES_FILE are set in environment
        ./run-elasticsearch-benchmark.sh --scheme https --no-verify-certs
        ```
    *   **Default Mode (Ingestion Only):**
        ```bash
        # Unset or don't provide ES_QUERIES_FILE or -q argument
        ./run-elasticsearch-benchmark.sh --scheme https --no-verify-certs -d ../elasticsearch-benchmark-tool/scripts/generated_logs.ndjson
        ```
    *   **Query Only Mode:**
        ```bash
        # Requires -q or ES_QUERIES_FILE to be set
        ./run-elasticsearch-benchmark.sh --scheme https --no-verify-certs --query-only -q ../elasticsearch-benchmark-tool/scripts/generated_queries.txt
        ```
    *   **Overriding some parameters via command line (Default Mode):**
        ```bash
        ./run-elasticsearch-benchmark.sh --scheme https --no-verify-certs -h localhost -p 9201 -i test_index -b 2000 -d ../data/small.ndjson -q ../queries/basic.txt
        ```
    *   **Specifying credentials via arguments (Query Only Mode):**
        ```bash
        ./run-elasticsearch-benchmark.sh --scheme https --no-verify-certs -h localhost -U someuser -P somepass --query-only -q ../queries/complex.txt
        ```

This script provides a flexible way to configure and repeat your benchmark runs.

### Debugging with `curl`

If you encounter connection or ingestion errors (especially related to headers or authentication) when using the Python script, you can test the Elasticsearch bulk endpoint directly using `curl`. This bypasses the Python library and helps isolate server-side or network issues.

1.  **Create Test Data:** Create a file named `bulk_test.ndjson` in the `utils` directory with the following content. **Ensure there is a newline character at the very end of the file.**
    ```ndjson
    {"index": {"_index": "my_benchmark_run"}}
    {"message": "Test document 1", "@timestamp": "2025-04-21T22:30:00Z"}
    {"index": {"_index": "my_benchmark_run"}}
    {"message": "Test document 2", "@timestamp": "2025-04-21T22:30:01Z"}

    ```
    *(Note the blank line at the end)*

2.  **Run `curl` Command:** Execute the following command, replacing `YOUR_PASSWORD`, `YOUR_HOST`, and `YOUR_PORT` with the actual values (or use the environment variables if set via `setup-elasticsearch-env-vars.sh`).
    ```bash
    # Replace placeholders or use environment variables
    ES_HOST_VAL=${ES_HOST:-YOUR_HOST}
    ES_PORT_VAL=${ES_PORT:-YOUR_PORT}
    ELASTIC_PASSWORD_VAL=${ELASTIC_PASSWORD:-YOUR_PASSWORD}

    curl -k -u "elastic:${ELASTIC_PASSWORD_VAL}" \
         -X POST "https://${ES_HOST_VAL}:${ES_PORT_VAL}/_bulk" \
         -H "Content-Type: application/x-ndjson" \
         --data-binary "@bulk_test.ndjson"
    ```
    *   `-k`: Allows insecure connections (like `--no-verify-certs`).
    *   `-u "elastic:..."`: Provides basic authentication.
    *   `-X POST`: Specifies the HTTP method.
    *   `-H "Content-Type: application/x-ndjson"`: Sets the required header.
    *   `--data-binary "@bulk_test.ndjson"`: Sends the file content.

3.  **Interpret Results:**
    *   **Success:** A JSON response with `"errors":false` indicates the server accepted the request, headers, and data format. The issue likely lies within the Python script or its libraries.
    *   **Failure:**
        *   `400 Bad Request` with `media_type_header_exception`: Suggests something (like a proxy) might still be interfering with the `Content-Type` header even for `curl`.
        *   `400 Bad Request` with `illegal_argument_exception` (e.g., missing newline): Indicates the data in `bulk_test.ndjson` is malformed.
        *   `401 Unauthorized`: Authentication failed (check username/password).
        *   `405 Method Not Allowed`: Incorrect URL path used.
        *   Connection errors: Network issues or incorrect host/port.