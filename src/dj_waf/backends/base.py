import json
import urllib.error
import urllib.request

from dj_waf.exceptions import WafError, WafSettingsError


class WafBackend:
    def __init__(self, backend_options: dict):
        self.backend_options = backend_options

        if not self.backend_options:
            raise WafSettingsError("Cloudflare settings not found")

        if not self.backend_options.get("apikey"):
            raise WafSettingsError("API key not found in settings")

        self.apikey = self.backend_options.get("apikey")

    def request(self, url: str, method="GET", headers: dict | None = None, data: dict | None = None):
        headers = headers or {"Authorization": f"Bearer {self.apikey}", "Content-Type": "application/json"}

        encoded_data = None

        if data is not None:
            encoded_data = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, method=method, headers=headers, data=encoded_data)  # noqa: S310

        try:
            with urllib.request.urlopen(req) as response:  # noqa: S310
                data = json.loads(response.read().decode())

                if data.get("success"):
                    return data
                else:
                    raise WafError(f"Failed to get JSON data: {data.get('errors')}")
        except urllib.error.HTTPError as e:
            raise WafError(f"HTTP Error {e.code}: {e.read().decode()}") from e
        except urllib.error.URLError as e:
            raise WafError(f"URL Error: {e.reason}") from e
