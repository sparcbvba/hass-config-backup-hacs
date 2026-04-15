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
    hub = GitHubBackupHub(hass, entry)
    
    # Combineer instellingen
    config_data = {**entry.data, **entry.options}
    interval_seconds = config_data.get(CONF_INTERVAL, 3600)

    async def async_timer_trigger(now):
        _LOGGER.debug("Automatische GitHub backup getriggerd door timer.")
        await hass.async_add_executor_job(hub.do_backup)

    remove_listener = async_track_time_interval(
        hass, async_timer_trigger, timedelta(seconds=interval_seconds)
    )

    hass.data[DOMAIN][entry.entry_id] = {
        "hub": hub,
        "remove_listener": remove_listener
    }

    # Registreer de Service / Action (Voorstel 2)
    async def handle_backup(call):
        _LOGGER.info("GitHub Backup handmatig getriggerd via service (actie).")
        await hass.async_add_executor_job(hub.do_backup)
    hass.services.async_register(DOMAIN, "push", handle_backup)

    # Luister naar wijzigingen in de opties (Voorstel 1)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Herlaad de integratie als de opties wijzigen."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    remove_listener = hass.data[DOMAIN][entry.entry_id].get("remove_listener")
    if remove_listener:
        remove_listener()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        # Verwijder de service als we de integratie verwijderen
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "push")
    return unload_ok