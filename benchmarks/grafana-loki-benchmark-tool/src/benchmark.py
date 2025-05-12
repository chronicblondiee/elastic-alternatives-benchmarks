# Core benchmarking logic (indexing, searching) for Grafana Loki

import time
import json
import logging
from datetime import datetime, timezone, timedelta
import requests  # Import requests for HTTP calls
import os

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

# --- Ingestion Benchmark Function for Loki ---
def run_ingestion(loki_url: str, data_file: str, batch_size: int = 1000, labels: dict = None):
    """
    Runs the bulk ingestion benchmark for Grafana Loki.

    Args:
        loki_url: The base URL of the Loki instance (e.g., http://localhost:3100).
        data_file: Path to the NDJSON data file. Each line should be a JSON log record.
        batch_size: Number of log entries per push request.
        labels: A dictionary of labels to apply to all log streams (e.g., {"job": "benchmark"}).

    Returns:
        A dictionary containing benchmark results.
    """
    push_url = f"{loki_url}/loki/api/v1/push"
    if labels is None:
        labels = {"job": "benchmark_ingest"}  # Default labels

    logger.info(f"Starting Loki ingestion benchmark to '{push_url}' from file '{data_file}' with batch size {batch_size}")

    streams = {}  # Group logs by labels
    total_docs = 0
    successful_docs = 0
    errors = 0
    error_details = []
    start_time_total = time.perf_counter()
    session = requests.Session()  # Use a session for potential connection reuse

    try:
        for doc in read_ndjson(data_file):
            total_docs += 1
            ts = doc.get('@timestamp') or doc.get('timestamp') or doc.get('time')
            if ts:
                try:
                    if isinstance(ts, (int, float)):
                        dt_obj = datetime.fromtimestamp(ts, timezone.utc)
                    else:
                        dt_obj = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                    timestamp_ns = str(int(dt_obj.timestamp() * 1e9))
                except ValueError:
                    logger.warning(f"Could not parse timestamp '{ts}', using current time.")
                    timestamp_ns = str(int(time.time() * 1e9))
            else:
                timestamp_ns = str(int(time.time() * 1e9))

            log_line = json.dumps(doc)
            label_key = tuple(sorted(labels.items()))

            if label_key not in streams:
                streams[label_key] = {"stream": labels, "values": []}

            streams[label_key]["values"].append([timestamp_ns, log_line])

            if len(streams[label_key]["values"]) >= batch_size:
                payload = {"streams": [streams[label_key]]}
                try:
                    response = session.post(push_url, json=payload)
                    response.raise_for_status()
                    successful_docs += len(streams[label_key]["values"])
                    logger.info(f"Pushed batch: {successful_docs} successful docs so far.")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Loki push request failed: {e}")
                    errors += len(streams[label_key]["values"])
                    error_details.append(f"RequestError: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error during Loki push: {e}")
                    errors += len(streams[label_key]["values"])
                    error_details.append(f"Unexpected Push Error: {e}")

                streams[label_key]["values"] = []
                if errors > 0:
                    logger.info(f"Processed batch: {successful_docs} successful, {errors} errors so far.")

        final_payload_streams = [stream_data for stream_data in streams.values() if stream_data["values"]]
        if final_payload_streams:
            payload = {"streams": final_payload_streams}
            try:
                response = session.post(push_url, json=payload)
                response.raise_for_status()
                docs_in_final_batch = sum(len(s["values"]) for s in final_payload_streams)
                successful_docs += docs_in_final_batch
                logger.info(f"Pushed final batch ({docs_in_final_batch} docs).")
            except requests.exceptions.RequestException as e:
                logger.error(f"Final Loki push request failed: {e}")
                docs_in_final_batch = sum(len(s["values"]) for s in final_payload_streams)
                errors += docs_in_final_batch
                error_details.append(f"Final RequestError: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during final Loki push: {e}")
                docs_in_final_batch = sum(len(s["values"]) for s in final_payload_streams)
                errors += docs_in_final_batch
                error_details.append(f"Unexpected Final Push Error: {e}")

    except FileNotFoundError:
        return {"total_docs_attempted": 0, "successful_docs": 0, "total_time": 0, "docs_per_sec": 0, "errors": 1, "error_details": [f"Data file not found: {data_file}"]}
    except Exception as e:
        logger.error(f"An unexpected error occurred during ingestion loop: {e}")
        remaining_docs = sum(len(s["values"]) for s in streams.values())
        errors += remaining_docs
        error_details.append(f"Unexpected Ingestion Loop Error: {e}")
    finally:
        session.close()

    end_time_total = time.perf_counter()
    total_time = end_time_total - start_time_total
    docs_per_sec = successful_docs / total_time if total_time > 0 else 0

    logger.info(f"Loki Ingestion finished. Total Docs Attempted: {total_docs}, Successful: {successful_docs}, Errors: {errors}")
    logger.info(f"Total Time: {total_time:.4f} seconds, Rate: {docs_per_sec:.2f} docs/sec")

    return {
        "total_docs_attempted": total_docs,
        "successful_docs": successful_docs,
        "total_time": total_time,
        "docs_per_sec": docs_per_sec,
        "errors": errors,
        "error_details": error_details[:10] if len(error_details) > 10 else error_details
    }

