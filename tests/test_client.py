import pytest
import client
import utils


@pytest.mark.parametrize("use_https", [True, False])
def test_client_default_url(use_https):
    protocol = "https" if use_https else "http"
    _client = client.ReedApiClient("", use_https=use_https)
    assert _client.base_url == utils.get_base_url(protocol=protocol)
