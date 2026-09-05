"""HTTP client for the API data extracting.

Owns the transport concerns of talking to an API: connection pooling, retry
policy, timeouts, status-code handling and JSON validation. Returns parsed
JSON or raises; callers decide what a failure means.

Deliberately knows nothing about API's data shapes - lines, end points and
arrivals are the caller's concern.
"""
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3 import Retry

def build_session():
    """Build a requests Session with a polite retry policy.

        Returns:
            requests.Session: pooled requests session that retries failed requests with an exponential backoff.
    """
    retry = Retry(
        total=3,
        backoff_factor=1,                           # urllib3 waits backoff_factor * 2**(n-1) seconds, so: 0s, 2s, 4s.
        status_forcelist=(429, 500, 502, 503, 504), # Retry on these calls
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


class APIClient:
    """
    Thin HTTP Client for talking to an API.
    All attributes are private, the caller is only responsible for fetching data from an API using appropriate end points

    Args:
        base_url: API domain
        app_key: API key
        session: Optional pre-built session. Defaults to `build_session()`.
            Injectable so tests can supply a fake and run without network.

    Example:
        client = Client("https://api.tfl.gov.uk", app_key)
        client.fetch("/Line/victoria/Status")
        Fetches the Victoria Line status from the TfL's API
    """

    _logger = logging.getLogger(__name__)
    def __init__(self, base_url, app_key, session = None):
        self._base_url = base_url
        self._app_key = app_key
        self._session = build_session() if session is None else session

    def fetch(self, endpoint):
        """
        Fetch data from an API endpoint.

        Args:
            endpoint: API's endpoint to fetch

        Returns:
            response: The decoded JSON response

        Raises:
            ValueError: The response is not JSON
            requests.exceptions.Timeout: Connect request timed out
            requests.exceptions.HTTPError: If the HTTP request failed
            requests.exceptions.RequestException: Unknown error:
            requests.exceptions.ConnectionError: Connection error
            requests.exceptions.InvalidURL: Invalid URL
            requests.exceptions.JSONDecodeError: Failed to convert to JSON
            requests.exceptions.RequestException: Unknown error
        """
        try:
            response = self._session.request(
                method="GET",
                url=f"{self._base_url}{endpoint}",
                params={"app_key": self._app_key},
                timeout=(3,5) ##Connect, Read
            )
            response.raise_for_status()
            if 'application/json' not in response.headers.get('Content-Type', ''):
                self._logger.error("Response is not JSON")
                raise ValueError(f"Non-JSON response from {endpoint}", response)
            return response.json()
        except requests.exceptions.InvalidURL:
            self._logger.error("Invalid URL", endpoint)
        except requests.exceptions.Timeout:
            self._logger.error(f"Request timed out")
            raise
        except requests.exceptions.ConnectionError:
            self._logger.error("Connection failed - check URL and internet connection", endpoint)
            raise
        except requests.exceptions.JSONDecodeError:
            self._logger.error("Failed to convert to JSON")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            error_messages = {
                400: "Invalid Request",
                401: "Unauthorised API key request",
                403: "Access denied",
                404: "Invalid URL",
                429: "Rate limit reached",
            }
            self._logger.error(error_messages.get(status, f"Server error: {status}"), endpoint)
            raise
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Unexpected error: {e}", endpoint)
            raise
























