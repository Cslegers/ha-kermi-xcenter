# Third-party notices

This repository is licensed under the Apache License 2.0 (see [LICENSE](LICENSE))
and includes material from the projects below, reproduced under their own terms.

## ludeeus/integration_blueprint

The repository scaffolding is taken from
[ludeeus/integration_blueprint](https://github.com/ludeeus/integration_blueprint).
The following files are copied verbatim or with only project-specific values
changed:

```
.devcontainer.json
.gitattributes
.gitignore
.ruff.toml                          (lint scope narrowed; otherwise unchanged)
CONTRIBUTING.md
config/configuration.yaml           (logger domain changed)
requirements_common.txt
requirements_dev.txt                (Home Assistant version raised to 2026.9.1)
requirements_lint.txt
scripts/develop
scripts/lint
scripts/setup
.github/renovate.json
.github/ISSUE_TEMPLATE/bug.yml
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/feature_request.yml
.github/workflows/lint.yml
.github/workflows/validate.yml
```

Used under the MIT License:

```
MIT License

Copyright (c) 2019 - 2025  Joakim Sørensen @ludeeus

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Vendored: kermi-xcenter-modbus

`custom_components/kermi_xcenter/vendor/kermi_xcenter_modbus` is a copy of
[Cslegers/kermi-xcenter-modbus](https://github.com/Cslegers/kermi-xcenter-modbus),
Apache License 2.0. See that repository's own `NOTICE.md` for what it in turn
builds on.

## Home Assistant

The integration under `custom_components/kermi_xcenter` follows the structure of
the `trovis557x` integration on the
[`trovis557x-integration`](https://github.com/home-assistant/core/tree/trovis557x-integration/homeassistant/components/trovis557x)
branch of [home-assistant/core](https://github.com/home-assistant/core), and is
built on [`modbus-connection`](https://github.com/home-assistant-libs/modbus-connection).
Both are Apache License 2.0.

## Kermi

Register numbers, datapoint names, ranges and defaults are taken from Kermi's
*Kurzanleitung – Einbindung in externe Systeme* (document D00028482/05-2024) and
from Kermi's published Loxone template. These are used as factual interface
documentation.

This project is **not affiliated with, endorsed by, or supported by Kermi GmbH**.
"Kermi" and "x-center" are trademarks of their respective owner and are used
only to identify the equipment this software talks to.
