#!/bin/bash

# Default values
DEFAULT_LINES=1000
OUTPUT_FILE="generated_logs.ndjson" # Changed default extension

# --- Functions ---

# Function to print usage instructions
usage() {
  echo "Usage: $0 [-n <number_of_lines>] [-o <output_file>]"
  echo "  Generates log data in NDJSON format."
  echo "  -n <number_of_lines>: Number of log lines (JSON objects) to generate (default: $DEFAULT_LINES)"
  echo "  -o <output_file>:     Name of the output NDJSON file (default: $OUTPUT_FILE)"
  exit 1
}

# Function to generate a random IP address (simple version)
generate_ip() {
  # Use arithmetic expansion directly in printf later if preferred
  echo "$((RANDOM % 256)).$((RANDOM % 256)).$((RANDOM % 256)).$((RANDOM % 256))"
}

# Function to generate a random log level
generate_level() {
  local levels=("INFO" "WARN" "ERROR" "DEBUG" "TRACE")
  echo "${levels[$((RANDOM % ${#levels[@]}))]}"
}

# Function to generate a random short message
# Escape double quotes within the message for valid JSON
generate_message() {
  local messages=(
    "User logged in successfully"
    "Configuration updated"
    "Service started"
    "Request processed"
    "Database connection failed"
    "File not found"
    "Invalid input received"
    "Cache cleared"
    "Processing data chunk"
    "System health check OK"
    "Timeout occurred"
    "Memory usage high"
    "Attempting to read file \"config.json\"" # Example with quotes
  )
  local msg="${messages[$((RANDOM % ${#messages[@]}))]}"
  # Basic escaping of double quotes for JSON
  echo "${msg//\"/\\\"}"
}

# Function to generate a random user ID
generate_user_id() {
    echo "usr-$((RANDOM % 1000 + 1))" # Generates usr-1 to usr-1000
}

# --- Argument Parsing ---

NUM_LINES=$DEFAULT_LINES

while getopts "n:o:h" opt; do
  case $opt in
    n)
      # Validate if the input is a positive integer
      if [[ "$OPTARG" =~ ^[1-9][0-9]*$ ]]; then
        NUM_LINES=$OPTARG
      else
        echo "Error: Number of lines must be a positive integer." >&2
        usage
      fi
      ;;
    o)
      OUTPUT_FILE=$OPTARG
      ;;
    h)
      usage
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      usage
      ;;
  esac
done

# --- Main Logic ---

echo "Generating $NUM_LINES NDJSON log lines into $OUTPUT_FILE..." >&2 # Also send initial message to stderr

# *** Performance Improvement: Redirect the entire loop's output once ***
{
  # Loop to generate log lines
  for (( i=1; i<=NUM_LINES; i++ )); do
    # Generate data fields
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ") # ISO 8601 UTC format
    level=$(generate_level)
    ip=$(generate_ip)
    message=$(generate_message)
    user_id=$(generate_user_id)

    # Construct the JSON line using printf for better control over quoting
    # Output directly to stdout (which is redirected to the file)
    printf '{"timestamp": "%s", "level": "%s", "message": "%s", "user_id": "%s", "source_ip": "%s"}\n' \
      "$timestamp" \
      "$level" \
      "$message" \
      "$user_id" \
      "$ip"

    # Optional: Print progress to stderr every 1000 lines so it doesn't go into the output file
    if (( i % 1000 == 0 )); then
       echo "Generated $i lines..." >&2
    fi

  done
} > "$OUTPUT_FILE" # Redirect stdout of the block to the output file

echo "Finished generating $NUM_LINES NDJSON log lines in $OUTPUT_FILE." >&2 # Send final message to stderr

exit 0