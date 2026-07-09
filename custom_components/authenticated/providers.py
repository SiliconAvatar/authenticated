"""Providers"""
import logging
import requests

_LOGGER = logging.getLogger(__name__)

PROVIDERS = {}


def register_provider(classname):
    """Decorator used to register providers."""
    PROVIDERS[classname.name] = classname
    return classname


class GeoProvider:
    """GeoProvider class."""

    url = None
    request_timeout = 5

    def __init__(self, ipaddr):
        """Initialize."""
        self.result = None
        self.ipaddr = ipaddr

    @property
    def country(self):
        """Return country name or None."""
        return (self.result or {}).get("country")

    @property
    def region(self):
        """Return region name or None."""
        return (self.result or {}).get("region")

    @property
    def city(self):
        """Return city name or None."""
        return (self.result or {}).get("city")

    @property
    def computed_result(self):
        """Return the computed result."""
        if self.result is not None:
            return {"country": self.country, "region": self.region, "city": self.city}
        return None

    def update_geo_info(self):
        """Update Geo Information."""
        self.result = None
        if self.url is None:
            return

        try:
            api = self.url.format(self.ipaddr)
            header = {"user-agent": "Home Assistant/Python"}
            response = requests.get(api, headers=header, timeout=self.request_timeout)
            if response.status_code == 429:
                _LOGGER.warning("Geo-IP provider rate limit reached.")
                return
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            _LOGGER.warning("Geo-IP provider request timed out.")
            return
        except requests.exceptions.RequestException:
            _LOGGER.warning("Geo-IP provider request failed.")
            return
        except ValueError:
            _LOGGER.warning("Geo-IP provider returned invalid JSON.")
            return

        if not isinstance(data, dict):
            _LOGGER.warning("Geo-IP provider returned an unexpected response.")
            return

        if data.get("error"):
            if data.get("reason") == "RateLimited":
                _LOGGER.warning("Geo-IP provider rate limit reached.")
            else:
                _LOGGER.warning("Geo-IP provider returned an error.")
            return

        if data.get("status", "success") in ("error", "fail"):
            _LOGGER.warning("Geo-IP provider returned an error.")
            return

        if data.get("reserved"):
            return

        self.result = data
        self.parse_data()

    def parse_data(self):
        """Parse data from geoprovider."""
        self.result = self.result


@register_provider
class NoGeoLookup(GeoProvider):
    """Provider that intentionally skips external Geo-IP lookup."""

    name = "none"

    @property
    def computed_result(self):
        """Return no result because Geo-IP lookup is disabled."""
        return None


@register_provider
class IPApi(GeoProvider):
    """IPApi class."""

    url = "https://ipapi.co/{}/json/"
    name = "ipapi"

    @property
    def country(self):
        """Return country name or None."""
        return (self.result or {}).get("country_name")
