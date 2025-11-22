# dj-waf 🙅

> Add WAF rules to block known bots and malicious traffic for Django applications

Provides easy integration with popular WAF services like Cloudflare.

## Features 🤩

- Create WAF rules in Cloudflare directly from Django.

## Installation

```bash
pip install dj-waf
```

OR

```bash
uv add dj-waf
```

## Usage

1. Add the app to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "dj_waf",
]
```

2. Configure your WAF settings in `settings.py`:

```python
# settings.py

WAF = {
    "default": {
        "BACKEND": "dj_waf.backends.cloudflare.CloudflareBackend",
        "OPTIONS": {
            "apikey": "cloudflare-waf-api-key",
            "domain": "your-example-domain.com",
            "rules": [
                {
                    "description": "dj-waf",
                    "expression": '(http.request.uri.path wildcard r"/wp-*") or (http.request.uri.path wildcard r"/*wp-*") or (http.request.uri.path wildcard r"/wordpress*") or (http.request.uri.path wildcard r"/*wordpress*") or (http.request.uri.path wildcard r"*.php") or (http.request.uri.path eq "/.env") or (http.request.uri.path wildcard r"/admin/*")',
                    "action": "block",
                    "enabled": True,
                }
            ],
        },
    },
}
```

3. Then run the management command to apply the rules:

```bash
python manage.py create_waf_rules
```

The command will create WAF rules in your configured WAF provider (e.g., Cloudflare) based on the rules defined in your WAF settings.

## Create Cloudflare API

1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click `Create Token`
3. Scroll to the bottom and click `Get started` in the "Create Custom Token" section
4. In the Permissions area, select `Zone`, `Zone Settings`, `Read`
5. Click `Add more`
6. Select `Zone`, `Zone WAF`, `Edit`
7. Click `Continue to summary`
8. Click `Create Token`
9. Copy API token from `User API Tokens` page

## Available Backends

- `cloudflare`

## Test 🧪

1. `uv install pip install -e .[dev]`
2. `just test`

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.
