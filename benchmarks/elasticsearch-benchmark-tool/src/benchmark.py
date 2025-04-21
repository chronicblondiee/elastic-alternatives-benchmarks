# Core benchmarking logic (indexing, searching)

import time
import json
import logging
from datetime import datetime, timezone  # Import datetime and timezone
from elasticsearch import Elasticsearch, helpers, exceptions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Helper function to read NDJSON data ---
def read_ndjson(file_path):
    """Reads an NDJSON file line by line and yields JSON objects."""
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping invalid JSON line: {line} - Error: {e}")
    except FileNotFoundError:
        logger.error(f"Data file not found: {file_path}")
        raise

# --- Ingestion Benchmark Function ---
def run_ingestion(client: Elasticsearch, index_name: str, data_file: str, batch_size: int = 1000):
    """
    Runs the bulk ingestion benchmark, adding a @timestamp field to each document.

    Args:
        client: An initialized Elasticsearch client instance.
        index_name: The name of the index to ingest into.
        data_file: Path to the NDJSON data file.
        batch_size: Number of documents per bulk request.

    Returns:
        A dictionary containing benchmark results (e.g., total_docs, total_time, docs_per_sec, errors).
    """
    logger.info(f"Starting ingestion benchmark for index '{index_name}' from file '{data_file}' with batch size {batch_size}")

    # --- FIX: Remove explicit exists check, rely on create with ignore=400 ---
    try:
        # Attempt to create the index, ignore error if it already exists
        logger.info(f"Ensuring index '{index_name}' exists (create if not present)...")
        create_response = client.indices.create(index=index_name, ignore=400)
        if create_response.get('acknowledged', False):
            logger.info(f"Index '{index_name}' created or already existed.")
        elif create_response.get('status') == 400 and 'resource_already_exists_exception' in str(create_response):
            logger.info(f"Index '{index_name}' already exists.")
        else:
            # Log unexpected non-400 errors from create
            logger.warning(f"Index creation check returned unexpected response: {create_response}")

    # --- FIX: Catch specific exceptions related to index creation/check ---
    except exceptions.AuthenticationException as e:
        logger.error(f"Authentication error during index check/create for '{index_name}': {e}")
        return {"total_docs_attempted": 0, "successful_docs": 0, "total_time": 0, "docs_per_sec": 0, "errors": 1, "error_details": [f"Authentication Error: {e}"]}
    except exceptions.ConnectionError as e:
        logger.error(f"Connection error during index check/create for '{index_name}': {e}")
        return {"total_docs_attempted": 0, "successful_docs": 0, "total_time": 0, "docs_per_sec": 0, "errors": 1, "error_details": [f"Connection Error: {e}"]}
    except exceptions.RequestError as e:
        logger.error(f"Error ensuring index '{index_name}' exists: {e}")
        return {"total_docs_attempted": 0, "successful_docs": 0, "total_time": 0, "docs_per_sec": 0, "errors": 1, "error_details": [str(e)]}
    except Exception as e:
        logger.error(f"Unexpected error during index setup for '{index_name}': {e}")
        return {"total_docs_attempted": 0, "successful_docs": 0, "total_time": 0, "docs_per_sec": 0, "errors": 1, "error_details": [f"Unexpected Setup Error: {e}"]}

    actions = []
    total_docs = 0
    successful_docs = 0
    errors = 0
    error_details = []
    start_time_total = time.perf_counter()

    try:
        for doc in read_ndjson(data_file):
            # --- FIX: Add @timestamp field ---
            # Get current time in UTC and format as ISO 8601 string with 'Z' for UTC
            now_utc = datetime.now(timezone.utc)
            timestamp_str = now_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'  # Format with milliseconds and Z
            doc['@timestamp'] = timestamp_str

            actions.append({"_index": index_name, "_source": doc})
            total_docs += 1

            if len(actions) >= batch_size:
                try:
                    success_count, failed_items = helpers.bulk(
                        client,
                        actions,
                        chunk_size=batch_size,
                        raise_on_error=False,    # Don't raise on individual doc errors
                        raise_on_exception=True, # Raise on transport errors (like connection/4xx/5xx)
                        stats_only=False         # Get detailed results to see errors
                    )
                    num_success = success_count
                    num_failed = len(failed_items)  # helpers.bulk returns list of failed actions
                    chunk_errors = []
                    if num_failed > 0:
                        # Extract reasons from failed items
                        for item_result in failed_items:
                            # Structure might be {'index': {'_index': '...', 'status': 400, 'error': {...}}}
                            action_type = list(item_result.keys())[0]  # e.g., 'index'
                            error_info = item_result.get(action_type, {}).get('error', {})
                            reason = error_info.get('reason', 'Unknown bulk error')
                            chunk_errors.append(f"{action_type.upper()}: {reason}")  # Add action type

                    successful_docs += num_success
                    errors += num_failed
                    if chunk_errors:
                        error_details.extend(chunk_errors)
                        logger.warning(f"Bulk chunk finished with {num_failed} errors. Examples: {chunk_errors[:3]}")

                except exceptions.TransportError as e:
                    # This includes connection errors, timeouts, and non-2xx responses if raise_on_exception=True
                    logger.error(f"Bulk request transport error: {getattr(e, 'info', e)} - Status: {getattr(e, 'status_code', 'N/A')}")
                    # Add specific error info if available
                    error_info_str = str(getattr(e, 'info', e))
                    errors += len(actions)  # Assume all failed if transport error occurs
                    error_details.append(f"TransportError ({getattr(e, 'status_code', 'N/A')}): {error_info_str}")
                except Exception as e:  # Catch other potential bulk errors
                    logger.error(f"Unexpected error during bulk processing: {e}", exc_info=True)  # Log traceback
                    errors += len(actions)
                    error_details.append(f"Unexpected Bulk Error: {e}")

                actions = []  # Clear actions after processing batch
                if errors == 0:
                    logger.info(f"Processed batch: {successful_docs} successful docs so far.")
                else:
                    logger.info(f"Processed batch: {successful_docs} successful, {errors} errors so far.")

        # Ingest remaining actions
        if actions:
            try:
                success_count, failed_items = helpers.bulk(
                    client,
                    actions,
                    chunk_size=len(actions),  # Process remaining
                    raise_on_error=False,
                    raise_on_exception=True,
                    stats_only=False
                )
                num_success = success_count
                num_failed = len(failed_items)
                chunk_errors = []
                if num_failed > 0:
                    for item_result in failed_items:
                        action_type = list(item_result.keys())[0]
                        error_info = item_result.get(action_type, {}).get('error', {})
                        reason = error_info.get('reason', 'Unknown bulk error')
                        chunk_errors.append(f"{action_type.upper()}: {reason}")

                    successful_docs += num_success
                    errors += num_failed
                    if chunk_errors:
                        error_details.extend(chunk_errors)
                        logger.warning(f"Final bulk chunk finished with {num_failed} errors. Examples: {chunk_errors[:3]}")

            except exceptions.TransportError as e:
                logger.error(f"Final bulk request transport error: {getattr(e, 'info', e)} - Status: {getattr(e, 'status_code', 'N/A')}")
                error_info_str = str(getattr(e, 'info', e))
                errors += len(actions)
                error_details.append(f"TransportError ({getattr(e, 'status_code', 'N/A')}): {error_info_str}")
            except Exception as e:  # Catch other potential bulk errors
                logger.error(f"Unexpected error during final bulk processing: {e}", exc_info=True)
                errors += len(actions)
                error_details.append(f"Unexpected Bulk Error: {e}")

    except FileNotFoundError:
        return {"total_docs_attempted": 0, "successful_docs": 0, "total_time": 0, "docs_per_sec": 0, "errors": 1, "error_details": [f"Data file not found: {data_file}"]}
    except Exception as e:
        logger.error(f"An unexpected error occurred during ingestion loop: {e}")
        errors += len(actions)
        error_details.append(f"Unexpected Ingestion Loop Error: {e}")

    end_time_total = time.perf_counter()
    total_time = end_time_total - start_time_total
    docs_per_sec = successful_docs / total_time if total_time > 0 else 0

    logger.info(f"Ingestion finished. Total Docs Attempted: {total_docs}, Successful: {successful_docs}, Errors: {errors}")
    logger.info(f"Total Time: {total_time:.4f} seconds, Rate: {docs_per_sec:.2f} docs/sec")

    return {
        "total_docs_attempted": total_docs,
        "successful_docs": successful_docs,
        "total_time": total_time,
        "docs_per_sec": docs_per_sec,
        "errors": errors,
        "error_details": error_details[:10] if len(error_details) > 10 else error_details
    }

