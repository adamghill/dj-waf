from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase


class TestCreateWafRulesCommand(TestCase):
    @patch("dj_waf.management.commands.create_waf_rules.import_string")
    @patch(
        "django.conf.settings.WAF",
        {
            "default": {
                "BACKEND": "dj_waf.backends.cloudflare.CloudflareBackend",
                "OPTIONS": {"apikey": "test-key", "domain": "example.com"},
            }
        },
    )
    def test_handle_with_backend(self, mock_import_string):
        # Setup
        mock_backend = MagicMock()
        mock_import_string.return_value = mock_backend

        # Test
        call_command("create_waf_rules", "--backend=default")

        # Verify
        mock_backend.assert_called_once_with({"apikey": "test-key", "domain": "example.com"})
        mock_backend.return_value.handle.assert_called_once()
