import json
from unittest.mock import MagicMock, patch

from django.test import TestCase

from dj_waf.backends.cloudflare import CloudflareBackend, CloudflareWafRule


class TestCloudflareWafRule(TestCase):
    def test_to_dict(self):
        rule = CloudflareWafRule(
            description="test-rule",
            expression="http.host eq 'example.com'",
            action="block",
            enabled=True,
            ruleset_id="123",
            rule_id="456",
        )

        result = rule.to_dict()

        assert result == {
            "description": "test-rule",
            "expression": "http.host eq 'example.com'",
            "action": "block",
            "enabled": True,
        }


class TestCloudflareBackend(TestCase):
    def setUp(self):
        self.backend_options = {
            "apikey": "test-api-key",
            "zone": "example.com",
            "rules": [
                {
                    "description": "test-rule",
                    "expression": "http.host eq 'example.com'",
                    "action": "block",
                    "enabled": True,
                }
            ],
        }
        self.backend = CloudflareBackend(self.backend_options)

    @patch("urllib.request.urlopen")
    def test_handle_creates_new_rule(self, mock_urlopen):
        # Setup
        self.backend.get_zone_id_by_domain = MagicMock(return_value="zone123")
        self.backend.find_cloudflare_waf_rule = MagicMock(return_value=None)

        # Create a proper response object with read() that returns bytes
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        # Make sure read() returns bytes, not a MagicMock
        mock_response.read.return_value = json.dumps({"success": True}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test
        self.backend.handle()

        # Verify
        assert mock_urlopen.call_count == 1
        request = mock_urlopen.call_args[0][0]
        assert request.method == "PUT"
        assert "zones/zone123/rulesets/phases/http_request_firewall_custom/entrypoint" in request.full_url
