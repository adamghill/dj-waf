import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create or update WAF to block bots."

    def add_arguments(self, parser):
        parser.add_argument(
            "--backend",
            type=str,
            help="Backend",
            default="default",
        )

        parser.add_argument(
            "--apikey",
            type=str,
            help="API key",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        backend_option = options.get("backend")

        if not backend_option:
            raise CommandError("Backend not specified")

        backend_settings = settings.WAF[backend_option]
        backend_import_str = backend_settings["BACKEND"]
        backend_options = backend_settings["OPTIONS"] or {}
        backend_class = import_string(backend_import_str)

        logger.debug(f"Using backend class: {backend_class}")

        if apikey := options.get("apikey"):
            backend_options["apikey"] = apikey

        backend_class(backend_options).handle()
