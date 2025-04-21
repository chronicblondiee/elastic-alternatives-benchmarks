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
