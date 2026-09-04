import requests
from dotenv import load_dotenv
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3 import Retry

load_dotenv()

BASE_URL = "https://api.tfl.gov.uk"
APP_KEY = os.getenv('TFL_API_KEY')

logger = logging.getLogger(__name__)

#Session maintains persistent TCP connection
def build_session():
    retry = Retry(
        total=3,
        backoff_factor=1,                           ## Increase time between retries by 1
        status_forcelist=(429, 500, 502, 503, 504), ## Retry on these calls
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session

new_session = build_session()

# Fetches data from API
def extract_data(endpoint):
    try:
        response = new_session.request(
            method="GET",
            url=f"{BASE_URL}{endpoint}",
            params={"app_key": APP_KEY},
            timeout=(3,5) ##Connect, Read
        )
        response.raise_for_status()
        if 'application/json' not in response.headers.get('Content-Type', ''):
            logger.warning("Response is not JSON")
            raise Exception("Response is not JSON")
        return response.json()
    except requests.exceptions.ReadTimeout:
        logger.error(f"Read request timed out after 5 seconds")
        raise
    except requests.exceptions.ConnectTimeout:
        logger.error(f"Connect request timed out after 3 seconds")
        raise
    except requests.exceptions.ConnectionError:
        logger.error("Connection failed - check URL and internet connection")
        raise
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        logger.error(f"HTTP Error {status}: {e}")
        error_messages = {
            400: "Invalid Request",
            401: "Unauthorised API key request",
            403: "Access denied",
            404: "Invalid URL",
            429: "Rate limit reached",
        }
        logger.error(error_messages.get(status, f"Server error: {status}"))
        raise
    except requests.exceptions.JSONDecodeError:
        logger.error("Failed to parse JSON response")
        raise
    except requests.exceptions.RetryError:
        logger.error("Retry request")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Unexpected error: {e}")
        raise






















