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

Add the app to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "dj_waf",
]
```

Configure your WAF settings in `settings.py`:

```python
# settings.py

WAF = {
    "default": {
        "BACKEND": "django_waf.backends.cloudflare.CloudflareBackend",
        "OPTIONS": {
            "apikey": "waf-cloudflare-api-key",
            "domain": "your-example-domain.com",
            "rules": [
                {
                    "description": "django-waf",
                    "expression": '(http.request.uri.path wildcard r"/wp-*") or (http.request.uri.path wildcard r"/*wp-*") or (http.request.uri.path wildcard r"/wordpress*") or (http.request.uri.path wildcard r"/*wordpress*") or (http.request.uri.path wildcard r"*.php") or (http.request.uri.path eq "/.env") or (http.request.uri.path wildcard r"/admin/*")',
                    "action": "block",
                    "enabled": True,
                }
            ],
        },
    },
}
```

Then run the management command to apply the rules:

```bash
python manage.py create_waf_rules
```

The command will create WAF rules in your configured WAF provider (e.g., Cloudflare) based on the rules defined in your WAF settings.

You can also configure multiple WAF providers and specify which one to use:

```bash
python manage.py create_waf_rules --backend cloudflare
```

To see all available options:

```bash
python manage.py create_waf_rules --help
```

## Available Backends

- `cloudflare`

## Test 🧪

1. `uv install pip install -e .[dev]`
2. `just test`

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.
