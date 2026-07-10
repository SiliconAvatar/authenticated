"""Config flow for Authenticated."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_EXCLUDE,
    CONF_EXCLUDE_CLIENTS,
    CONF_NOTIFY,
    CONF_PROVIDER,
    DEFAULT_EXCLUDE,
    DEFAULT_EXCLUDE_CLIENTS,
    DEFAULT_NOTIFY,
    DEFAULT_PROVIDER,
    DOMAIN,
)
from .providers import PROVIDERS

PROVIDER_OPTIONS = [
    selector.SelectOptionDict(value="ipwhois", label="ipwho.is"),
    selector.SelectOptionDict(value="ipapi", label="ipapi.co"),
    selector.SelectOptionDict(
        value="iplocation", label="api.iplocation.net (country only)"
    ),
    selector.SelectOptionDict(value="none", label="No Geo-IP lookup"),
]


def _normalize_provider(value):
    """Return a supported provider name."""
    if value in PROVIDERS:
        return value
    return DEFAULT_PROVIDER


def _data_schema(defaults=None):
    """Return the config/options flow schema."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Optional(
                CONF_PROVIDER,
                default=_normalize_provider(defaults.get(CONF_PROVIDER)),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(options=PROVIDER_OPTIONS)
            ),
            vol.Optional(
                CONF_NOTIFY, default=defaults.get(CONF_NOTIFY, DEFAULT_NOTIFY)
            ): bool,
            vol.Optional(
                CONF_EXCLUDE,
                default=_list_to_csv(defaults.get(CONF_EXCLUDE, DEFAULT_EXCLUDE)),
            ): str,
            vol.Optional(
                CONF_EXCLUDE_CLIENTS,
                default=_list_to_csv(
                    defaults.get(CONF_EXCLUDE_CLIENTS, DEFAULT_EXCLUDE_CLIENTS)
                ),
            ): str,
        }
    )


def _normalize_user_input(user_input):
    """Normalize config flow input into integration config data."""
    return {
        CONF_PROVIDER: _normalize_provider(user_input.get(CONF_PROVIDER)),
        CONF_NOTIFY: user_input.get(CONF_NOTIFY, DEFAULT_NOTIFY),
        CONF_EXCLUDE: _csv_to_list(user_input.get(CONF_EXCLUDE, DEFAULT_EXCLUDE)),
        CONF_EXCLUDE_CLIENTS: _csv_to_list(
            user_input.get(CONF_EXCLUDE_CLIENTS, DEFAULT_EXCLUDE_CLIENTS)
        ),
    }


def _config_to_form(config):
    """Convert stored config to config flow form defaults."""
    return {
        CONF_PROVIDER: _normalize_provider(config.get(CONF_PROVIDER)),
        CONF_NOTIFY: config.get(CONF_NOTIFY, DEFAULT_NOTIFY),
        CONF_EXCLUDE: _list_to_csv(config.get(CONF_EXCLUDE, DEFAULT_EXCLUDE)),
        CONF_EXCLUDE_CLIENTS: _list_to_csv(
            config.get(CONF_EXCLUDE_CLIENTS, DEFAULT_EXCLUDE_CLIENTS)
        ),
    }


def _csv_to_list(value):
    """Convert a comma-separated string or existing list to a list."""
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _list_to_csv(value):
    """Convert a list or string to a comma-separated string."""
    if isinstance(value, list):
        return ", ".join(value)
    return value or ""


class AuthenticatedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Authenticated config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Authenticated",
                data=_normalize_user_input(user_input),
            )

        return self.async_show_form(step_id="user", data_schema=_data_schema())

    async def async_step_import(self, import_config):
        """Import YAML configuration."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="Authenticated",
            data={
                CONF_PROVIDER: _normalize_provider(import_config.get(CONF_PROVIDER)),
                CONF_NOTIFY: import_config.get(CONF_NOTIFY, DEFAULT_NOTIFY),
                CONF_EXCLUDE: import_config.get(CONF_EXCLUDE, DEFAULT_EXCLUDE),
                CONF_EXCLUDE_CLIENTS: import_config.get(
                    CONF_EXCLUDE_CLIENTS, DEFAULT_EXCLUDE_CLIENTS
                ),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return AuthenticatedOptionsFlow(config_entry)


class AuthenticatedOptionsFlow(config_entries.OptionsFlow):
    """Handle Authenticated options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=_normalize_user_input(user_input),
            )

        current_config = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init", data_schema=_data_schema(_config_to_form(current_config))
        )
