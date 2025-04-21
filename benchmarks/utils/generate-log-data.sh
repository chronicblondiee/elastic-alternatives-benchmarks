#!/bin/bash

# Default values
DEFAULT_LINES=1000
OUTPUT_FILE="generated_logs.log"

# --- Functions ---

# Function to print usage instructions
usage() {
  echo "Usage: $0 [-n <number_of_lines>] [-o <output_file>]"
  echo "  -n <number_of_lines>: Number of log lines to generate (default: $DEFAULT_LINES)"
  echo "  -o <output_file>:     Name of the output log file (default: $OUTPUT_FILE)"
  exit 1
}

# Function to generate a random IP address (simple version)
generate_ip() {
  echo "$((RANDOM % 256)).$((RANDOM % 256)).$((RANDOM % 256)).$((RANDOM % 256))"
}

# Function to generate a random log level
generate_level() {
  local levels=("INFO" "WARN" "ERROR" "DEBUG" "TRACE")
  echo "${levels[$((RANDOM % ${#levels[@]}))]}"
}

# Function to generate a random short message
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
  )
  echo "${messages[$((RANDOM % ${#messages[@]}))]}"
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

echo "Generating $NUM_LINES log lines into $OUTPUT_FILE..."

# Clear the output file or create it if it doesn't exist
> "$OUTPUT_FILE"

# Loop to generate log lines
for (( i=1; i<=NUM_LINES; i++ )); do
  timestamp=$(date +"%Y-%m-%d %H:%M:%S.%3N")
  level=$(generate_level)
  ip=$(generate_ip)
  message=$(generate_message)
  request_id=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12) # Random request ID

  # Construct the log line
  log_line="$timestamp [$level] client=$ip request_id=$request_id : $message"

  # Append to the output file
  echo "$log_line" >> "$OUTPUT_FILE"

  # Optional: Print progress every 1000 lines
  if (( i % 1000 == 0 )); then
     echo "Generated $i lines..."
  fi

done

echo "Finished generating $NUM_LINES log lines in $OUTPUT_FILE."

exit 0