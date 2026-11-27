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

PicoDrive's libretro core, unchanged, on the NBT App SDK's libretro host: Mega
Drive / Genesis, Mega-CD / Sega CD, 32X, Master System, Game Gear, SG-1000 and
SC-3000 games, the frame scaled to the car's panel, sound through the car's
speakers, battery saves, save states and a pause menu. Games come from a USB
stick or the NBT Manager phone app, copied to the head unit's hard disk.
Installed and launched through NBT Manager.

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
game or BIOS is included: use only games you have the right to use.

## Status

Built and tested on the desktop and in the SDK's VM under QEMU; not yet tested
in a car.

## Adding games

| System | Files |
| --- | --- |
| Mega Drive / Genesis | `.md`, `.gen`, `.smd`, `.bin` |
| 32X | `.32x` |
| Master System, Game Gear, SG-1000, SC-3000 | `.sms`, `.gg`, `.sg`, `.sc` |
| Mega-CD / Sega CD | a `.chd` image, or a folder (or zip archive) holding a `.cue` sheet and its tracks (`.bin`, `.iso`, `.wav`, `.mp3`, `.ogg`), or an `.m3u` playlist and its discs |

Files of up to 1 GiB each, 16 GiB in all (NBT Manager's `files` capability).

- **From a USB stick:** on the car, hold the push on PicoDrive in NBT Manager,
  then **Files** › **Import from a USB stick**. Cartridges are copied one by
  one; a zip archive is unpacked; a folder with a cue sheet (`Sonic CD/Sonic
  CD.cue` with its tracks) arrives as one game.
- **From the phone:** files up to 64 MiB: the NBT Manager app, the car,
  PicoDrive, **Files**, **Add files**.

**Mega-CD BIOS:** Mega-CD games need the console's BIOS, added as a game
is, named as PicoDrive looks for it: `bios_CD_U.bin` (US), `bios_CD_E.bin`
(Europe), `bios_CD_J.bin` (Japan), or its other names (`us_scd1_9210.bin`,
`eu_mcd1_9210.bin`, `jp_mcd1_9112.bin` and so on). The BIOS files are used,
not listed. The 32X, Master System and Game Gear need none.

The game list names each game by its file (or folder) name without the
extension.

## Playing

PicoDrive opens on its game list, the last game played focused. In a game,
the pause menu has Resume, Save state, Load state, the slot (1 to 4), the disc
(Mega-CD games with several), Reset, Choose another game and Quit. Battery
saves are written when they change and on leaving; they and the states stay
in PicoDrive's data folder across updates.

## Controls

Bindings are chosen for the pad plugged in, by its family; there is nothing to
set. Buttons are where the Mega Drive's six-button pad has them: A, B and C on
the left, bottom and right face buttons, Y on the top one, X and Z on the
shoulders. Master System buttons 1 and 2 are B and C. Pads are three-button
pads to the games, as in PicoDrive's libretro port: X, Y, Z and Mode reach
games that force the six-button pad.

| Mega Drive | Xbox | DualShock 4 / DualSense | iDrive controller | Desktop |
| --- | --- | --- | --- | --- |
| D-pad | D-pad or left stick | D-pad or left stick | Tilt | Arrows |
| A | X | Square | Favourite key 1 | Z |
| B (Master System 1) | A | Cross | Push | X |
| C (Master System 2) | B | Circle | BACK, tap | C |
| X / Z | LB / RB, LT / RT | L1 / R1, L2 / R2 | Turn the knob left / right | A / D |
| Y | Y | Triangle | Favourite key 2 | S |
| Mode | View | Share / Create | MEDIA | Right Shift |
| Start (Master System Pause) | Menu | Options | OPTION | Return |
| Pause menu | Xbox button, or View + Menu | PS button, or Share / Create + Options | MENU, or BACK held | Escape |
| Quit | from the menu | from the menu | BACK, long hold | from the menu |

In the menus the D-pad, left stick, knob or tilts move, the bottom button
(push) chooses and the right button (BACK) goes back; LB and RB (L1, R1) jump
ten games. The menus name the buttons of the pad in use, and a notice says
when a pad is plugged in or removed: the iDrive controller then plays. The
knob holds X or Z for 150 ms per detent. Which pads are supported is up to
NBT Manager (`NBTFoundry/manager: docs/gamepad-bridge.md`).

## Settings

Changed from the phone app or NBT Manager's settings page; they apply at once.

| Setting | Choices | Default |
| --- | --- | --- |
| Aspect | 4-3, pixel (whole multiples), full | 4-3 |
| Filter | sharp (crisp pixels, smoothed edges), smooth, nearest | sharp |
| Region | auto (from the game), us, europe (50 Hz), japan, japan_pal (50 Hz) | auto |
| Renderer | accurate, good, fast (faster, for games without mid-frame effects) | accurate |
| Sprite limit | on (as the console), off (less flicker, some glitches) | on |
| 32X recompiler | on (fast), off (the SH-2 interpreter: slow, for checks) | on |
| 68000 overclock | off, 25, 50, 100 (%: less slowdown, may glitch) | off |
| Sound | on, off | on |
| Show FPS | off, on | off |
| Debug log | off, on | off |

## Bridge

The package carries the module (built with the NBT toolchain, loaded by NBT
Manager's `nbt-runner`) and declares bridge 1.7: `show`, `controller`, `files`
and `runner` required, `status`, `live-settings` and `gamepad` optional, and
the files policy
`md,gen,smd,bin,32x,sms,gg,sg,sc,cue,iso,chd,m3u,wav,mp3,ogg|1024|16384|folders=m3u,cue`.
It also carries what the phone app shows before an install (the PicoDrive
version, the project, the licence, notices), so it needs NBT Manager 0.3.1 or
later. PicoDrive reports the game played as its status. NBT Manager keeps its
standard error as its log (shown, shared and cleared from the phone app); the
Debug log setting adds tracing and the core's debug messages.

## Build

Needs the NBT App SDK next to this repository (`../sdk`, or `NBT_SDK_DIR`), gcc,
GNU make 4.3 or newer, Python 3, and the X11, EGL and GLESv2
development files; Xvfb for the tests. `git submodule update --init --recursive`
fetches PicoDrive and the libraries it bundles.

```sh
make -j"$(nproc)" host test test-asan test-align check-static-init   # host binary and tests
./build/nbt-picodrive-host                                           # play on the desktop (X11)
```

The desktop build lists the games in `NBT_FILES_DIR` and keeps saves in
`NBT_DATA_DIR` (the current folder without it):
`NBT_FILES_DIR=~/megadrive NBT_DATA_DIR=/tmp/picodrive ./build/nbt-picodrive-host`,
or `--game <file>` to start one directly. The tests make a cartridge of their
own (a few 68000 instructions writing its battery RAM); no game is needed.
`test-align` plays it with the core under the alignment sanitizer: the head
unit stops a misaligned access with SIGBUS, which x86 never shows.

Head unit: PicoDrive is not GPL or LGPL code, so the application is a
**module** (`sdk/docs/native-apps.md`): built with the NBT toolchain (`make -C
../sdk toolchain` once) and loaded by the `nbt-runner` NBT Manager ships
(bridge 1.7, `runner`).

```sh
make -j"$(nproc)" module                                 # build/nbt-picodrive.so
make APP_KEY=/path/to/apps-signing-key.pem package       # build/picodrive-<version>.nbt
make vm-test                                             # the SDK's VM under QEMU
```

`package` signs the module with NBT Manager's packer
(`../manager/tools/package.py`, or `NBT_MGR_DIR`), described by
`release/package.args`; `make package-args` writes the PicoDrive version the pin
builds, and `make test` fails when it lags. `vm-test` runs it in the SDK's VM,
with the SDK's own `nbt-runner` (`sdk/docs/native-apps.md`, "Testing without a
head unit", says what building it takes). `make notice` writes
`legal/NOTICE.txt`.

### PicoDrive on the NBT toolchain

Upstream's own libretro Makefiles (`Makefile.libretro`, `Makefile`,
`platform/common/common.mak`) build the core, unchanged, in a copy of the
submodule per build kind under `build/core/` (upstream writes its objects next
to its sources); `tools/core.mk`, read after them, archives upstream's object
list into a static library. The module uses PicoDrive's C cores and renderers
(`NO_ARM_ASM=1`: FAME/C, CZ80; no Cyclone, DrZ80 or ARM assembly, which need a
generator and unaligned access), the SH-2 recompiler with its ARM back end for
the 32X (`ARCH=arm`), and the zlib and Tremor PicoDrive bundles. Two flags come
after upstream's own: `-w` and `-fno-lto` (its objects go into an archive).

## Releases

`.github/workflows/ci.yml` runs the host tests, the same under ASan/UBSan and
the alignment sanitizer, and the module build on every push and pull request. A
`vX.Y.Z` tag runs `.github/workflows/release.yml`: NBT Manager's application
release workflow builds the module on a plain runner with the NBT toolchain (no
private image), signs it with the apps key after a maintainer approves the run
(the `release` environment, secret `APPS_SIGNING_KEY`, tags `v*` only) and
publishes `picodrive-X.Y.Z.nbt`, sequence `X*1000000 + Y*1000 + Z`.
`release/sdk.ref` is the SDK commit both build against: [SDK
0.2.0](https://github.com/NBTFoundry/sdk/releases/tag/v0.2.0).

## To confirm on the head unit

- Full speed with sound (Show FPS) for Mega Drive, Mega-CD and 32X games:
  otherwise the Renderer setting, then `port-perf`.
- The 32X through the SH-2 recompiler, the first JIT in a module on the car.
- Mega-CD discs from a cue folder and a CHD image, with the BIOS beside them.
- The profile follows a pad plugged in and out; the iDrive controller plays
  without one.

## Layout

| Path | Contents |
| --- | --- |
| `third_party/picodrive/` | PicoDrive (irixxxx/picodrive), unmodified (submodule) |
| `src/main.cpp` | The application: the SDK's libretro host with PicoDrive's settings; the game list without the BIOS files |
| `src/controls.*` | The Mega Drive pad's layout for each pad family, the iDrive controller and the keyboard |
| `tests/` | Controls unit test (`controls_test.cpp`), health check, play and package tests (`test_picodrive.py`) |
| `tools/` | `core.mk` (upstream's objects into a library); PicoDrive's version for the package (`package_version.py`); notices (`make_notice.py`) |
| `release/` | The package description and the SDK commit to build against |

## License

Copyright (c) 2026 Fabien Poussin. Original code, tests, build scripts and
documentation are licensed under **MPL-2.0**; see [LICENSE](LICENSE).

PicoDrive keeps its own licence, the MAME license
([LICENSES/LicenseRef-PicoDrive.txt](LICENSES/LicenseRef-PicoDrive.txt)): no
sale, no commercial product or activity, the complete source of a modified
build published. Its CPU cores have their own non-commercial terms (FAME/C,
CZ80, the SH-2 core), as do the parts it takes from Genesis Plus GX. The
application's binary contains them and may be distributed only on those terms,
free of charge. The libraries PicoDrive bundles have their own licences (BSD,
MIT, zlib, public domain). Original NBTFoundry logos and artwork are MPL-2.0;
copyright permission for artwork does not grant trademark rights or imply
endorsement by BMW AG, Sega or the PicoDrive authors.

See [legal/README.md](legal/README.md) for third-party license notices.
