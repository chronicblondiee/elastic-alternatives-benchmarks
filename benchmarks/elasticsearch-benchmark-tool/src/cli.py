import argparse
import os
from pathlib import Path
from .benchmark import run_ingestion, run_queries
from .es_client import ElasticsearchClient

def main():
    parser = argparse.ArgumentParser(description="Elasticsearch Benchmark Tool")
    
    parser.add_argument("--host", required=True, help="Elasticsearch host address.")
    parser.add_argument("--port", type=int, default=9200, help="Elasticsearch port (default: 9200).")
    parser.add_argument("--index-name", default="logs", help="Index name for storing logs (default: logs).")
    parser.add_argument("--data-file", required=True, type=Path, help="Path to the log file for ingestion.")
    parser.add_argument("--queries-file", type=Path, help="Path to a file containing queries for benchmarking.")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for bulk ingestion (default: 1000).")

    args = parser.parse_args()

    # Initialize Elasticsearch client
    client = ElasticsearchClient(host=args.host, port=args.port)

    # Run ingestion benchmark
    ingestion_results = run_ingestion(client, args.index_name, args.data_file, args.batch_size)
    print("Ingestion Results:", ingestion_results)

    # Run query benchmark if queries file is provided
    if args.queries_file:
        query_results = run_queries(client, args.index_name, args.queries_file)
        print("Query Results:", query_results)

if __name__ == "__main__":
    main()