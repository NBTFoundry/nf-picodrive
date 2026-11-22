<!-- SPDX-License-Identifier: MPL-2.0 -->
# Car test: PicoDrive before a release

Parked, ignition on. About 45 minutes, all from the phone: no adapter, no
computer.

Run it on a candidate before tagging a release, and whenever the car-side
behaviour changed. PicoDrive's libretro core is a **module**, loaded by the
`nbt-runner` NBT Manager ships (bridge 1.7). The main questions: Mega Drive,
Mega-CD and 32X games at full speed with sound (the 32X through PicoDrive's
SH-2 recompiler, the first JIT in a module on the car), Mega-CD discs from a
cue folder and a CHD image, no crash (SIGBUS) in any game.

## You need

- NBT Manager 0.3.1 or later on the car, and its phone app, paired.
- From the kit folder: the candidate `picodrive-<version>.nbt`, a second one
  with a higher sequence for part C, and their `SHA256SUMS` file. Add both to
  the phone app's library.
- A USB stick with games you own:
  - two or three **Mega Drive** games (`.md`, `.bin` or `.gen`; zipped is fine:
    the car unpacks them), one of them with **battery saves** (Phantasy Star,
    Shining Force, Sonic 3);
  - a **Master System** or **Game Gear** game;
  - a **32X** game (`.32x`: Virtua Racing Deluxe, Knuckles' Chaotix);
  - a **Mega-CD** game as a folder holding its `.cue` and tracks (Sonic CD,
    Snatcher), and if you have one, another as a `.chd` file;
  - the Mega-CD **BIOS** for your games' region: `bios_CD_E.bin`,
    `bios_CD_U.bin` or `bios_CD_J.bin` (or its other names, such as
    `eu_mcd1_9210.bin`), at the stick's top level.
- A USB gamepad (Xbox or DualShock 4 / DualSense), for part B.5.

## A. Install, health check, settings

| # | Do | Look for |
| --- | --- | --- |
| A0 | Phone: Library › open the candidate | Under the file name: **PicoDrive** (2.05 and a commit), **Project: PicoDrive (https://github.com/irixxxx/picodrive)**, **Licence: PicoDrive licence (non-commercial)**, then the text with the FAME and CZ80 credits, ending with the repository's address |
| A1 | Phone: Car › PicoDrive › install (or update to) the candidate; approve on the car | The health check passes (about 10 s), "Installed" |
| A2 | Car: hold the push on **picodrive** › settings | 10 settings: Aspect, Filter, Region, Renderer, Sprite limit, 32X recompiler, 68000 overclock, Sound, Show FPS, Debug log |
| A3 | Set **Show FPS: on**, **Debug log: on** | Kept when you leave and come back |

## B. Games, start and play

| # | Do | Look for |
| --- | --- | --- |
| B1 | Plug in the stick. Hold the push on **picodrive** › **Files** › **Import from a USB stick** | The cartridges listed one by one (a zip as the file inside it), the Mega-CD folder **as one entry**, the CHD and the BIOS; Import all |
| B2 | Files page | The games with their sizes; the Mega-CD folder as `<name>/` |
| B3 | Select **picodrive** | The list shows the games without their extensions, in name order; **no BIOS entry** |
| B4 | Start a Mega Drive game | Title screen with **sound**; FPS top right about 60 (50 for a European game) |
| B5 | Controls, iDrive: tilts the D-pad, push B, BACK tap C, favourite key 1 A, favourite key 2 Y, knob X / Z, MEDIA Mode, OPTION Start. Then plug the pad: a notice names it; Square/Cross/Circle (X/A/B on Xbox) are A/B/C, Start is Start. Unplug it | Every button reacts; the iDrive controller plays again after unplugging |
| B6 | Pause menu (MENU, BACK hold, or the pad's Xbox/PS button): **Save state**, play on, **Load state** | Back where saved |
| B7 | The game with battery saves: save in the game, then **Choose another game** and come back | The game's own save is there |
| B8 | The Master System or Game Gear game | Plays with sound, right colours |
| B9 | The **32X** game | Plays with sound; note the FPS in play. Then **32X recompiler: off**, Choose another game › the 32X game again: note the FPS (expected much lower); set it back **on** |
| B10 | The **Mega-CD** folder game | The BIOS screen, then the game, with CD music; note the FPS. Then the CHD game, if you have one |
| B11 | Settings while a game runs: **Aspect: full**, **Filter: smooth** (each applies at once); **Region: europe**, then Choose another game › a Mega Drive game | FPS about 50 |
| B12 | If a game ran under full speed: **Renderer: fast** | FPS and picture with it |

## C. Stop, start again, update

| # | Do | Look for |
| --- | --- | --- |
| C1 | Hold the push on **picodrive** › **Stop** | Back to iDrive |
| C2 | Start it again | The list focuses the last game played |
| C3 | While a game runs, phone: update to the second package; approve | It stops, checks, installs; start again: states and battery saves still there |

## Logs (before switching off: `/dev/shmem` is RAM)

- Phone: **picodrive** › **Show log** › Share. Wanted lines: `game <name>: …
  fps` for each game, `using bios: …` for the Mega-CD, any `core: … failed`,
  `killed by signal` or `SIGBUS` line.
- Phone: Car › Manage › **Manager log** and **iDrive log**.

## Going back

Uninstall **picodrive** from its page on the phone (or hold › Uninstall on
the car): its games go with it. Or install the last release from GitHub (a
test package with a lower sequence is refused).

## Results

| Step | OK / not OK | Notes |
| --- | --- | --- |
| A0 information shown | | |
| A1-A3 | | |
| B1-B2 import | | |
| B3 names, no BIOS entry | | |
| B4 Mega Drive: sound, FPS | | |
| B5 controls | | |
| B6 states | | |
| B7 battery save | | |
| B8 Master System / Game Gear | | |
| B9 32X: FPS with and without the recompiler | | |
| B10 Mega-CD: folder, CHD, FPS | | |
| B11 settings, region | | |
| B12 renderer | | |
| C1-C3 | | |

With the games used and the pad model.
