<!-- SPDX-License-Identifier: MPL-2.0 -->
# License notices

The repository's original work is licensed as described in its root README and LICENSE. Third-party components retain their own licenses and copyright notices, collected in [NOTICE.txt](NOTICE.txt) (written by `make notice`, `tools/make_notice.py`). Original NBTFoundry artwork is MPL-2.0.

| Component | Licence | Text |
| --- | --- | --- |
| This application (`src/`, `tests/`, `tools/`, build files) | MPL-2.0 | [LICENSE](../LICENSE) |
| PicoDrive (`third_party/picodrive`), with MAME's YM2612 and SN76496 chips | PicoDrive's licence: the MAME license (non-commercial) | [LicenseRef-PicoDrive](../LICENSES/LicenseRef-PicoDrive.txt) |
| FAME/C, the 68000 core | FAME's terms (nothing charged; credit text required) | [LicenseRef-FAME](../LICENSES/LicenseRef-FAME.txt) |
| CZ80, the Z80 core | its terms (non-commercial; credit) | [LicenseRef-CZ80](../LICENSES/LicenseRef-CZ80.txt) |
| The SH-2 core (32X) | its author's terms (non-commercial freeware; credit) | [LicenseRef-MAME-SH2](../LICENSES/LicenseRef-MAME-SH2.txt) |
| Genesis Plus GX's Mega-CD and EEPROM parts | Genesis Plus GX's licence (non-commercial) | [LicenseRef-GenesisPlusGX](../LICENSES/LicenseRef-GenesisPlusGX.txt) |
| The SVP chip, libchdr, Zstandard, Tremor | BSD-3-Clause | [BSD-3-Clause](../LICENSES/BSD-3-Clause.txt); holders in NOTICE.txt |
| The resampler | GPL-2.0-or-later or the MAME license: used under the MAME license | [LicenseRef-PicoDrive](../LICENSES/LicenseRef-PicoDrive.txt) |
| emu2413, the VGM parser, the blipper filter, libretro-common | MIT | [MIT](../LICENSES/MIT.txt); NOTICE.txt |
| dr_libs (dr_mp3) | Unlicense or MIT-0 | [MIT-0](../LICENSES/MIT-0.txt) |
| zlib | Zlib | [Zlib](../LICENSES/Zlib.txt); NOTICE.txt |
| LZMA SDK | public domain | NOTICE.txt |
| NBT App SDK and its third-party parts | MPL-2.0; MIT, public domain | [MPL-2.0](../LICENSES/MPL-2.0.txt); NOTICE.txt |
| picolibc (the NBT toolchain's C library, linked in) | BSD-style | NOTICE.txt |
| compiler-rt, libc++, libc++abi, libunwind (linked in) | Apache-2.0 WITH LLVM-exception | no attribution owed in binaries |

Not in the module: PicoDrive's Cyclone and DrZ80 assembly cores, its ARM assembly renderers and its own front end (`platform/libpicofe`): the build uses the C cores (`NO_ARM_ASM=1`) and the libretro port.

The notices are a snapshot of the current dependencies. Update them when changing the pin, a bundled dependency or the toolchain. PicoDrive's licence and its cores' terms forbid any sale or commercial use, and ask that the source of a modified build be published: the package is distributed free of charge only, with this repository, its submodule and the SDK commit it names (`release/sdk.ref`) as its source.

No game or BIOS is included or distributed.

See [DISCLAIMER.md](../DISCLAIMER.md) for head-unit risks and warranty and liability terms.
