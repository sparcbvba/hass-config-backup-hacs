"""Config flow for GitHub Config Backup integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_REPO, CONF_TOKEN, CONF_NAME, CONF_EMAIL, CONF_INTERVAL, CONF_PATHS

class GitHubBackupConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GitHub Config Backup."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="GitHub Backup", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_REPO): str,
            vol.Required(CONF_TOKEN): str,
            vol.Optional(CONF_NAME, default="Home Assistant"): str,
            vol.Optional(CONF_EMAIL, default="homeassistant@local.host"): str,
            vol.Optional(CONF_INTERVAL, default=3600): int,
            vol.Optional(CONF_PATHS, default="configuration.yaml, template/"): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Vertel HA dat we een optie-menu hebben."""
        return GitHubBackupOptionsFlowHandler(config_entry)

class GitHubBackupOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Combineer originele data met eventuele bestaande opties
        config = {**self.config_entry.data, **self.config_entry.options}

        options_schema = vol.Schema({
            vol.Required(CONF_REPO, default=config.get(CONF_REPO)): str,
            vol.Required(CONF_TOKEN, default=config.get(CONF_TOKEN)): str,
            vol.Optional(CONF_NAME, default=config.get(CONF_NAME, "Home Assistant")): str,
            vol.Optional(CONF_EMAIL, default=config.get(CONF_EMAIL, "homeassistant@local.host")): str,
            vol.Optional(CONF_INTERVAL, default=config.get(CONF_INTERVAL, 3600)): int,
            vol.Optional(CONF_PATHS, default=config.get(CONF_PATHS, "configuration.yaml, template/")): str,
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)