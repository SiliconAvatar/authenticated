"""Authentication data source helpers for Authenticated."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import os
from ipaddress import ip_address as validate_ip, ip_network

_LOGGER = logging.getLogger(__name__)


def load_authentications(hass, exclude, exclude_clients):
    """Load users and latest refresh-token usage by IP address.

    Prefer Home Assistant's already-loaded auth manager data so this component does
    not need to parse the private storage file during normal operation. The storage
    file reader remains as a compatibility fallback for older Home Assistant builds
    or unusual startup timing where the in-memory auth store is unavailable.
    """
    manager_users, manager_tokens = _load_from_auth_manager(
        hass, exclude, exclude_clients
    )
    if manager_tokens:
        return manager_users, manager_tokens

    storage_authentications = _load_from_auth_storage(
        hass.config.path(".storage/auth"), exclude, exclude_clients
    )
    if not storage_authentications:
        if manager_users:
            return manager_users, {}
        return storage_authentications

    storage_users, storage_tokens = storage_authentications
    if storage_tokens:
        return storage_users or manager_users, storage_tokens

    if manager_users:
        return manager_users, {}

    return storage_users, storage_tokens


def _load_from_auth_manager(hass, exclude, exclude_clients):
    """Load auth data from Home Assistant's in-memory auth manager."""
    auth = getattr(hass, "auth", None)
    store = getattr(auth, "_store", None)  # pylint: disable=protected-access
    if store is None:
        return {}, {}

    try:
        raw_users = getattr(store, "_users", None)  # pylint: disable=protected-access
        if not raw_users:
            return {}, {}

        users = {
            user_id: getattr(user, "name", None) or "Unknown"
            for user_id, user in raw_users.items()
        }

        get_refresh_tokens = getattr(store, "async_get_refresh_tokens", None)
        if get_refresh_tokens is None:
            return users, {}

        tokens = {}
        for refresh_token in get_refresh_tokens():
            token_data = _refresh_token_to_dict(refresh_token)
            _add_token(tokens, token_data, exclude, exclude_clients)

        return users, tokens
    except Exception:  # pylint: disable=broad-except
        _LOGGER.debug("Unable to read Home Assistant auth manager data.")
        return {}, {}


def _load_from_auth_storage(authfile, exclude, exclude_clients):
    """Load auth data from Home Assistant's auth storage compatibility file."""
    if not os.path.exists(authfile):
        _LOGGER.critical("File is missing %s", authfile)
        return False

    try:
        with open(authfile, "r") as auth_file:
            auth = json.loads(auth_file.read())
    except (OSError, json.JSONDecodeError) as exception:
        _LOGGER.error("Unable to read Home Assistant auth storage: %s", exception)
        return {}, {}

    data = auth.get("data") or {}
    users = {}
    for user in data.get("users") or []:
        user_id = user.get("id")
        if user_id is not None:
            users[user_id] = user.get("name") or "Unknown"

    tokens = {}
    for token in data.get("refresh_tokens") or []:
        _add_token(tokens, token, exclude, exclude_clients)

    return users, tokens


def _refresh_token_to_dict(refresh_token):
    """Convert a Home Assistant refresh token object to the legacy dict shape."""
    user = getattr(refresh_token, "user", None)
    user_id = getattr(user, "id", None) or getattr(refresh_token, "user_id", None)
    last_used_at = getattr(refresh_token, "last_used_at", None)

    return {
        "client_id": getattr(refresh_token, "client_id", None),
        "last_used_at": _format_last_used_at(last_used_at),
        "last_used_ip": getattr(refresh_token, "last_used_ip", None),
        "user_id": user_id,
    }


def _format_last_used_at(last_used_at):
    """Return last-used timestamps in the string format expected by the sensor."""
    if isinstance(last_used_at, datetime):
        return last_used_at.isoformat()
    return last_used_at


def _parse_last_used_at(value):
    """Parse Home Assistant auth timestamps for safe comparison."""
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        timestamp = value.strip()
        if not timestamp:
            return None

        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            try:
                parsed = datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return None
    else:
        return None

    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _add_token(tokens, token, exclude, exclude_clients):
    """Add a token to the latest-token-per-IP mapping if it should be tracked."""
    last_used_ip = token.get("last_used_ip")
    last_used_at = token.get("last_used_at")
    client_id = token.get("client_id")

    if last_used_ip is None or last_used_at is None:
        return

    try:
        ipaddr = validate_ip(last_used_ip)
    except ValueError:
        return

    if _is_excluded_ip(ipaddr, exclude):
        return

    if client_id in exclude_clients:
        return

    parsed_last_used_at = _parse_last_used_at(last_used_at)
    if parsed_last_used_at is None:
        return

    if last_used_ip in tokens:
        stored_last_used_at = _parse_last_used_at(tokens[last_used_ip]["last_used_at"])
        if (
            stored_last_used_at is not None
            and parsed_last_used_at <= stored_last_used_at
        ):
            return

    tokens[last_used_ip] = {
        "last_used_at": last_used_at,
        "user_id": token.get("user_id"),
    }


def _is_excluded_ip(ipaddr, exclude):
    """Return true if an IP address matches an excluded network."""
    for excludeaddress in exclude:
        try:
            if ipaddr in ip_network(excludeaddress, False):
                return True
        except ValueError:
            _LOGGER.warning("Ignoring invalid excluded IP network.")
    return False
