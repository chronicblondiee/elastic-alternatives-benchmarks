from elasticsearch import Elasticsearch, exceptions
import logging
import warnings
from elastic_transport import SecurityWarning

logger = logging.getLogger(__name__)

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, user=None, password=None, api_key=None, scheme='http', verify_certs=True, timeout=30):
        """Initializes the Elasticsearch client."""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.api_key = api_key
        self.scheme = scheme
        self.verify_certs = verify_certs
        self.timeout = timeout
        self.client = self._connect()

    def _connect(self):
        """Connects to the Elasticsearch instance."""
        auth_params = {}
        if self.api_key:
            auth_params['api_key'] = self.api_key
        elif self.user and self.password:
            auth_params['basic_auth'] = (self.user, self.password)

        hosts_config = [{
            'host': self.host,
            'port': self.port,
            'scheme': self.scheme
        }]

        ssl_params = {}
        if self.scheme == 'https':
            ssl_params['verify_certs'] = self.verify_certs
            if not self.verify_certs:
                warnings.filterwarnings("ignore", category=SecurityWarning)

        try:
            client = Elasticsearch(
                hosts=hosts_config,
                **auth_params,
                **ssl_params,
                request_timeout=self.timeout
            )
            logger.info(f"Successfully created Elasticsearch client for {self.scheme}://{self.host}:{self.port}")
            return client
        except exceptions.AuthenticationException as e:
            logger.error(f"Elasticsearch authentication failed: {e}")
            raise
        except exceptions.ConnectionError as e:
            logger.error(f"Elasticsearch connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during connection: {e}")
            raise

    def ensure_index(self, index_name):
        """Ensure that the specified index exists, creating it if necessary."""
        try:
            create_response = self.client.indices.create(index=index_name, ignore=400)
            if create_response.get('acknowledged', False):
                logger.info(f"Index '{index_name}' created or already existed.")
            elif create_response.get('status') == 400 and 'resource_already_exists_exception' in str(create_response):
                logger.info(f"Index '{index_name}' already exists.")
            else:
                logger.warning(f"Index creation check returned unexpected response: {create_response}")
        except exceptions.RequestError as e:
            logger.error(f"Error ensuring index '{index_name}' exists: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during index setup for '{index_name}': {e}")
            raise

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

        try:
            success, failed_items = bulk(
                self.client,
                actions,
                chunk_size=batch_size,
                raise_on_error=False,
                raise_on_exception=True
            )
            num_failed = len(failed_items)
            logger.info(f"Bulk ingest attempt finished. Successful: {success}, Failed: {num_failed} into '{index_name}'.")
            if num_failed > 0:
                logger.warning(f"First few failed items: {failed_items[:5]}")
            return success, num_failed
        except exceptions.TransportError as e:
            logger.error(f"Bulk request transport error: {getattr(e, 'info', e)} - Status: {getattr(e, 'status_code', 'N/A')}")
            return 0, len(actions)
        except Exception as e:
            logger.error(f"Unexpected error during bulk ingest: {e}", exc_info=True)
            return 0, len(actions)

    def search(self, index_name, query):
        """Execute a search query against the specified index."""
        try:
            response = self.client.search(index=index_name, body=query)
            return response['hits']['hits']
        except exceptions.NotFoundError:
            logger.error(f"Index '{index_name}' not found for search.")
            return []
        except exceptions.RequestError as e:
            logger.error(f"Search request error on index '{index_name}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search on index '{index_name}': {e}")
            return []