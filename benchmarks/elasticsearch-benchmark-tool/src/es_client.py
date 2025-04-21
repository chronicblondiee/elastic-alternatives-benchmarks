from elasticsearch import Elasticsearch, exceptions

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, user=None, password=None, api_key=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.api_key = api_key
        self.client = self._connect()

    def _connect(self):
        """Establish a connection to the Elasticsearch instance."""
        try:
            if self.api_key:
                return Elasticsearch(
                    [{'host': self.host, 'port': self.port}],
                    api_key=self.api_key
                )
            else:
                return Elasticsearch(
                    [{'host': self.host, 'port': self.port}],
                    http_auth=(self.user, self.password) if self.user and self.password else None
                )
        except exceptions.ConnectionError as e:
            raise RuntimeError(f"Failed to connect to Elasticsearch: {e}")

    def ensure_index(self, index_name):
        """Ensure that the specified index exists, creating it if necessary."""
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name)
            print(f"Index '{index_name}' created.")
        else:
            print(f"Index '{index_name}' already exists.")

    def bulk_ingest(self, index_name, documents, batch_size=1000):
        """Bulk ingest documents into the specified index."""
        from elasticsearch.helpers import bulk

        actions = [
            {
                "_index": index_name,
                "_source": doc
            }
            for doc in documents
        ]

        success, _ = bulk(self.client, actions, chunk_size=batch_size)
        print(f"Successfully indexed {success} documents into '{index_name}'.")

    def search(self, index_name, query):
        """Execute a search query against the specified index."""
        response = self.client.search(index=index_name, body=query)
        return response['hits']['hits']