"""Button platform for GitHub Config Backup."""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the button platform."""
    # Haal de Hub op uit het geheugen
    hub = hass.data[DOMAIN][entry.entry_id]["hub"]
    async_add_entities([GitHubBackupButton(entry, hub)])

class GitHubBackupButton(ButtonEntity):
    """Representation of a manual backup button."""

    def __init__(self, entry: ConfigEntry, hub):
        """Initialize the button."""
        self._entry = entry
        self._hub = hub
        self._attr_name = "GitHub Backup Nu"
        self._attr_unique_id = f"{entry.entry_id}_backup_button"
        self._attr_icon = "mdi:github"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Git operaties zijn 'blocking', dus we draaien dit op de achtergrond (executor job)
        await self.hass.async_add_executor_job(self._hub.do_backup)