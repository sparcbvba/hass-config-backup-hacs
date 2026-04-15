"""The GitHub Config Backup integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# We vertellen HA dat we later een Button en een Sensor gaan toevoegen
PLATFORMS = ["button", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GitHub Config Backup from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Sla de configuratie op in het geheugen van HA
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Laad de platforms (sensor en button)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok