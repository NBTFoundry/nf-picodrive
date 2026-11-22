<!-- SPDX-License-Identifier: MPL-2.0 -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
    <img src="docs/assets/logo-light.svg" alt="NBTFoundry" height="44">
  </picture>
</p>

<h1 align="center">PicoDrive for NBT Manager</h1>

> **Warning: installing or modifying this software can brick your head unit. Recovery may require professional service or replacement, at your expense. Provided AS IS; use at your own risk, subject to applicable law.** [Read the risk and liability disclaimer](DISCLAIMER.md).

<p align="center">
  <b>Sega Mega Drive, Mega-CD, 32X and Master System games on the iDrive screen,</b><br>
  played with a USB gamepad or the iDrive controller.
</p>

**Supported head units:** BMW NBT Evo (iDrive 6). Support for the earlier NBT
may come later.

Part of [NBTFoundry](https://github.com/NBTFoundry):
[manager](https://github.com/NBTFoundry/manager) ·
[sdk](https://github.com/NBTFoundry/sdk) ·
[mobile-app](https://github.com/NBTFoundry/mobile-app) ·
[installer](https://github.com/NBTFoundry/installer) ·
[toolchains](https://github.com/NBTFoundry/toolchains)

Not affiliated with or endorsed by BMW AG, Sega or the PicoDrive authors. BMW,
iDrive and NBT are trademarks of BMW AG; Sega, Mega Drive, Genesis, Mega-CD,
Sega CD, 32X, Master System and Game Gear are trademarks of Sega Corporation. No
game or BIOS is included.

## Status

Work in progress: the port is being set up.

## Build

`git submodule update --init --recursive` fetches PicoDrive and the libraries
it bundles.

## Layout

| Path | Contents |
| --- | --- |
| `third_party/picodrive/` | PicoDrive (irixxxx/picodrive), unmodified (submodule) |
| `release/` | The SDK commit to build against |

## License

Copyright (c) 2026 Fabien Poussin. Original code, tests, build scripts and
documentation are licensed under **MPL-2.0**; see [LICENSE](LICENSE).
PicoDrive keeps its own non-commercial licence.
