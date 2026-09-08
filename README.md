# Kermi x-center for Home Assistant

> ### This is not an official Kermi integration
>
> An independent, community-built project. It is **not affiliated with, endorsed
> by, or supported by Kermi GmbH**, and Kermi provides no support for it. Do not
> raise problems with it to Kermi — [open an issue here](https://github.com/Cslegers/ha-kermi-xcenter/issues)
> instead. It writes to a heat pump; use it at your own risk.

A Home Assistant integration for Kermi x-center heat pump controllers, over
local Modbus TCP. No cloud, no account, no polling of anything but your own
controller.

Install this to try it out and report problems. It is the community-testing
build of an integration intended for Home Assistant core.

> **Requires Home Assistant 2026.9.0 or newer.** It is built on the shared
> Modbus connections the `modbus` integration began handing out in 2026.9.0.

## What you get

The integration discovers which Modbus modules your installation actually has
and creates a device for each one.

- **Heat pump** — outdoor, source inlet/outlet, flow and return temperatures;
  flow rate; coefficient of performance overall and per mode; thermal and
  electrical power; compressor, fan and storage pump run times; run state; and
  an alarm binary sensor.
- **Heating storage / hot water storage** — store and tank temperatures, a
  `water_heater` entity for hot water (including the one-shot charge as the
  high-demand mode), a `climate` entity for the heating circuit, and the
  heating curve thresholds as `number` entities.
- **Photovoltaic feed-in** — a `number` entity you write your solar surplus to.

Entities that are noisy or rarely wanted are created disabled; enable them from
the device page.

## Photovoltaic surplus

If Kermi has enabled the feed-in register for your installation, you get a
`number.photovoltaic_feed_in_photovoltaic_surplus` entity. Write your inverter's
current surplus to it and the controller modulates the heat pump against it.
The entity is in **whole watts**: set it to 3500 to offer 3500 W.

```yaml
automation:
  - alias: Send solar surplus to the heat pump
    triggers:
      - trigger: state
        entity_id: sensor.inverter_surplus_power
    actions:
      - action: number.set_value
        target:
          entity_id: number.photovoltaic_feed_in_photovoltaic_surplus
        data:
          value: "{{ [states('sensor.inverter_surplus_power') | int(0), 0] | max }}"
```

The heat pump's own photovoltaic target temperatures are exposed as `number`
entities too, so an automation can raise the hot water target while the sun is
out.

> **The feed-in register is undocumented.** It appears in no Kermi document.
> Kermi enables the excess-solar function per installation and tells you the
> address it lives on — see [Before you install](#before-you-install). If it has
> not been enabled for you, the entity simply does not appear.

## Before you install

**Kermi has to switch two things on for you, and they are separate requests.**

1. **The Modbus interface itself.** Kermi's own integration guide states that
   release and configuration of the interface is done by the manufacturer.
   Without this, nothing here responds at all.
2. **The excess-solar / PV modulation function.** Enabling Modbus does *not*
   enable this. It is a separate feature, released per installation, and it is
   what makes the photovoltaic feed-in address exist. Ask for it explicitly if
   you want to send solar surplus to the heat pump.

Everything except the photovoltaic surplus entity works with only the first.
If you have Modbus but not the second, the integration still sets up — the
feed-in device simply does not appear.

You also need interface module firmware v1.6.1.66 or later.

Give the interface module a static IP address, or at least a DHCP reservation —
its address can otherwise move after a power cut and the integration will stop
finding it.

## Installation

### HACS

1. In HACS, add `https://github.com/Cslegers/ha-kermi-xcenter` as a custom
   repository of type *Integration*.
2. Install **Kermi x-center**, then restart Home Assistant.
3. Go to *Settings → Devices & Services → Add Integration* and search for
   **Kermi x-center**.

### Manual

Copy `custom_components/kermi_xcenter` into your `config/custom_components`
directory and restart Home Assistant.

## Configuration

The integration asks for the interface module's host and port, plus the Modbus
device addresses. The defaults are the ones Kermi ships:

| Module | Device address |
| --- | --- |
| Heat pump | 40 |
| Storage system module, heating | 50 |
| Storage system module, hot water | 51 |
| Heating circuit / universal module | 30 |
| Photovoltaic surplus feed-in | 2 |

Only the heat pump has to answer. Anything else that does not respond is
treated as not fitted and skipped, so leaving the defaults alone is normally
right — change one only if your installer did.

## How this repository is built

There is no hand-written integration code here. Everything under
`custom_components/kermi_xcenter` is generated by `scripts/vendor_sync` from
two upstream repositories:

- [`kermi-xcenter-modbus`](https://github.com/Cslegers/kermi-xcenter-modbus)
  — the standalone device library, vendored into `vendor/` so this installs
  through HACS without waiting on a PyPI release.
- [`kermi-xcenter-core`](https://github.com/Cslegers/kermi-xcenter-core)
  — the integration as it is staged for Home Assistant core.

Change those, then re-run `scripts/vendor_sync`. CI re-runs it and fails if the
committed result differs.

## Development

```bash
scripts/setup     # install Home Assistant and the dev dependencies
scripts/develop   # run Home Assistant with this integration loaded
scripts/lint      # ruff
```

## Icon

HACS shows no icon for this integration yet. Icons are not set from this
repository — they come from [home-assistant/brands](https://github.com/home-assistant/brands),
which needs a pull request adding `custom_integrations/kermi_xcenter/icon.png`
(256×256, transparent background) and optionally `logo.png`. Until then HACS
falls back to a placeholder; `.github/workflows/validate.yml` passes
`ignore: brands` so validation still succeeds.

## Credits and licence

Apache License 2.0 — see [LICENSE](LICENSE).

This project reuses substantial material from other projects. See
[NOTICE.md](NOTICE.md) for the full list and their licence terms. In summary:

- Repository scaffolding — CI workflows, dev container, lint config, helper
  scripts, issue templates — is copied from
  [ludeeus/integration_blueprint](https://github.com/ludeeus/integration_blueprint)
  (MIT, © Joakim Sørensen), mostly verbatim.
- The integration's structure follows the `trovis557x` integration on the
  [trovis557x-integration](https://github.com/home-assistant/core/tree/trovis557x-integration/homeassistant/components/trovis557x)
  branch of home-assistant/core (Apache-2.0).
- The device library is
  [Cslegers/kermi-xcenter-modbus](https://github.com/Cslegers/kermi-xcenter-modbus),
  built on [`modbus-connection`](https://github.com/home-assistant-libs/modbus-connection).
- Register numbers, names, ranges and defaults come from Kermi's
  *Kurzanleitung – Einbindung in externe Systeme* (D00028482/05-2024).

**No code** is taken from the other Kermi projects that exist
([py-kermi-xcenter](https://github.com/jr42/py-kermi-xcenter), the
[openHAB binding](https://www.openhab.org/addons/bindings/modbus.kermi/),
[kermi-ha-bridge](https://github.com/m-zenker/kermi-ha-bridge)); they were read
while researching the interface, nothing more.

Not affiliated with, endorsed by, or supported by Kermi GmbH. "Kermi" and
"x-center" are trademarks of their respective owner, used only to identify the
equipment this software talks to.
