import json
import logging
from dataclasses import asdict, dataclass

from dj_waf.backends.base import WafBackend
from dj_waf.exceptions import WafError, WafSettingsError

logger = logging.getLogger(__name__)


@dataclass
class CloudflareWafRule:
    description: str
    expression: str
    action: str
    enabled: bool
    ruleset_id: str | None = None
    rule_id: str | None = None
    data: dict | None = None

    def to_dict(self):
        d = asdict(self)
        del d["ruleset_id"]
        del d["rule_id"]
        del d["data"]

        return d


class CloudflareBackend(WafBackend):
    def __init__(self, backend_options: dict):
        super().__init__(backend_options)

        if not self.backend_options.get("zone") and not self.backend_options.get("domain"):
            raise WafSettingsError("Domain and zone are not found in settings")

        self.apikey = self.backend_options["apikey"]
        self.domain = self.backend_options.get("domain")
        self.rules = []

        for rule in self.backend_options.get("rules", []):
            self.rules.append(CloudflareWafRule(**rule))

    def handle(self) -> None:
        """Handle creating or updating WAF rules."""

        logger.info(f"Looking up zone for domain: {self.domain}")
        self.zone_id = self.get_zone_id_by_domain()
        logger.debug(f"Domain '{self.domain}' has zone id: {self.zone_id}")

        if not self.zone_id:
            raise WafError(f'Zone for domain "{self.domain}" not found')

        # Check if ruleset exists
        for rule in self.rules:
            cloudflare_waf_rule = None

            try:
                cloudflare_waf_rule = self.find_cloudflare_waf_rule(rule)
            except WafError as e:
                pass

            if cloudflare_waf_rule and cloudflare_waf_rule.ruleset_id and cloudflare_waf_rule.rule_id:
                logger.info(f'Found existing "{rule.description}" rule, updating...')
                self.update_cloudflare_waf_rule(cloudflare_waf_rule)
                print(f"Successfully updated WAF rule: {rule.description} ✨")  # noqa: T201
            else:
                logger.info(f'No existing "{rule.description}" rule found, creating...')
                self.create_cloudflare_waf_rule(rule)
                print(f"Successfully created WAF rule: {rule.description} ✨")  # noqa: T201

    def get_zone_id_by_domain(self) -> str | None:
        """Get zone ID from domain name."""

        data = self.request(url=f"https://api.cloudflare.com/client/v4/zones?name={self.domain}")

        if data.get("success") and data.get("result"):
            return str(data["result"][0]["id"])

        return None

    def find_cloudflare_waf_rule(self, rule: CloudflareWafRule) -> CloudflareWafRule | None:
        """Find existing rule in the custom firewall ruleset."""

        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/rulesets/phases/http_request_firewall_custom/entrypoint"
        data = self.request(url=url)

        if data.get("success") and data.get("result"):
            cloudflare_waf_ruleset = data["result"]

            for cloudflare_waf_rule in cloudflare_waf_ruleset.get("rules", []):
                if cloudflare_waf_rule.get("description") == rule.description:
                    rule.ruleset_id = cloudflare_waf_ruleset["id"]
                    rule.rule_id = cloudflare_waf_rule["id"]

                    # Store the full rule data when updating the rule later.
                    rule.data = cloudflare_waf_rule

                    return rule

        return None

    def create_cloudflare_waf_rule(self, waf_rule):
        """Create new WAF rule by setting up the entrypoint."""

        payload = {"rules": [waf_rule.to_dict()]}
        data = json.dumps(payload).encode("utf-8")

        self.request(
            url=f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/rulesets/phases/http_request_firewall_custom/entrypoint",
            method="PUT",
            data=data,
        )

    def update_cloudflare_waf_rule(self, rule: CloudflareWafRule):
        """Update existing WAF rule"""

        existing_data = rule.data or {}

        # Merge with existing rule data to preserve fields like position
        payload = {
            **existing_data,
            **rule.to_dict(),
        }

        data = json.dumps(payload).encode("utf-8")

        self.request(
            url=f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/rulesets/{rule.ruleset_id}/rules/{rule.rule_id}",
            method="PATCH",
            data=data,
        )