# --- Query Benchmark Function ---
def run_queries(client: Elasticsearch, index_name: str, queries_file: str):
    """
    Runs the search query benchmark.

    Args:
        client: An initialized Elasticsearch client instance.
        index_name: The name of the index to search against.
        queries_file: Path to the file containing queries (one per line).

    Returns:
        A dictionary containing benchmark results (e.g., total_queries, avg_latency, errors).
    """
    logger.info(f"Starting query benchmark for index '{index_name}' using queries from '{queries_file}'")

    queries = []
    try:
        with open(queries_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    queries.append({
                        "query": {
                            "query_string": {
                                "query": line
                            }
                        }
                    })
    except FileNotFoundError:
        logger.error(f"Queries file not found: {queries_file}")
        return {"total_queries": 0, "avg_latency": 0, "errors": 1}

    if not queries:
        logger.warning("No queries found in the queries file.")
        return {"total_queries": 0, "avg_latency": 0, "errors": 0}

    total_queries = len(queries)
    latencies = []
    errors = 0

    for i, query_body in enumerate(queries):
        start_time = time.perf_counter()
        try:
            response = client.search(index=index_name, body=query_body, size=10)
            end_time = time.perf_counter()
            latency = end_time - start_time
            latencies.append(latency)
        except exceptions.TransportError as e:
            logger.error(f"Query {i+1} failed: {e}")
            errors += 1
        except Exception as e:
            logger.error(f"An unexpected error occurred during query {i+1}: {e}")
            errors += 1

    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0

    logger.info(f"Query benchmark finished. Total Queries: {total_queries}, Successful: {len(latencies)}, Errors: {errors}")
    logger.info(f"Avg Latency: {avg_latency:.4f}s, Min: {min_latency:.4f}s, Max: {max_latency:.4f}s")

    return {
        "total_queries": total_queries,
        "successful_queries": len(latencies),
        "avg_latency": avg_latency,
        "min_latency": min_latency,
        "max_latency": max_latency,
        "errors": errors
    }


class BenchmarkTool:
    def __init__(self, host='localhost', port=9200, index_name='logs', user=None, password=None, api_key=None):
        self.host = host
        self.port = port
        self.index_name = index_name
        self.user = user
        self.password = password
        self.api_key = api_key
        self.client = self._connect()

    def _connect(self):
        """Connect to the Elasticsearch instance."""
        auth_params = {}
        if self.api_key:
            auth_params['api_key'] = self.api_key
        elif self.user and self.password:
            auth_params['basic_auth'] = (self.user, self.password)

        try:
            client = Elasticsearch(
                [{'host': self.host, 'port': self.port, 'scheme': 'http'}],
                **auth_params,
                request_timeout=30
            )
            if not client.ping():
                raise exceptions.ConnectionError("Failed to connect to Elasticsearch.")
            logger.info(f"Successfully connected to Elasticsearch at {self.host}:{self.port}")
            return client
        except exceptions.ConnectionError as e:
            logger.error(f"Elasticsearch connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during connection: {e}")
            raise

    def ensure_index(self):
        """Ensure the index exists."""
        try:
            if not self.client.indices.exists(index=self.index_name):
                logger.info(f"Index '{self.index_name}' does not exist. Creating...")
                self.client.indices.create(index=self.index_name, ignore=400)
            else:
                logger.info(f"Index '{self.index_name}' already exists.")
        except exceptions.RequestError as e:
            logger.error(f"Error checking/creating index '{self.index_name}': {e}")
        except exceptions.ConnectionError as e:
            logger.error(f"Connection error during index check/create: {e}")
            raise

    def bulk_ingest(self, log_data_iterable, batch_size=1000):
        """Bulk ingest log data into Elasticsearch using an iterable."""
        logger.info(f"Starting class-based bulk ingest for index '{self.index_name}'")
        actions = ({"_index": self.index_name, "_source": log} for log in log_data_iterable)

        success_count = 0
        fail_count = 0
        start_time_total = time.perf_counter()

        try:
            for ok, action in helpers.streaming_bulk(self.client, actions, chunk_size=batch_size, raise_on_error=False):
                if ok:
                    success_count += 1
                else:
                    fail_count += 1
                if (success_count + fail_count) % batch_size == 0:
                    logger.info(f"Processed batch: {success_count} successful, {fail_count} errors so far.")

        except exceptions.TransportError as e:
            logger.error(f"Bulk request transport error: {e}")
            fail_count = -1

        end_time_total = time.perf_counter()
        total_time = end_time_total - start_time_total
        docs_per_sec = success_count / total_time if total_time > 0 else 0

        logger.info(f"Class-based ingestion finished. Successful: {success_count}, Errors: {fail_count if fail_count != -1 else 'TransportError'}")
        logger.info(f"Total Time: {total_time:.4f} seconds, Rate: {docs_per_sec:.2f} docs/sec")
        return {"successful": success_count, "failed": fail_count, "time": total_time, "rate": docs_per_sec}

    def search_logs(self, query_body, size=10):
        """Search logs in Elasticsearch."""
        start_time = time.perf_counter()
        try:
            response = self.client.search(index=self.index_name, body=query_body, size=size)
            end_time = time.perf_counter()
            latency = end_time - start_time
            logger.info(f"Class-based search completed in {latency:.4f} seconds. Hits: {response['hits']['total']['value']}")
            return response['hits']['hits']
        except exceptions.TransportError as e:
            logger.error(f"Class-based search failed: {e}")
            return None