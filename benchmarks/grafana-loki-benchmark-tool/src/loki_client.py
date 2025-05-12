import requests
import logging
import warnings
import json
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class LokiClient:
    def __init__(self, loki_url, user=None, password=None, api_key=None, verify_certs=True, timeout=30):
        """Initializes the Grafana Loki client."""
        self.loki_url = loki_url.rstrip('/') + '/' # Ensure trailing slash for urljoin
        self.user = user
        self.password = password
        self.api_key = api_key # Note: Loki often uses headers like X-Scope-OrgID or Basic Auth
        self.verify_certs = verify_certs
        self.timeout = timeout
        self.session = self._create_session()

        if not self.verify_certs:
            warnings.filterwarnings("ignore", message="Unverified HTTPS request")

    def _create_session(self):
        """Creates a requests session with authentication if provided."""
        session = requests.Session()
        session.verify = self.verify_certs

        if self.api_key:
            # Loki might use a specific header for API keys, e.g., 'Authorization: Bearer <key>'
            # Or it might be used as Basic Auth username with empty password. Adjust as needed.
            # Assuming Bearer token for now:
            session.headers.update({'Authorization': f'Bearer {self.api_key}'})
            logger.info("Configured Loki client with API Key (Bearer Token).")
        elif self.user and self.password:
            session.auth = (self.user, self.password)
            logger.info("Configured Loki client with Basic Authentication.")
        else:
             logger.info("Configured Loki client without specific authentication.")

        # Common headers for Loki push API
        session.headers.update({'Content-Type': 'application/json'})
        return session

    def _make_request(self, method, endpoint, **kwargs):
        """Helper method to make requests to Loki."""
        url = urljoin(self.loki_url, endpoint)
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            logger.debug(f"Loki API request successful: {method} {url} - Status: {response.status_code}")
            return response
        except requests.exceptions.HTTPError as e:
            logger.error(f"Loki API HTTP error: {e.response.status_code} {e.response.reason} for {method} {url}")
            logger.error(f"Response body: {e.response.text}")
            raise # Re-raise after logging
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Loki connection error for {method} {url}: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Loki request timed out for {method} {url}: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"An unexpected error occurred during Loki request for {method} {url}: {e}")
            raise

    def push_logs(self, streams):
        """
        Pushes log streams to Loki's /loki/api/v1/push endpoint.

        Args:
            streams: A list of Loki stream objects. Example format:
                     [
                         {
                             "stream": { "label": "value", ... },
                             "values": [ [ "<unix_epoch_nano>", "<log_line>" ], ... ]
                         },
                         ...
                     ]
        """
        endpoint = "loki/api/v1/push"
        payload = {"streams": streams}
        try:
            response = self._make_request('POST', endpoint, data=json.dumps(payload))
            # Loki push API returns 204 No Content on success
            if response.status_code == 204:
                logger.debug(f"Successfully pushed {len(streams)} streams to Loki.")
                return True, None
            else:
                # Should be caught by raise_for_status, but as a fallback
                logger.warning(f"Loki push API returned unexpected status: {response.status_code} - Body: {response.text}")
                return False, f"Unexpected status: {response.status_code}"
        except Exception as e:
            logger.error(f"Failed to push logs to Loki: {e}")
            return False, str(e) # Return error message

    def query(self, logql_query, limit=100, time_range=None):
        """
        Executes a LogQL query against Loki's /loki/api/v1/query or /loki/api/v1/query_range endpoint.

        Args:
            logql_query: The LogQL query string.
            limit: Maximum number of log entries to return for instant queries.
            time_range: Optional tuple (start_time, end_time) for range queries.
                        Times should be in Unix timestamp (seconds) or RFC3339 format.
                        If None, performs an instant query.

        Returns:
            The parsed JSON response from Loki, or None if an error occurs.
        """
        params = {'query': logql_query}

        if time_range:
            endpoint = "loki/api/v1/query_range"
            params['start'] = time_range[0]
            params['end'] = time_range[1]
            # Add step if needed, e.g., params['step'] = '15s'
            if len(time_range) > 2:
                 params['step'] = time_range[2] # Optional step
            params['limit'] = limit # Range queries also support limit
        else:
            endpoint = "loki/api/v1/query"
            params['limit'] = limit
            # Optional 'time' param for instant query time, defaults to now

        try:
            response = self._make_request('GET', endpoint, params=params)
            return response.json() # Return parsed JSON
        except Exception as e:
            logger.error(f"Failed to execute LogQL query '{logql_query}': {e}")
            return None # Indicate error

    def check_connection(self):
        """Checks if the Loki instance is reachable and ready."""
        endpoint = "ready" # Use the /ready endpoint
        try:
            response = self._make_request('GET', endpoint)
            logger.info(f"Loki readiness check successful: {response.text.strip()}")
            return True
        except Exception as e:
            logger.warning(f"Loki readiness check failed: {e}")
            return False