# --- Query Benchmark Function for Loki ---
def run_queries(loki_url: str, queries_file: str, time_range_minutes: int = 60):
    """
    Runs the search query benchmark against Grafana Loki using LogQL.

    Args:
        loki_url: The base URL of the Loki instance (e.g., http://localhost:3100).
        queries_file: Path to the file containing LogQL queries (one per line).
        time_range_minutes: The duration in minutes for the query range (ending now).

    Returns:
        A dictionary containing benchmark results.
    """
    query_range_url = f"{loki_url}/loki/api/v1/query_range"
    logger.info(f"Starting Loki query benchmark using queries from '{queries_file}' against '{query_range_url}'")

    queries = []
    try:
        with open(queries_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    queries.append(line)
    except FileNotFoundError:
        logger.error(f"Queries file not found: {queries_file}")
        return {"total_queries": 0, "successful_queries": 0, "avg_latency": 0, "errors": 1}

    if not queries:
        logger.warning("No queries found in the queries file.")
        return {"total_queries": 0, "successful_queries": 0, "avg_latency": 0, "errors": 0}

    total_queries = len(queries)
    latencies = []
    errors = 0
    session = requests.Session()

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=time_range_minutes)
    params = {
        'start': str(int(start_time.timestamp() * 1e9)),
        'end': str(int(end_time.timestamp() * 1e9)),
        'limit': 1000
    }

    for i, logql_query in enumerate(queries):
        request_params = params.copy()
        request_params['query'] = logql_query
        query_start_time = time.perf_counter()
        try:
            response = session.get(query_range_url, params=request_params)
            response.raise_for_status()
            query_end_time = time.perf_counter()
            latency = query_end_time - query_start_time
            latencies.append(latency)
        except requests.exceptions.RequestException as e:
            query_end_time = time.perf_counter()
            logger.error(f"Query {i+1} ('{logql_query[:50]}...') failed: {e}")
            errors += 1
        except Exception as e:
            query_end_time = time.perf_counter()
            logger.error(f"An unexpected error occurred during query {i+1} ('{logql_query[:50]}...'): {e}")
            errors += 1

    session.close()

    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0

    logger.info(f"Loki Query benchmark finished. Total Queries: {total_queries}, Successful: {len(latencies)}, Errors: {errors}")
    logger.info(f"Avg Latency: {avg_latency:.4f}s, Min: {min_latency:.4f}s, Max: {max_latency:.4f}s")

    return {
        "total_queries": total_queries,
        "successful_queries": len(latencies),
        "avg_latency": avg_latency,
        "min_latency": min_latency,
        "max_latency": max_latency,
        "errors": errors
    }

