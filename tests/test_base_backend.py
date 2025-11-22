import json
import urllib
from unittest.mock import MagicMock, patch

import pytest

from dj_waf.backends.base import WafBackend
from dj_waf.exceptions import WafError, WafSettingsError


def test_no_apikey_raises_error():
    with pytest.raises(WafSettingsError, match="Cloudflare settings not found"):
        WafBackend({})


@patch("urllib.request.urlopen")
def test_request_success(mock_urlopen):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = json.dumps({"success": True, "result": {"id": "test"}}).encode("utf-8")

    # Set up the context manager behavior
    mock_urlopen.return_value.__enter__.return_value = mock_response

    # Test
    backend = WafBackend({"apikey": "test"})
    result = backend.request("http://example.com")

    # Verify
    assert result == {"success": True, "result": {"id": "test"}}
    assert mock_urlopen.called


@patch("urllib.request.urlopen")
def test_request_http_error(mock_urlopen):
    # Setup mock to raise HTTPError
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"message": "Forbidden"}'
    mock_urlopen.side_effect = urllib.error.HTTPError("http://example.com", 403, "Forbidden", {}, mock_response)

    # Test
    backend = WafBackend({"apikey": "test"})
    with pytest.raises(WafError, match="HTTP Error 403"):
        backend.request("http://example.com")
