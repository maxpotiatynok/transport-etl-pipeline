from unittest.mock import Mock
import pytest
from transport_elt_pipeline import apiclient
import requests

MOCK_BASE_URL = "https://example.com"

@pytest.fixture()
def session():
    session = Mock(spec=requests.Session)
    yield session

@pytest.fixture()
def apiclient_object():
    fixture_apiclient = apiclient.APIClient(MOCK_BASE_URL)
    yield fixture_apiclient

@pytest.fixture()
def apiclient_object_custom_session(session):
    fixture_apiclient = apiclient.APIClient(MOCK_BASE_URL, session=session)
    yield fixture_apiclient

def test_apiclient_object_exist(apiclient_object):
    assert apiclient_object is not None

def test_apiclient_object_custom_session(apiclient_object_custom_session):
    assert apiclient_object_custom_session is not None

HEADER = "/api"
def test_fetch(apiclient_object_custom_session, session):
    response = Mock()
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.json.return_value = {'key': 'value'}
    session.request.return_value = response
    client = apiclient_object_custom_session
    result = client.fetch(HEADER)
    # Asserts
    assert result == {'key': 'value'}
    session.request.assert_called_once_with(
        method="GET",
        url=MOCK_BASE_URL + HEADER,
        params={"app_key": None},
        timeout=(apiclient.FETCH_CONNECT_TIMEOUT, apiclient.FETCH_READ_TIMEOUT),
    )
