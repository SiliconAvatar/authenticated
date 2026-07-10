"""Constants for authenticated."""

DOMAIN = "authenticated"
INTEGRATION_VERSION = "1.0.0"
ISSUE_URL = "https://github.com/SiliconAvatar/authenticated/issues"

STARTUP = f"""
-------------------------------------------------------------------
{DOMAIN}
Version: {INTEGRATION_VERSION}
This is a custom component
If you have any issues with this you need to open an issue here:
https://github.com/SiliconAvatar/authenticated/issues
-------------------------------------------------------------------
"""


CONF_NOTIFY = "enable_notification"
CONF_EXCLUDE = "exclude"
CONF_EXCLUDE_CLIENTS = "exclude_clients"
CONF_PROVIDER = "provider"

DEFAULT_NOTIFY = True
DEFAULT_EXCLUDE = []
DEFAULT_EXCLUDE_CLIENTS = []
DEFAULT_PROVIDER = "ipwhois"

OUTFILE = ".ip_authenticated.yaml"
