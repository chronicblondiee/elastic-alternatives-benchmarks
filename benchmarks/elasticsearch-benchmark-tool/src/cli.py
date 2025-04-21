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
    # --- FIX: Add scheme argument ---
    parser.add_argument("--scheme", default="http", choices=["http", "https"], help="Connection scheme (http or https, default: http).")
    parser.add_argument("--user", help="Username for basic authentication.")
    parser.add_argument("--password", help="Password for basic authentication.")
    parser.add_argument("--api-key", help="API key for authentication.")
    # --- FIX: Add argument to disable SSL verification ---
    parser.add_argument("--no-verify-certs", action="store_true", help="Disable SSL certificate verification (use with caution).")

    # Benchmark Arguments
    parser.add_argument("--index-name", default="logs", help="Index name for storing logs (default: logs).")
    parser.add_argument("--data-file", required=True, type=Path, help="Path to the NDJSON log file for ingestion.")
    parser.add_argument("--queries-file", type=Path, help="Path to a file containing queries (one per line) for benchmarking.")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for bulk ingestion (default: 1000).")

    args = parser.parse_args()

    # --- FIX: Disable warnings if verification is off ---
    if args.no_verify_certs:
        warnings.filterwarnings("ignore", category=SecurityWarning)
        logger.warning("SSL certificate verification is disabled.")

    # Validate data file existence
    if not args.data_file.is_file():
        logger.error(f"Data file not found: {args.data_file}")
        return

    # Validate queries file existence if provided
    if args.queries_file and not args.queries_file.is_file():
        logger.error(f"Queries file not found: {args.queries_file}")
        return

    try:
        # --- FIX: Pass scheme and verify_certs status to client ---
        client_wrapper = ElasticsearchClient(
            host=args.host,
            port=args.port,
            scheme=args.scheme, # Pass scheme
            user=args.user,
            password=args.password,
            api_key=args.api_key,
            verify_certs=not args.no_verify_certs # Pass verification status
        )
        es_client = client_wrapper.client
        if not es_client:
            raise ConnectionError("Failed to get valid Elasticsearch client object.")

    except ConnectionError as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        return
    except Exception as e:
        logger.error(f"An unexpected error occurred during client initialization: {e}")
        return

    # Run ingestion benchmark
    logger.info("--- Starting Ingestion Benchmark ---")
    ingestion_results = run_ingestion(es_client, args.index_name, str(args.data_file), args.batch_size)
    logger.info("--- Ingestion Benchmark Finished ---")
    print("\nIngestion Results:")
    for key, value in ingestion_results.items():
        if key == 'error_details' and isinstance(value, list) and len(value) > 5:
            print(f"  {key}: {len(value)} errors (details truncated)")
        else:
            print(f"  {key}: {value}")

    # Run query benchmark if queries file is provided
    if args.queries_file:
        logger.info("\n--- Starting Query Benchmark ---")
        query_results = run_queries(es_client, args.index_name, str(args.queries_file))
        logger.info("--- Query Benchmark Finished ---")
        print("\nQuery Results:")
        for key, value in query_results.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()