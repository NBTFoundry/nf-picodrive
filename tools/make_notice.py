#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Writes legal/NOTICE.txt: the notices the application's module carries.

Ours (MPL-2.0); PicoDrive's licence (the MAME license) and credits; the code
in it under other terms (FAME/C, CZ80, the SH-2 core, Genesis Plus GX's parts,
the SVP chip, the per-file MIT sources); the libraries it bundles and the
module links (read from their own files); the NBT App SDK (MPL-2.0) and its
third-party notices (NBT_SDK_DIR, default ../sdk); and picolibc, which the NBT
toolchain's runtime links statically (NBT_TOOLCHAIN, default the SDK's
installed release). Run again when the pin, a bundled library or the
toolchain changes.
"""
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ.get("NBT_SDK_DIR", ROOT.parent / "sdk"))
CORE = ROOT / "third_party/picodrive"
CHDR = CORE / "pico/cd/libchdr"
RULE = "\n" + "=" * 72 + "\n\n"

HEADER = """NBTFoundry

NBTFoundry nf-picodrive
Copyright (c) 2026 Fabien Poussin
Original software: MPL-2.0. You may redistribute and modify it under that license.
This software comes WITHOUT ANY WARRANTY, to the extent permitted by law.
Original NBTFoundry artwork: MPL-2.0. Trademark rights are separate.
Source: https://github.com/NBTFoundry/nf-picodrive
When redistributing binaries, include applicable notices and provide the source required by the component licenses.

The application's binary contains PicoDrive and the CPU cores it carries,
whose licences forbid any sale or commercial use: the binary, as a whole,
may be distributed only free of charge and on their terms below. Its source
is the repository above with its submodule (irixxxx/picodrive, with its own
submodules) and the NBT App SDK it names (release/sdk.ref). No game or BIOS
is included.

