import argparse
import os
from pathlib import Path
import logging
import warnings
import json # For parsing labels

# Ensure benchmark functions are correctly imported
from .benchmark import run_ingestion, run_queries
# Ensure the Loki client class is correctly imported
from .loki_client import LokiClient

# Configure basic logging for the CLI
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_labels(label_string):
    """Parses a comma-separated key=value string into a dictionary."""
    labels = {}
    if not label_string:
        return labels
    try:
        for pair in label_string.split(','):
            key, value = pair.strip().split('=', 1)
            labels[key.strip()] = value.strip()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid label format: '{label_string}'. Use comma-separated key=value pairs.")
    return labels

def main():
    parser = argparse.ArgumentParser(description="Grafana Loki Benchmark Tool")

    # Connection Arguments for Loki
    parser.add_argument("--loki-url", required=True, help="Grafana Loki base URL (e.g., http://localhost:3100).")
    parser.add_argument("--user", help="Username for Loki basic authentication.")
    parser.add_argument("--password", help="Password for Loki basic authentication.")
    parser.add_argument("--api-key", help="API key for Loki authentication (e.g., Bearer token).")
    parser.add_argument("--no-verify-certs", action="store_true", help="Disable SSL certificate verification (use with caution).")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds (default: 30).")

    # Benchmark Arguments
    parser.add_argument("--labels", type=parse_labels, default="job=benchmark_tool",
                        help="Comma-separated key=value labels to apply to ingested logs (default: job=benchmark_tool). Example: 'app=myapp,env=prod'")
    parser.add_argument("--data-file", type=Path, help="Path to the NDJSON log file for ingestion (required unless --query-only). Each line should be a JSON object.")
    parser.add_argument("--queries-file", type=Path, help="Path to a file containing LogQL queries (one per line) for benchmarking.")
    parser.add_argument("--batch-size", type=int, default=500, help="Number of log lines per push request to Loki (default: 500, ignored if --query-only). Note: Loki has payload size limits.")
    parser.add_argument("--query-only", action="store_true", help="Run only the query benchmark (requires --queries-file).")
    parser.add_argument("--query-limit", type=int, default=100, help="Limit for number of results returned by Loki queries (default: 100).")
    # Add arguments for query time range if needed
    # parser.add_argument("--query-start", help="Start time for range queries (RFC3339 or Unix timestamp).")
    # parser.add_argument("--query-end", help="End time for range queries (RFC3339 or Unix timestamp).")
    # parser.add_argument("--query-step", help="Step for range queries (e.g., '15s').")

    args = parser.parse_args()

    # Validation
    if args.query_only:
        if not args.queries_file:
            parser.error("--queries-file is required when using --query-only.")
        if args.data_file:
            logger.warning("--data-file is ignored when using --query-only.")
        if args.batch_size != 500:
             logger.warning("--batch-size is ignored when using --query-only.")
    else:
        if not args.data_file:
            parser.error("--data-file is required unless --query-only is specified.")
        if not args.data_file.is_file():
            logger.error(f"Data file not found: {args.data_file}")
            return

    if args.queries_file and not args.queries_file.is_file():
        logger.error(f"Queries file specified but not found: {args.queries_file}")
        return

    if args.no_verify_certs:
        logger.warning("SSL certificate verification is disabled.")
        # Warning filtering is handled within LokiClient now

    try:
        # Initialize Loki Client
        loki_client = LokiClient(
            loki_url=args.loki_url,
            user=args.user,
            password=args.password,
            api_key=args.api_key,
            verify_certs=not args.no_verify_certs,
            timeout=args.timeout
        )

        # Check connection
        if not loki_client.check_connection():
             logger.error("Failed to connect to Loki or Loki is not ready. Please check the URL and Loki status.")
             return

    except Exception as e:
        logger.error(f"An unexpected error occurred during Loki client initialization or connection check: {e}")
        return

    # Run Benchmarks
    if not args.query_only:
        logger.info("--- Starting Ingestion Benchmark ---")
        ingestion_results = run_ingestion(
            loki_client,
            args.labels, # Pass labels dictionary
            str(args.data_file),
            args.batch_size
        )
        logger.info("--- Ingestion Benchmark Finished ---")
        print("\nIngestion Results:")
        if isinstance(ingestion_results, dict):
            for key, value in ingestion_results.items():
                # Truncate long error lists
                if key == 'error_details' and isinstance(value, list) and len(value) > 5:
                    print(f"  {key}: {len(value)} errors (details truncated: {value[:5]}...)")
                else:
                    print(f"  {key}: {value}")
        else:
            print("  Ingestion benchmark did not return expected results.")
    else:
        logger.info("Skipping ingestion benchmark (--query-only specified).")

    if args.queries_file:
        logger.info("\n--- Starting Query Benchmark ---")
        # Construct time_range if args exist
        # time_range = (args.query_start, args.query_end, args.query_step) if args.query_start and args.query_end else None
        query_results = run_queries(
            loki_client,
            str(args.queries_file),
            limit=args.query_limit
            # time_range=time_range # Pass time range if implemented
        )
        logger.info("--- Query Benchmark Finished ---")
        print("\nQuery Results:")
        if isinstance(query_results, dict):
            for key, value in query_results.items():
                print(f"  {key}: {value}")
        else:
            print("  Query benchmark did not return expected results.")
    elif args.query_only:
        logger.error("Query-only mode specified, but no queries file provided or found.")

if __name__ == "__main__":
    main()