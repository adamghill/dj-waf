from pathlib import Path

import pytest
from django.conf import settings


def pytest_configure():
    caches = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

    databases = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

    base_dir = Path(__file__).resolve().parent

    settings.configure(
        BASE_DIR=base_dir,
        DEBUG=False,
        ENVIRONMENT="unittest",
        SECRET_KEY="this-is-a-secret",
        ROOT_URLCONF="project.urls",
        CACHES=caches,
        AXES_ENABLED=False,
        COMPRESS_ENABLED=False,
        INSTALLED_APPS=(
            # django apps
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sites",
            "django.contrib.admin",
            "django.contrib.sessions",
            "dj_waf",
        ),
        DATABASES=databases,
        WAF={
            "default": {
                "BACKEND": "dj_waf.backends.cloudflare.CloudflareBackend",
                "OPTIONS": {
                    "apikey": "test-api-key",
                    "domain": "example.com",
                    "rules": [
                        {
                            "description": "test-rule",
                            "expression": "http.host eq 'example.com'",
                            "action": "block",
                            "enabled": True,
                        }
                    ],
                },
            }
        },
    )


@pytest.fixture(autouse=True)
def reset_settings(settings):
    """
    This takes the original settings before the test is run, runs the test, and then resets them afterwards.
    This is required because mutating nested dictionaries does not reset them as expected by `pytest-django`.
    More details in https://github.com/pytest-dev/pytest-django/issues/601#issuecomment-440676001.
    """

    # Get original settings
    cache_settings = {**settings.CACHES}

    # Run test
    yield

    # Re-set original settings
    settings.CACHES = cache_settings