FAME Motorola 68000 Emulation Library by Oscar Orallo (oscar@m68k.com)
CZ80 Z80 CPU emulator by Stephane Dallongeville
SH-2 CPU core by Juergen Buchmueller
"""


def toolchain() -> Path:
    if os.environ.get("NBT_TOOLCHAIN"):
        return Path(os.environ["NBT_TOOLCHAIN"])
    version = re.search(r"^NBT_TOOLCHAIN_VERSION := (\S+)", (SDK / "module/flags.mk").read_text(), re.M)
    return SDK / "toolchain" / f"nbt-toolchain-{version.group(1)}"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def leading_comment(path: Path, start: str = "/*") -> str:
    """A source file's licence: its first block comment (from `start`),
    without the comment marks."""
    text = read(path)
    at = text.index(start)
    block = text[at + (2 if start == "/*" else 0) : text.index("*/", at)]
    lines = [re.sub(r"^\s*\*+ ?", "", line).rstrip() for line in block.strip("\n").split("\n")]
    return "\n".join(lines).strip("\n") + "\n"


def main():
    runtime = toolchain() / "share/licenses/picolibc"
    if not runtime.is_dir():
        sys.exit(f"no picolibc notices in {runtime}: set NBT_TOOLCHAIN")
    revision = subprocess.run(["git", "-C", str(CORE), "rev-parse", "--short=12", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    sdk_notices = subprocess.run([sys.executable, str(SDK / "tools/third_party_notices.py")],
                                 check=True, capture_output=True, text=True).stdout
    lics = ROOT / "LICENSES"
    parts = [
        HEADER,
        "Head-unit risk and disclaimer\n\n" + read(ROOT / "DISCLAIMER.md").split("\n", 1)[1],
        "MPL-2.0: this application and the NBT App SDK (https://github.com/NBTFoundry/sdk)\n\n"
        + read(lics / "MPL-2.0.txt"),
        f"PicoDrive, the emulator (third_party/picodrive, irixxxx/picodrive at {revision})\n"
        "https://github.com/irixxxx/picodrive; its licence, the MAME license, which its source\n"
        "files name (\"licensed under the terms of MAME license\"), verbatim (COPYING):\n\n"
        + read(CORE / "COPYING").strip("\n") + "\n",
        "PicoDrive's authors and credits, verbatim (AUTHORS)\n\n" + read(CORE / "AUTHORS"),
        "FAME/C, the 68000 CPU core (cpu/fame), a C version of FAME, based on C68K by Stephane\n"
        "Dallongeville; FAME's terms of use, from its documentation (cpu/fame/fame.html)\n\n"
        + read(lics / "LicenseRef-FAME.txt").split("\n\n", 1)[1],
        "CZ80, the Z80 CPU core (cpu/cz80)\n\n" + read(lics / "LicenseRef-CZ80.txt"),
        "The SH-2 CPU core of the 32X (cpu/sh2/mame/sh2.c, from MAME), changed for PicoDrive;\n"
        "its header\n\n" + leading_comment(CORE / "cpu/sh2/mame/sh2.c", "Copyright Juergen"),
        "The YM2612 FM sound chip (pico/sound/ym2612.c, from MAME's fm.c: Jarek Burczynski,\n"
        "Tatsuyuki Satoh) and the SN76496 sound chip (pico/sound/sn76496.c, from MAME), under\n"
        "the MAME license above",
        "Genesis Plus GX's parts (Eke-Eke): the Mega-CD graphics processor, CD controller and\n"
        "drive (pico/cd/gfx.c, cdc.c, cdd.c) and the SPI EEPROM (pico/carthw/eeprom_spi.c);\n"
        "the licence in their headers\n\n" + leading_comment(CORE / "pico/cd/cdc.c"),
        "The SVP chip (pico/carthw/svp), under the BSD-3-Clause licence\n\n"
        + leading_comment(CORE / "pico/carthw/svp/svp.c"),
        "The resampler (pico/sound/resampler.c), under the GNU GPL 2 or later or the MAME license,\n"
        "used here under the MAME license; its SINC filter from the blipper library\n\n"
        + leading_comment(CORE / "pico/sound/resampler.c", "SINC filter generation"),
        "The VGM parser (pico/sound/vgm.c), under the MIT licence\n\n" + read(lics / "MIT.txt"),
        "emu2413, the YM2413 sound chip (pico/sound/emu2413)\n\n" + read(CORE / "pico/sound/emu2413/LICENSE"),
        "libchdr, CHD images (pico/cd/libchdr)\n\n" + read(CHDR / "LICENSE.txt"),
        "LZMA SDK 24.05 (pico/cd/libchdr/deps/lzma-24.05)\n\n" + read(CHDR / "deps/lzma-24.05/LICENSE"),
        "Zstandard 1.5.6, its decoder (pico/cd/libchdr/deps/zstd-1.5.6), under its BSD licence\n\n"
        + read(CHDR / "deps/zstd-1.5.6/LICENSE"),
        "Tremor, the Ogg Vorbis decoder (platform/common/tremor)\n\n"
        + read(CORE / "platform/common/tremor/COPYING"),
        "dr_libs: dr_mp3 (platform/common/dr_libs)\n\n" + read(CORE / "platform/common/dr_libs/LICENSE"),
        "zlib (zlib/)\n\n" + leading_comment(CORE / "zlib/zlib.h"),
        "libretro-common (platform/libretro/libretro-common), under the MIT licence\n\n"
        + leading_comment(CORE / "platform/libretro/libretro-common/file/file_path.c"),
        sdk_notices,
        "picolibc, the C library of the NBT toolchain's runtime, linked statically "
        "(https://github.com/picolibc/picolibc)\n\n"
        + read(runtime / "COPYING.picolibc") + RULE.lstrip("\n")
        + "picolibc's newlib-derived parts\n\n" + read(runtime / "COPYING.NEWLIB"),
    ]
    text = "\n\n" + RULE.join(p.rstrip("\n") + "\n" for p in parts)
    (ROOT / "legal").mkdir(exist_ok=True)
    (ROOT / "legal/NOTICE.txt").write_text(text, encoding="utf-8")
    print(f"legal/NOTICE.txt: {len(parts)} sections")


if __name__ == "__main__":
    main()
