# NDJSON Log Data Generator (`generate_log_data.sh`)

This Bash script generates sample log data in NDJSON (Newline Delimited JSON) format. Each line in the output file is a valid JSON object representing a simulated log entry. This format is suitable for bulk ingestion into systems like Elasticsearch.

## Features

-   Generates a specified number of log entries.
-   Outputs data in NDJSON format.
-   Includes randomized fields: timestamp, log level, message, user ID, and source IP.
-   Allows customization of the number of lines and the output file name via command-line arguments.
-   Includes basic escaping for double quotes within generated messages.

## Prerequisites

-   A Bash-compatible shell environment (Linux, macOS, WSL on Windows).
-   Standard Unix utilities like `date`, `printf`, `head`, `tr`.

## Output Format

Each line in the output file is a JSON object with the following structure:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS.mmmZ", // ISO 8601 format in UTC
  "level": "LOG_LEVEL",                   // Randomly chosen from INFO, WARN, ERROR, DEBUG, TRACE
  "message": "Random log message text",     // Randomly chosen message, with internal quotes escaped
  "user_id": "usr-XXX",                   // Randomly generated user ID (e.g., usr-1 to usr-1000)
  "source_ip": "X.X.X.X"                    // Randomly generated IPv4 address
}

```markdown
# NDJSON Log Data Generator (`generate_log_data.sh`)

This Bash script generates sample log data in NDJSON (Newline Delimited JSON) format. Each line in the output file is a valid JSON object representing a simulated log entry. This format is suitable for bulk ingestion into systems like Elasticsearch.

## Features

-   Generates a specified number of log entries.
-   Outputs data in NDJSON format.
-   Includes randomized fields: timestamp, log level, message, user ID, and source IP.
-   Allows customization of the number of lines and the output file name via command-line arguments.
-   Includes basic escaping for double quotes within generated messages.

## Prerequisites

-   A Bash-compatible shell environment (Linux, macOS, WSL on Windows).
-   Standard Unix utilities like `date`, `printf`, `head`, `tr`.

## Output Format

Each line in the output file is a JSON object with the following structure:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS.mmmZ", // ISO 8601 format in UTC
  "level": "LOG_LEVEL",                   // Randomly chosen from INFO, WARN, ERROR, DEBUG, TRACE
  "message": "Random log message text",     // Randomly chosen message, with internal quotes escaped
  "user_id": "usr-XXX",                   // Randomly generated user ID (e.g., usr-1 to usr-1000)
  "source_ip": "X.X.X.X"                    // Randomly generated IPv4 address
}
```

**Example Line:**

```json
{"timestamp": "2025-04-21T15:30:45.123Z", "level": "WARN", "message": "Memory usage high", "user_id": "usr-542", "source_ip": "192.168.10.5"}
```

## Usage

Run the script from your terminal.

```bash
bash generate_log_data.sh [options]
```

### Options

-   `-n <number_of_lines>`: Specifies the total number of log lines (JSON objects) to generate.
    -   Default: `1000`
    -   Must be a positive integer.
-   `-o <output_file>`: Specifies the name of the output file where the NDJSON data will be saved.
    -   Default: `generated_logs.ndjson`
-   `-h`: Displays the usage instructions and exits.

### Examples

1.  **Generate default 1000 lines:**
    ```bash
    bash generate_log_data.sh
    # Output: Creates 'generated_logs.ndjson' with 1000 lines.
    ```

2.  **Generate 50,000 lines:**
    ```bash
    bash generate_log_data.sh -n 50000
    # Output: Creates 'generated_logs.ndjson' with 50,000 lines.
    ```

3.  **Generate 100 lines into a specific file:**
    ```bash
    bash generate_log_data.sh -n 100 -o my_test_data.ndjson
    # Output: Creates 'my_test_data.ndjson' with 100 lines.
    ```

4.  **Show help:**
    ```bash
    bash generate_log_data.sh -h
    ```

## Notes

-   The script overwrites the output file if it already exists.
-   Random data generation is basic and intended for generating load, not necessarily for simulating complex real-world log patterns.
-   The timestamp uses `date -u` to ensure UTC time.

