#!/bin/bash

# --- Configuration (Defaults & Environment Variable Checks) ---

# Get the directory where this script is located
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Assume the script is in benchmarks/utils, navigate to the benchmark tool directory
BENCHMARK_TOOL_DIR="${SCRIPT_DIR}/../elasticsearch-benchmark-tool"

# Elasticsearch Connection
ES_HOST="${ES_HOST:-localhost}" # Default to localhost if ES_HOST is not set
ES_PORT="${ES_PORT:-9200}"      # Default to 9200 if ES_PORT is not set
ES_SCHEME="${ES_SCHEME:-http}" # Default scheme
ES_VERIFY_CERTS="${ES_VERIFY_CERTS:-true}" # Default to verify certs

# ELASTIC_USER and ELASTIC_PASSWORD should be set by sourcing extract-elastic-secrets.sh or manually
ES_USER="${ELASTIC_USER:-}"     # Default to empty if ELASTIC_USER is not set
ES_PASSWORD="${ELASTIC_PASSWORD:-}" # Default to empty if ELASTIC_PASSWORD is not set
ES_API_KEY="${ES_API_KEY:-}"    # Default to empty if ES_API_KEY is not set

# Benchmark Parameters
ES_INDEX_NAME="${ES_INDEX_NAME:-benchmark_logs}" # Default index name
# Default data file relative to the benchmark tool directory
DEFAULT_DATA_FILE="${BENCHMARK_TOOL_DIR}/scripts/generated_logs.ndjson"
ES_DATA_FILE="${ES_DATA_FILE:-$DEFAULT_DATA_FILE}"
# Default queries file relative to the benchmark tool directory
DEFAULT_QUERIES_FILE="${BENCHMARK_TOOL_DIR}/scripts/generated_queries.txt"
ES_QUERIES_FILE="${ES_QUERIES_FILE:-}" # Default to empty (no query benchmark)
ES_BATCH_SIZE="${ES_BATCH_SIZE:-1000}" # Default batch size
QUERY_ONLY_MODE="false" # Default to run ingestion + queries

# --- Functions ---
usage() {
  echo "Usage: $0 [-h <host>] [-p <port>] [--scheme <scheme>] [--no-verify-certs] [-i <index>] [-d <data_file>] [-q <queries_file>] [-b <batch_size>] [-U <user>] [-P <password>] [-K <api_key>] [--query-only] [--help]"
  echo ""
  echo "  Runs the Python Elasticsearch benchmark tool using environment variables and optional overrides."
  echo "  Ensure the Python virtual environment for the tool is activated before running."
  echo "  Set environment variables (e.g., ES_HOST, ES_PORT, ES_SCHEME, ELASTIC_USER, ELASTIC_PASSWORD) for configuration."
  echo ""
  echo "  Modes:"
  echo "    Default:          Run ingestion benchmark, then query benchmark (if -q is specified)."
  echo "    --query-only:     Run only the query benchmark (requires -q)."
  echo ""
  echo "  Options (override environment variables):"
  echo "    -h <host>:         Elasticsearch host (default: \$ES_HOST or '$ES_HOST')"
  echo "    -p <port>:         Elasticsearch port (default: \$ES_PORT or '$ES_PORT')"
  echo "    --scheme <scheme>: Connection scheme (http or https, default: \$ES_SCHEME or '$ES_SCHEME')"
  echo "    --no-verify-certs: Disable SSL certificate verification (sets ES_VERIFY_CERTS=false)"
  echo "    -i <index>:        Index name (default: \$ES_INDEX_NAME or '$ES_INDEX_NAME')"
  echo "    -d <data_file>:    Path to NDJSON data file (required unless --query-only, default: \$ES_DATA_FILE or '$ES_DATA_FILE')"
  echo "    -q <queries_file>: Path to queries file (required for query benchmark, default: \$ES_QUERIES_FILE or none, e.g., '$DEFAULT_QUERIES_FILE')"
  echo "    -b <batch_size>:   Ingestion batch size (ignored if --query-only, default: \$ES_BATCH_SIZE or '$ES_BATCH_SIZE')"
  echo "    -U <user>:         Elasticsearch user (default: \$ELASTIC_USER or none)"
  echo "    -P <password>:     Elasticsearch password (default: \$ELASTIC_PASSWORD or none)"
  echo "    -K <api_key>:      Elasticsearch API key (default: \$ES_API_KEY or none)"
  echo "    --query-only:      Run only the query benchmark (requires -q)."
  echo "    --help:            Display this help message"
  exit 1
}

# --- Argument Parsing ---
VERIFY_CERTS_FLAG=""
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -h) ES_HOST="$2"; shift; shift ;;
    -p) ES_PORT="$2"; shift; shift ;;
    --scheme) ES_SCHEME="$2"; shift; shift ;;
    --no-verify-certs) ES_VERIFY_CERTS="false"; VERIFY_CERTS_FLAG="--no-verify-certs"; shift ;;
    -i) ES_INDEX_NAME="$2"; shift; shift ;;
    -d) ES_DATA_FILE="$2"; shift; shift ;;
    -q) ES_QUERIES_FILE="$2"; shift; shift ;;
    -b) ES_BATCH_SIZE="$2"; shift; shift ;;
    -U) ES_USER="$2"; shift; shift ;;
    -P) ES_PASSWORD="$2"; shift; shift ;;
    -K) ES_API_KEY="$2"; shift; shift ;;
    --query-only) QUERY_ONLY_MODE="true"; shift ;; # Set query only mode
    --help) usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

