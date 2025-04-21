#!/bin/bash

# Default values
DEFAULT_NUM_QUERIES=100
OUTPUT_FILE="generated_queries.txt"

# --- Functions ---

# Function to print usage instructions
usage() {
  echo "Usage: $0 [-n <number_of_queries>] [-o <output_file>]"
  echo "  Generates sample query strings (Lucene-like syntax), one per line."
  echo "  -n <number_of_queries>: Number of queries to generate (default: $DEFAULT_NUM_QUERIES)"
  echo "  -o <output_file>:       Name of the output file (default: $OUTPUT_FILE)"
  exit 1
}

# --- Query Components ---
log_levels=("INFO" "WARN" "ERROR" "DEBUG" "TRACE")
common_messages=("logged" "failed" "processed" "connection" "timeout" "updated" "started" "file" "input" "data")
user_id_prefixes=("usr-1" "usr-2" "usr-3" "usr-4" "usr-5" "usr-6" "usr-7" "usr-8" "usr-9") # For prefix/wildcard
ip_prefixes=("192.168" "10.0" "172.16")

# --- Argument Parsing ---
NUM_QUERIES=$DEFAULT_NUM_QUERIES

while getopts "n:o:h" opt; do
  case $opt in
    n)
      # Validate if the input is a positive integer
      if [[ "$OPTARG" =~ ^[1-9][0-9]*$ ]]; then
        NUM_QUERIES=$OPTARG
      else
        echo "Error: Number of queries must be a positive integer." >&2
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

echo "Generating $NUM_QUERIES sample queries into $OUTPUT_FILE..." >&2

# Redirect the entire loop's output once for efficiency
{
  for (( i=1; i<=NUM_QUERIES; i++ )); do
    query=""
    # Randomly choose a query type
    query_type=$((RANDOM % 5))

    case $query_type in
      0) # Term query on level
        level=${log_levels[$((RANDOM % ${#log_levels[@]}))]}
        query="level:\"$level\""
        ;;
      1) # Match query on message
        term=${common_messages[$((RANDOM % ${#common_messages[@]}))]}
        query="message:$term" # Match queries often don't need quotes unless phrase
        ;;
      2) # Term query on user_id
        user_id="usr-$((RANDOM % 1000 + 1))"
        query="user_id:\"$user_id\""
        ;;
      3) # Wildcard query on source_ip
        prefix=${ip_prefixes[$((RANDOM % ${#ip_prefixes[@]}))]}
        query="source_ip:${prefix}.*"
        ;;
      4) # Boolean query (Level AND Message)
        level=${log_levels[$((RANDOM % ${#log_levels[@]}))]}
        term=${common_messages[$((RANDOM % ${#common_messages[@]}))]}
        query="level:\"$level\" AND message:$term"
        ;;
      *) # Default fallback (shouldn't happen)
        query="level:INFO"
        ;;
    esac

    # Output the generated query string
    printf '%s\n' "$query"

    # Optional: Print progress to stderr
    if (( i % 100 == 0 )); then
       echo "Generated $i queries..." >&2
    fi

  done
} > "$OUTPUT_FILE" # Redirect stdout of the block to the output file

echo "Finished generating $NUM_QUERIES queries in $OUTPUT_FILE." >&2

exit 0