# --- BenchmarkTool Class adapted for Loki ---
class BenchmarkTool:
    def __init__(self, loki_url='http://localhost:3100', default_labels=None):
        """Initialize the Loki Benchmark Tool."""
        self.loki_url = loki_url.rstrip('/')
        self.default_labels = default_labels if default_labels else {"job": "benchmark_tool"}
        self.session = requests.Session()
        self._connect()

    def _connect(self):
        """Check connection to Loki."""
        ready_url = f"{self.loki_url}/ready"
        try:
            response = self.session.get(ready_url, timeout=10)
            response.raise_for_status()
            if "ready" in response.text:
                logger.info(f"Successfully connected to Loki at {self.loki_url}")
            else:
                logger.warning(f"Connected to Loki at {self.loki_url}, but readiness check returned unexpected content: {response.text[:100]}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Loki connection failed to {ready_url}: {e}")
            raise ConnectionError(f"Failed to connect to Loki at {ready_url}: {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred during Loki connection check: {e}")
            raise

    def bulk_ingest(self, log_data_iterable, batch_size=1000, labels=None):
        """
        Bulk ingest log data into Loki using an iterable.

        Args:
            log_data_iterable: An iterable yielding log documents (dictionaries).
            batch_size: Number of log entries per push request.
            labels: Specific labels for this ingestion batch, overrides default.
        """
        push_url = f"{self.loki_url}/loki/api/v1/push"
        ingest_labels = labels if labels else self.default_labels
        label_key = tuple(sorted(ingest_labels.items()))

        logger.info(f"Starting class-based Loki bulk ingest to '{push_url}'")

        current_batch = {"stream": ingest_labels, "values": []}
        successful_docs = 0
        fail_count = 0
        start_time_total = time.perf_counter()

        try:
            for doc in log_data_iterable:
                ts = doc.get('@timestamp') or doc.get('timestamp') or doc.get('time')
                if ts:
                    try:
                        if isinstance(ts, (int, float)):
                            dt_obj = datetime.fromtimestamp(ts, timezone.utc)
                        else:
                            dt_obj = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                        timestamp_ns = str(int(dt_obj.timestamp() * 1e9))
                    except ValueError:
                        timestamp_ns = str(int(time.time() * 1e9))
                else:
                    timestamp_ns = str(int(time.time() * 1e9))

                log_line = json.dumps(doc)
                current_batch["values"].append([timestamp_ns, log_line])

                if len(current_batch["values"]) >= batch_size:
                    payload = {"streams": [current_batch]}
                    try:
                        response = self.session.post(push_url, json=payload)
                        response.raise_for_status()
                        successful_docs += len(current_batch["values"])
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Loki push request failed during batch: {e}")
                        fail_count += len(current_batch["values"])
                    current_batch["values"] = []
                    if (successful_docs + fail_count) % (batch_size * 10) == 0:
                        logger.info(f"Processed batch: {successful_docs} successful, {fail_count} errors so far.")

            if current_batch["values"]:
                payload = {"streams": [current_batch]}
                try:
                    response = self.session.post(push_url, json=payload)
                    response.raise_for_status()
                    successful_docs += len(current_batch["values"])
                except requests.exceptions.RequestException as e:
                    logger.error(f"Final Loki push request failed: {e}")
                    fail_count += len(current_batch["values"])

        except Exception as e:
            logger.error(f"An unexpected error occurred during class-based ingestion: {e}", exc_info=True)
            fail_count = -1

        end_time_total = time.perf_counter()
        total_time = end_time_total - start_time_total
        docs_per_sec = successful_docs / total_time if total_time > 0 else 0

        logger.info(f"Class-based Loki ingestion finished. Successful: {successful_docs}, Errors: {fail_count if fail_count != -1 else 'Major Error'}")
        logger.info(f"Total Time: {total_time:.4f} seconds, Rate: {docs_per_sec:.2f} docs/sec")
        return {"successful": successful_docs, "failed": fail_count, "time": total_time, "rate": docs_per_sec}

    def search_logs(self, logql_query, time_range_minutes=60, limit=100):
        """
        Search logs in Loki using LogQL.

        Args:
            logql_query: The LogQL query string.
            time_range_minutes: The duration in minutes for the query range (ending now).
            limit: Maximum number of log entries to return.

        Returns:
            The list of log entries (streams/values) or None if the query fails.
        """
        query_range_url = f"{self.loki_url}/loki/api/v1/query_range"
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=time_range_minutes)
        params = {
            'query': logql_query,
            'start': str(int(start_time.timestamp() * 1e9)),
            'end': str(int(end_time.timestamp() * 1e9)),
            'limit': limit
        }

        start_query_time = time.perf_counter()
        try:
            response = self.session.get(query_range_url, params=params)
            response.raise_for_status()
            end_query_time = time.perf_counter()
            latency = end_query_time - start_query_time
            result_data = response.json().get('data', {}).get('result', [])
            result_type = response.json().get('data', {}).get('resultType', 'unknown')
            logger.info(f"Class-based Loki search completed in {latency:.4f} seconds. Result Type: {result_type}, Items: {len(result_data)}")
            return result_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Class-based Loki search failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during class-based Loki search: {e}")
            return None

    def close_session(self):
        """Close the underlying requests session."""
        self.session.close()
        logger.info("Loki HTTP session closed.")