import argparse
import os
from pathlib import Path
# Ensure benchmark functions are correctly imported
from .benchmark import run_ingestion, run_queries
# Ensure the client class is correctly imported
from .es_client import ElasticsearchClient
import logging # Import logging
# --- FIX: Import warnings to disable SSL warnings if needed ---
import warnings
from elastic_transport import SecurityWarning

# Configure basic logging for the CLI as well
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Elasticsearch Benchmark Tool")

    # Connection Arguments
    parser.add_argument("--host", required=True, help="Elasticsearch host address.")
    parser.add_argument("--port", type=int, default=9200, help="Elasticsearch port (default: 9200).")
    parser.add_argument("--scheme", default="http", choices=["http", "https"], help="Connection scheme (http or https, default: http).")
    parser.add_argument("--user", help="Username for basic authentication.")
    parser.add_argument("--password", help="Password for basic authentication.")
    parser.add_argument("--api-key", help="API key for authentication.")
    parser.add_argument("--no-verify-certs", action="store_true", help="Disable SSL certificate verification (use with caution).")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds (default: 30).") # Added timeout

    # Benchmark Arguments
    parser.add_argument("--index-name", default="logs", help="Index name for storing logs (default: logs).")
    # --- FIX: Make data-file conditionally required ---
    parser.add_argument("--data-file", type=Path, help="Path to the NDJSON log file for ingestion (required unless --query-only).")
    parser.add_argument("--queries-file", type=Path, help="Path to a file containing queries (one per line) for benchmarking.")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for bulk ingestion (default: 1000, ignored if --query-only).")
    # --- FIX: Add query-only mode argument ---
    parser.add_argument("--query-only", action="store_true", help="Run only the query benchmark (requires --queries-file).")


    args = parser.parse_args()

    # --- FIX: Validation for query-only mode ---
    if args.query_only:
        if not args.queries_file:
            parser.error("--queries-file is required when using --query-only.")
        if args.data_file:
            logger.warning("--data-file is ignored when using --query-only.")
        if args.batch_size != 1000: # Check if default was overridden
             logger.warning("--batch-size is ignored when using --query-only.")
    else:
        # Data file is required if not in query-only mode
        if not args.data_file:
            parser.error("--data-file is required unless --query-only is specified.")
        # Validate data file existence only if needed
        if not args.data_file.is_file():
            logger.error(f"Data file not found: {args.data_file}")
            return

    # Validate queries file existence if provided (relevant for both modes if specified)
    if args.queries_file and not args.queries_file.is_file():
        logger.error(f"Queries file specified but not found: {args.queries_file}")
        return

    # --- FIX: Disable warnings if verification is off ---
    if args.no_verify_certs:
        warnings.filterwarnings("ignore", category=SecurityWarning)
        logger.warning("SSL certificate verification is disabled.")


    try:
        # --- FIX: Pass scheme, verify_certs status, and timeout to client ---
        client_wrapper = ElasticsearchClient(
            host=args.host,
            port=args.port,
            scheme=args.scheme, # Pass scheme
            user=args.user,
            password=args.password,
            api_key=args.api_key,
            verify_certs=not args.no_verify_certs, # Pass verification status
            timeout=args.timeout # Pass timeout
        )
        es_client = client_wrapper.client
        if not es_client:
            # The client constructor now raises exceptions on failure
            # This check might be redundant if constructor always raises
            raise ConnectionError("Failed to get valid Elasticsearch client object.")

    except ConnectionError as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        return
    except Exception as e:
        logger.error(f"An unexpected error occurred during client initialization: {e}")
        return

    # --- FIX: Conditional execution based on query-only mode ---
    if not args.query_only:
        # Run ingestion benchmark
        logger.info("--- Starting Ingestion Benchmark ---")
        ingestion_results = run_ingestion(es_client, args.index_name, str(args.data_file), args.batch_size)
        logger.info("--- Ingestion Benchmark Finished ---")
        print("\nIngestion Results:")
        for key, value in ingestion_results.items():
            # Truncate long error lists
            if key == 'error_details' and isinstance(value, list) and len(value) > 5:
                print(f"  {key}: {len(value)} errors (details truncated: {value[:5]}...)")
            else:
                print(f"  {key}: {value}")
    else:
        logger.info("Skipping ingestion benchmark (--query-only specified).")


    # Run query benchmark if queries file is provided (always check, even in query-only mode)
    if args.queries_file:
        logger.info("\n--- Starting Query Benchmark ---")
        query_results = run_queries(es_client, args.index_name, str(args.queries_file))
        logger.info("--- Query Benchmark Finished ---")
        print("\nQuery Results:")
        # Check if query_results is not None and is a dictionary before iterating
        if isinstance(query_results, dict):
            for key, value in query_results.items():
                print(f"  {key}: {value}")
        else:
            print("  Query benchmark did not return results (likely not fully implemented).")
    elif args.query_only:
        # This case should have been caught by validation, but added for safety
        logger.error("Query-only mode specified, but no queries file provided or found.")


if __name__ == "__main__":
    main()