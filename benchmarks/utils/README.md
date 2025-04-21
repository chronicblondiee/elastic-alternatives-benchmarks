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

-   Reads connection details (`ES_HOST`, `ES_PORT`, `ELASTIC_USER`, `ELASTIC_PASSWORD`, `ES_API_KEY`) and benchmark parameters (`ES_INDEX_NAME`, `ES_DATA_FILE`, `ES_QUERIES_FILE`, `ES_BATCH_SIZE`) from environment variables.
-   Allows overriding these settings via command-line arguments.
-   Constructs and executes the `python -m src.cli` command with the appropriate arguments.
-   Requires the Python virtual environment for the benchmark tool to be activated.

### Prerequisites

-   The Python virtual environment for the `elasticsearch-benchmark-tool` must be set up (see `../elasticsearch-benchmark-tool/README.md`).
-   The `elasticsearch-benchmark-tool/src/cli.py` script should ideally be modified to accept `--user`, `--password`, and `--api-key` arguments if authentication is needed.

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
        # export ES_QUERIES_FILE="../elasticsearch-benchmark-tool/scripts/queries.txt"
        # export ES_BATCH_SIZE=500
        ```
    *   **Or set manually:**
        ```bash
        export ES_HOST="manual-host.example.com"
        export ES_PORT="9200"
        export ELASTIC_USER="myuser"
        export ELASTIC_PASSWORD="mypassword"
        export ES_INDEX_NAME="manual_index"
        export ES_DATA_FILE="/absolute/path/to/data.ndjson"
        # export ES_API_KEY="myapikey"
        # export ES_QUERIES_FILE="/path/to/queries.txt"
        # export ES_BATCH_SIZE=1000
        ```
4.  **Run the Benchmark Script:**
    *   **Using environment variables/defaults:**
        ```bash
        ./run-elasticsearch-benchmark.sh
        ```
    *   **Overriding some parameters via command line:**
        ```bash
        ./run-elasticsearch-benchmark.sh -h localhost -p 9201 -i test_index -b 2000 -q ../elasticsearch-benchmark-tool/scripts/queries.txt
        ```
    *   **Specifying credentials via arguments (if env vars not set and Python script modified):**
        ```bash
        ./run-elasticsearch-benchmark.sh -h localhost -U someuser -P somepass -d ../elasticsearch-benchmark-tool/scripts/generated_logs.ndjson
        ```

This script provides a flexible way to configure and repeat your benchmark runs.