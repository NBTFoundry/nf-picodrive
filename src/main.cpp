// SPDX-License-Identifier: MPL-2.0
/* PicoDrive on NBT Manager: the upstream libretro core, linked statically, on
 * the SDK's libretro host (game list, saves, states, pause menu, discs,
 * controls). */
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <strings.h>

#include "controls.hpp"
#include "nbt/retro/host.hpp"

namespace {

/* The games offered: cartridges (Mega Drive, 32X, Master System, Game Gear,
 * SG-1000, SC-3000) and discs (Mega-CD: a CHD or ISO image, or a cue sheet
 * or playlist, usually in a game folder with its tracks). The same list as
 * release/package.args's files policy, without the audio tracks. */
const char* const kExtensions[] = {"md", "gen", "smd", "bin", "32x", "sms", "gg",
                                   "sg", "sc",  "cue", "iso", "chd", "m3u", NULL};
/* A game folder (a disc's cue sheet and tracks, a playlist and its discs,
 * imported whole: `|folders=` in release/package.args) opens at its playlist,
 * else its cue sheet, else its image. */
const char* const kFolderMains[] = {"m3u", "cue", "chd", "iso", NULL};

/* The Mega-CD BIOS files PicoDrive looks for in its system folder, the files
 * folder here (platform/libretro/libretro.c, biosfiles_*): used, not listed. */
const char* const kBiosNames[] = {"us_scd2_9306",   "SegaCDBIOS9303", "us_scd1_9210", "bios_CD_U",
                                  "eu_mcd2_9306",   "eu_mcd2_9303",   "eu_mcd1_9210", "bios_CD_E",
                                  "jp_mcd2_921222", "jp_mcd1_9112",   "jp_mcd1_9111", "bios_CD_J"};

/* The game list names a game by its file or folder name without the
 * extension, and leaves the BIOS files out. */
bool describe_game(const char* name, char* label, size_t size) {
  const char* dot = strrchr(name, '.');
  const size_t stem = dot && dot != name ? static_cast<size_t>(dot - name) : strlen(name);
  for (size_t i = 0; i < sizeof(kBiosNames) / sizeof(kBiosNames[0]); ++i) {
    if (strlen(kBiosNames[i]) == stem && strncasecmp(name, kBiosNames[i], stem) == 0) return false;
  }
  snprintf(label, size, "%.*s", static_cast<int>(stem), name);
  return true;
}

/* Manager settings feeding the core's variables
 * (platform/libretro/libretro_core_options.h): setting value, core value. */
const char* const kRegion[] = {"auto",  "Auto",       "us",        "US",        "europe", "Europe",
                               "japan", "Japan NTSC", "japan_pal", "Japan PAL", NULL};
const char* const kRenderer[] = {"accurate", "accurate", "good", "good", "fast", "fast", NULL};
const char* const kSpriteLimit[] = {"on", "disabled", "off", "enabled", NULL};
const char* const kRecompiler[] = {"on", "enabled", "off", "disabled", NULL};
const char* const kOverclock[] = {"off",  "disabled", "25",    "+25%", "50",
                                  "+50%", "100",      "+100%", NULL};
const nbt::retro::VariableMap kVariables[] = {{"region", "picodrive_region", kRegion},
                                              {"renderer", "picodrive_renderer", kRenderer},
                                              {"sprite_limit", "picodrive_sprlim", kSpriteLimit},
                                              {"recompiler", "picodrive_drc", kRecompiler},
                                              {"overclock", "picodrive_overclk68k", kOverclock}};

}  // namespace

int main(int argc, char** argv) {
  const nbt::retro::HostConfig config = {"picodrive",
                                         "PicoDrive",
                                         "Mega Drive",
                                         kExtensions,
                                         &picodrive::controls(),
                                         kVariables,
                                         sizeof(kVariables) / sizeof(kVariables[0]),
                                         4.0f / 3.0f,
                                         0 /* the core reads its games itself */,
                                         true /* Mega-CD BIOS files with the games */,
                                         kFolderMains,
                                         &describe_game};
  return nbt::retro::run(argc, argv, config);
}
