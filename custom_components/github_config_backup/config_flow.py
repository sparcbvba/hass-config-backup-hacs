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
        super().__init__() # Interne Home Assistant initialisatie aanroepen
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # 1. Haal de opgeslagen data veilig op (val nooit terug op None)
        config_data = dict(self.config_entry.data)
        options_data = dict(self.config_entry.options) if self.config_entry.options else {}
        
        repo = options_data.get(CONF_REPO) or config_data.get(CONF_REPO) or ""
        token = options_data.get(CONF_TOKEN) or config_data.get(CONF_TOKEN) or ""
        name = options_data.get(CONF_NAME) or config_data.get(CONF_NAME) or "Home Assistant"
        email = options_data.get(CONF_EMAIL) or config_data.get(CONF_EMAIL) or "homeassistant@local.host"
        paths = options_data.get(CONF_PATHS) or config_data.get(CONF_PATHS) or "configuration.yaml, template/"

        # 2. Zorg dat het interval 100% zeker een integer (getal) is!
        try:
            interval = int(options_data.get(CONF_INTERVAL) or config_data.get(CONF_INTERVAL) or 3600)
        except (ValueError, TypeError):
            interval = 3600

        # 3. Bouw het formulier met strikte type-castings voor de default waarden
        options_schema = vol.Schema({
            vol.Required(CONF_REPO, default=str(repo)): str,
            vol.Required(CONF_TOKEN, default=str(token)): str,
            vol.Optional(CONF_NAME, default=str(name)): str,
            vol.Optional(CONF_EMAIL, default=str(email)): str,
            vol.Optional(CONF_INTERVAL, default=interval): int,
            vol.Optional(CONF_PATHS, default=str(paths)): str,
        })
        
        return self.async_show_form(step_id="init", data_schema=options_schema)