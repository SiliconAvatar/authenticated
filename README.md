# Authenticated

Authenticated is a Home Assistant custom integration that exposes the latest successful authentication as a sensor.

It tracks recent Home Assistant refresh-token activity by login IP address, stores known IP metadata in your Home Assistant config directory, and can optionally notify you when a new login IP is seen.

## Installation

### HACS

1. Add this repository to HACS as a custom repository.
2. Install **Authenticated** from HACS.
3. Restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration**.
5. Search for **Authenticated**.

### Manual

Copy `custom_components/authenticated` into your Home Assistant `custom_components` directory, then restart Home Assistant and add the integration from **Settings > Devices & services**.

## Configuration

The recommended setup is through the Home Assistant UI.

| Option | Default | Description |
| --- | --- | --- |
| Geo-IP lookup provider | `ipwhois` | Adds best-effort location details for login IPs. Choose `none` to avoid external lookups. |
| Notify for new login IPs | `true` | Creates a persistent notification when a previously unknown login IP is detected. |
| Ignored login IPs or networks | empty | Comma-separated IP addresses or CIDR ranges to ignore, such as `192.168.1.50` or `10.0.0.0/8`. |
| Ignored auth client IDs | empty | Comma-separated Home Assistant auth client IDs to ignore. This is intended for advanced filtering. |

Legacy YAML setup is still available during the transition:

```yaml
sensor:
  - platform: authenticated
```

Legacy YAML options use these keys:

| Key | Default | Description |
| --- | --- | --- |
| `platform` | required | Must be `authenticated`. |
| `provider` | `ipwhois` | One of `none`, `ipwhois`, `ipapi`, or `iplocation`. |
| `enable_notification` | `true` | Enables persistent notifications for new login IPs. |
| `exclude` | empty | IP addresses or networks to ignore. |
| `exclude_clients` | empty | Auth client IDs to ignore. |

## Geo-IP Lookup And Privacy

Geo-IP lookup is optional. The integration continues tracking successful authentication activity even when provider data is unavailable.

| Provider | Lookup URL | Location detail | Notes |
| --- | --- | --- | --- |
| `ipwhois` | `https://ipwho.is/{ip}` | Country, region, city | Default provider. |
| `ipapi` | `https://ipapi.co/{ip}/json/` | Country, region, city | Alternate full-location provider. |
| `iplocation` | `https://api.iplocation.net/?ip={ip}` | Country only | Country-level fallback. |
| `none` | none | none | Does not send login IPs to an external service. |

Choosing an external provider sends each newly detected login IP address to that provider. Choose `none` if you do not want login IPs sent to a third-party Geo-IP service.

## Entity

Authenticated creates a sensor named **Last successful authentication**. The sensor state is the latest tracked login IP address.

The sensor exposes these attributes when data is available:

| Attribute | Description |
| --- | --- |
| `hostname` | Reverse DNS hostname when available. |
| `country` | Geo-IP country when lookup is enabled and available. |
| `region` | Geo-IP region when lookup is enabled and available. |
| `city` | Geo-IP city when lookup is enabled and available. |
| `username` | Home Assistant user associated with the latest token use when available. |
| `new_ip` | Whether the latest IP was newly detected before notification handling. |
| `last_authenticated_time` | Latest token use timestamp. |
| `previous_authenticated_time` | Previous token use timestamp for that IP, when available. |

Known IP data is stored in `.ip_authenticated.yaml` in your Home Assistant config directory.

## Screenshots

![Sample overview](img/overview.png)

![Persistent notification](img/persistant_notification.png)

## Debug Logging

To enable debug logging:

```yaml
logger:
  default: warn
  logs:
    custom_components.authenticated: debug
```

## Security Resources

- [Home Assistant authentication](https://www.home-assistant.io/docs/authentication/)
- [Multi-factor authentication](https://www.home-assistant.io/docs/authentication/multi-factor-auth)
- [Securing Home Assistant](https://www.home-assistant.io/docs/configuration/securing/)