```markdown
# Benchmark Tool Scripts

This directory contains helper scripts for generating test data and queries for the Elasticsearch benchmark tool.

# NDJSON Log Data Generator (`generate_log_data.sh`)

This Bash script generates sample log data in NDJSON (Newline Delimited JSON) format. Each line in the output file is a valid JSON object representing a simulated log entry. This format is suitable for bulk ingestion into systems like Elasticsearch.

## Features

-   Generates a specified number of log entries.
-   Outputs data in NDJSON format.
-   Includes randomized fields: timestamp, log level, message, user ID, and source IP.
-   Allows customization of the number of lines and the output file name via command-line arguments.
-   Includes basic escaping for double quotes within generated messages.

## Prerequisites

-   A Bash-compatible shell environment (Linux, macOS, WSL on Windows).
-   Standard Unix utilities like `date`, `printf`, `head`, `tr`.

## Output Format

Each line in the output file is a JSON object with the following structure:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS.mmmZ", // ISO 8601 format in UTC
  "level": "LOG_LEVEL",                   // Randomly chosen from INFO, WARN, ERROR, DEBUG, TRACE
  "message": "Random log message text",     // Randomly chosen message, with internal quotes escaped
  "user_id": "usr-XXX",                   // Randomly generated user ID (e.g., usr-1 to usr-1000)
  "source_ip": "X.X.X.X"                    // Randomly generated IPv4 address
}
```

**Example Line:**

```json
{"timestamp": "2025-04-21T15:30:45.123Z", "level": "WARN", "message": "Memory usage high", "user_id": "usr-542", "source_ip": "192.168.10.5"}
```

## Usage

Run the script from your terminal. Make sure it's executable (`chmod +x generate_log_data.sh`).

```bash
./generate_log_data.sh [options]
```

### Options

-   `-n <number_of_lines>`: Specifies the total number of log lines (JSON objects) to generate.
    -   Default: `1000`
    -   Must be a positive integer.
-   `-o <output_file>`: Specifies the name of the output file where the NDJSON data will be saved.
    -   Default: `generated_logs.ndjson`
-   `-h`: Displays the usage instructions and exits.

### Examples

1.  **Generate default 1000 lines:**
    ```bash
    ./generate_log_data.sh
    # Output: Creates 'generated_logs.ndjson' with 1000 lines.
    ```

2.  **Generate 50,000 lines:**
    ```bash
    ./generate_log_data.sh -n 50000
    # Output: Creates 'generated_logs.ndjson' with 50,000 lines.
    ```

3.  **Generate 100 lines into a specific file:**
    ```bash
    ./generate_log_data.sh -n 100 -o my_test_data.ndjson
    # Output: Creates 'my_test_data.ndjson' with 100 lines.
    ```

4.  **Show help:**
    ```bash
    ./generate_log_data.sh -h
    ```

## Notes

-   The script overwrites the output file if it already exists.
-   Random data generation is basic and intended for generating load, not necessarily for simulating complex real-world log patterns.
-   The timestamp uses `date -u` to ensure UTC time.

---

# Sample Query Generator (`generate_sample_querys.sh`)

This Bash script generates a file containing sample query strings, one per line, based on the fields typically found in the log data generated by `generate_log_data.sh`. These queries use a simple Lucene-like syntax.

## Features

-   Generates a specified number of query strings.
-   Outputs one query string per line.
-   Creates different types of queries (term, match, wildcard, boolean) targeting fields like `level`, `message`, `user_id`, and `source_ip`.
-   Allows customization of the number of queries and the output file name.

## Prerequisites

-   A Bash-compatible shell environment (Linux, macOS, WSL on Windows).

## Output Format

Each line in the output file is a single query string.

**Example Lines:**

```
level:"ERROR"
message:failed
user_id:"usr-452"
source_ip:10.0.*
level:"INFO" AND message:processed
level:"DEBUG"
```

## Usage

Run the script from your terminal. Make sure it's executable (`chmod +x generate_sample_querys.sh`).

```bash
./generate_sample_querys.sh [options]
```

### Options

-   `-n <number_of_queries>`: Specifies the total number of query strings to generate.
    -   Default: `100`
    -   Must be a positive integer.
-   `-o <output_file>`: Specifies the name of the output file where the query strings will be saved.
    -   Default: `generated_queries.txt`
-   `-h`: Displays the usage instructions and exits.

### Examples

1.  **Generate default 100 queries:**
    ```bash
    ./generate_sample_querys.sh
    # Output: Creates 'generated_queries.txt' with 100 lines.
    ```

2.  **Generate 500 queries:**
    ```bash
    ./generate_sample_querys.sh -n 500
    # Output: Creates 'generated_queries.txt' with 500 lines.
    ```

3.  **Generate 20 queries into a specific file:**
    ```bash
    ./generate_sample_querys.sh -n 20 -o my_queries.txt
    # Output: Creates 'my_queries.txt' with 20 lines.
    ```

4.  **Show help:**
    ```bash
    ./generate_sample_querys.sh -h
    ```

## Notes

-   The script overwrites the output file if it already exists.
-   The generated queries are basic examples.
-   **Important:** The Python benchmark tool (`../src/benchmark.py`) currently **does not** implement the logic to read this file, parse the queries, and execute them against Elasticsearch. This script only generates the input file; the benchmark code needs to be extended to use it.
