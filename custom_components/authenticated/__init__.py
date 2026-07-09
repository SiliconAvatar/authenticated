"""The authenticated component."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, STARTUP

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


class AuthenticatedBaseException(Exception):
    """Base exception for Authenticated."""


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Authenticated from a config entry."""
    _LOGGER.info(STARTUP)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        **entry.data,
        **entry.options,
    }
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Authenticated config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options by reloading the config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
