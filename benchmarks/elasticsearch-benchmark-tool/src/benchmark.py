# Core benchmarking logic (indexing, searching)

import time
import json
from elasticsearch import Elasticsearch, helpers

class BenchmarkTool:
    def __init__(self, host='localhost', port=9200, index_name='logs'):
        self.host = host
        self.port = port
        self.index_name = index_name
        self.client = self._connect()

    def _connect(self):
        """Connect to the Elasticsearch instance."""
        return Elasticsearch([{'host': self.host, 'port': self.port}])

    def ensure_index(self):
        """Ensure the index exists."""
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(index=self.index_name)

    def bulk_ingest(self, log_data, batch_size=1000):
        """Bulk ingest log data into Elasticsearch."""
        actions = [
            {
                "_index": self.index_name,
                "_source": log
            }
            for log in log_data
        ]

        for i in range(0, len(actions), batch_size):
            batch = actions[i:i + batch_size]
            start_time = time.perf_counter()
            helpers.bulk(self.client, batch)
            end_time = time.perf_counter()
            print(f"Indexed batch {i // batch_size + 1} in {end_time - start_time:.4f} seconds.")

    def search_logs(self, query, size=10):
        """Search logs in Elasticsearch."""
        start_time = time.perf_counter()
        response = self.client.search(index=self.index_name, body=query, size=size)
        end_time = time.perf_counter()
        print(f"Search completed in {end_time - start_time:.4f} seconds.")
        return response['hits']['hits']

    def run_benchmark(self, log_data, query, batch_size=1000):
        """Run the indexing and search benchmark."""
        self.ensure_index()
        self.bulk_ingest(log_data, batch_size)
        search_results = self.search_logs(query)
        return search_results