# --- Validation ---
if [[ -z "$ES_HOST" ]]; then
  echo "Error: Elasticsearch host is required. Set ES_HOST environment variable or use -h option." >&2
  exit 1
fi
if [[ "$ES_SCHEME" != "http" && "$ES_SCHEME" != "https" ]]; then
    echo "Error: Invalid scheme '$ES_SCHEME'. Must be 'http' or 'https'." >&2
    exit 1
fi
if [[ "$ES_SCHEME" == "http" && "$ES_VERIFY_CERTS" == "false" ]]; then
    echo "Warning: --no-verify-certs is only applicable for https scheme." >&2
fi

# Data file validation depends on mode
if [[ "$QUERY_ONLY_MODE" == "false" && ! -f "$ES_DATA_FILE" ]]; then
  echo "Error: Data file not found at '$ES_DATA_FILE'. Set ES_DATA_FILE or use -d option." >&2
  exit 1
elif [[ "$QUERY_ONLY_MODE" == "true" && -z "$ES_QUERIES_FILE" ]]; then
  echo "Error: Queries file (-q) is required when using --query-only mode." >&2
  exit 1
fi

# Queries file validation
if [[ -n "$ES_QUERIES_FILE" && ! -f "$ES_QUERIES_FILE" ]]; then
  echo "Error: Queries file specified but not found at '$ES_QUERIES_FILE'." >&2
  exit 1
fi

if ! command -v python &> /dev/null; then
    echo "Error: 'python' command not found. Is the virtual environment activated?" >&2
    exit 1
fi
# Check if the benchmark tool's cli.py exists
if [[ ! -f "${BENCHMARK_TOOL_DIR}/src/cli.py" ]]; then
    echo "Error: Benchmark script not found at ${BENCHMARK_TOOL_DIR}/src/cli.py" >&2
    exit 1
fi


# --- Construct Python Command ---
PYTHON_CMD="python -m src.cli"
PYTHON_CMD+=" --host \"$ES_HOST\""
PYTHON_CMD+=" --port \"$ES_PORT\""
PYTHON_CMD+=" --scheme \"$ES_SCHEME\""
PYTHON_CMD+=" --index-name \"$ES_INDEX_NAME\""

# Add data file and batch size only if NOT in query-only mode
if [[ "$QUERY_ONLY_MODE" == "false" ]]; then
    PYTHON_CMD+=" --data-file \"$ES_DATA_FILE\""
    PYTHON_CMD+=" --batch-size \"$ES_BATCH_SIZE\""
fi

# Add optional arguments
if [[ -n "$ES_QUERIES_FILE" ]]; then
  PYTHON_CMD+=" --queries-file \"$ES_QUERIES_FILE\""
fi
if [[ "$ES_VERIFY_CERTS" == "false" ]]; then
    PYTHON_CMD+=" $VERIFY_CERTS_FLAG"
fi
# Add query-only flag if set
if [[ "$QUERY_ONLY_MODE" == "true" ]]; then
    PYTHON_CMD+=" --query-only" # Pass flag to Python script
fi


# --- Authentication Handling ---
# NOTE: This assumes the elasticsearch-benchmark-tool/src/cli.py has been modified
# to accept --user, --password, and --api-key arguments as described in its README.
AUTH_ARGS=""
if [[ -n "$ES_API_KEY" ]]; then
    AUTH_ARGS+=" --api-key \"$ES_API_KEY\""
    echo "Using API Key authentication." >&2
elif [[ -n "$ES_USER" && -n "$ES_PASSWORD" ]]; then
    AUTH_ARGS+=" --user \"$ES_USER\""
    AUTH_ARGS+=" --password \"$ES_PASSWORD\""
    echo "Using User/Password authentication for user '$ES_USER'." >&2
elif [[ -n "$ES_USER" || -n "$ES_PASSWORD" ]]; then
    echo "Warning: Both user and password must be provided for basic authentication. Ignoring." >&2
fi

PYTHON_CMD+="$AUTH_ARGS"

# --- Execute Benchmark ---
echo "--- Running Elasticsearch Benchmark ---"
if [[ "$QUERY_ONLY_MODE" == "true" ]]; then
    echo "Mode: Query Only"
else
    echo "Mode: Ingestion + Query (if specified)"
fi
echo "Scheme: $ES_SCHEME"
echo "Host: $ES_HOST:$ES_PORT"
echo "Verify Certs: $ES_VERIFY_CERTS"
echo "Index: $ES_INDEX_NAME"
if [[ "$QUERY_ONLY_MODE" == "false" ]]; then
    echo "Data File: $ES_DATA_FILE"
    echo "Batch Size: $ES_BATCH_SIZE"
fi
[[ -n "$ES_QUERIES_FILE" ]] && echo "Queries File: $ES_QUERIES_FILE"
echo "Executing command:"
echo "$PYTHON_CMD"
echo "---------------------------------------"

# Execute from the benchmark tool's directory
(cd "$BENCHMARK_TOOL_DIR" && eval "$PYTHON_CMD")

EXIT_CODE=$?
echo "---------------------------------------"
if [[ $EXIT_CODE -eq 0 ]]; then
  echo "Benchmark finished successfully."
else
  echo "Benchmark finished with errors (Exit Code: $EXIT_CODE)."
fi

exit $EXIT_CODE