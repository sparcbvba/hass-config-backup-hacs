"""The GitHub Config Backup integration."""
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, CONF_INTERVAL
from .hub import GitHubBackupHub

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["button", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GitHub Config Backup from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Maak de Hub aan
    hub = GitHubBackupHub(hass, entry)
    
    # Haal de interval op (standaard 3600 seconden)
    interval_seconds = entry.data.get(CONF_INTERVAL, 3600)

    # De functie die door de timer wordt aangeroepen
    async def async_timer_trigger(now):
        _LOGGER.debug("Automatische GitHub backup getriggerd door timer.")
        await hass.async_add_executor_job(hub.do_backup)

    # Start de timer
    remove_listener = async_track_time_interval(
        hass, async_timer_trigger, timedelta(seconds=interval_seconds)
    )

    # Sla de hub en de timer-stop functie op in het geheugen
    hass.data[DOMAIN][entry.entry_id] = {
        "hub": hub,
        "remove_listener": remove_listener
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Stop de automatische timer
    remove_listener = hass.data[DOMAIN][entry.entry_id].get("remove_listener")
    if remove_listener:
        remove_listener()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok