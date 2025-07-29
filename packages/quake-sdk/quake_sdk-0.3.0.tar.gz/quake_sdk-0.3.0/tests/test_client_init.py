import pytest

from quake_sdk.client import QuakeClient
from .conftest import API_KEY

class TestQuakeClientInit:
    def test_client_initialization(self, client: QuakeClient):
        assert client.api_key == API_KEY # Using API_KEY from conftest
        assert client._session.headers["X-QuakeToken"] == API_KEY

    def test_client_initialization_empty_api_key(self):
        with pytest.raises(ValueError, match="API key cannot be empty."):
            QuakeClient(api_key="")
