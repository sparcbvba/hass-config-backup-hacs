"""Sensor platform for GitHub Config Backup."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform."""
    # Haal de Hub op uit het geheugen
    hub = hass.data[DOMAIN][entry.entry_id]["hub"]
    async_add_entities([GitHubBackupStatusSensor(entry, hub)])

class GitHubBackupStatusSensor(SensorEntity):
    """Representation of the status sensor."""

    def __init__(self, entry: ConfigEntry, hub):
        """Initialize the sensor."""
        self._entry = entry
        self._attr_name = "GitHub Backup Status"
        self._attr_unique_id = f"{entry.entry_id}_backup_status"
        self._attr_native_value = "Inactief (Klaar voor gebruik)"
        self._attr_icon = "mdi:cloud-check"
        
        # Koppel de update functie aan de Hub
        hub.set_sensor_callback(self.update_state)

    def update_state(self, new_state):
        """Callback to update the sensor state from the Hub."""
        self._attr_native_value = new_state
        self.async_write_ha_state()