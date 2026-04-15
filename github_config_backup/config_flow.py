"""Config flow for GitHub Config Backup integration."""
import voluptuous as vol
from homeassistant import config_entries
from .const import (
    DOMAIN,
    CONF_REPO,
    CONF_TOKEN,
    CONF_NAME,
    CONF_EMAIL,
    CONF_INTERVAL,
    CONF_PATHS,
)

class GitHubBackupConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GitHub Config Backup."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Sla de gegevens op en maak de integratie aan
            return self.async_create_entry(title="GitHub Backup", data=user_input)

        # Toon het formulier in de UI
        data_schema = vol.Schema(
            {
                vol.Required(CONF_REPO): str,
                vol.Required(CONF_TOKEN): str,
                vol.Optional(CONF_NAME, default="Home Assistant"): str,
                vol.Optional(CONF_EMAIL, default="homeassistant@local.host"): str,
                vol.Optional(CONF_INTERVAL, default=3600): int,
                vol.Optional(CONF_PATHS, default="configuration.yaml, template/"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema
        )