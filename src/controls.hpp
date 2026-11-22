// SPDX-License-Identifier: MPL-2.0
/* The Sega pads on a USB gamepad, the iDrive controller and the desktop
 * keyboard. */
#ifndef NBT_PICODRIVE_CONTROLS_HPP
#define NBT_PICODRIVE_CONTROLS_HPP

#include "nbt/frontend/pad_profiles.hpp"

namespace picodrive {

/* Each pad family has the Mega Drive six-button pad's layout by position: A,
 * B and C on the left, bottom and right face buttons, Y on the top one, X
 * and Z on the shoulders. Actions are RETRO_DEVICE_ID_JOYPAD_* of port 0, as
 * PicoDrive's libretro port reads them (RetroPad Y, B, A are A, B, C; L, X, R
 * are X, Y, Z; Select is Mode). The Master System's buttons 1 and 2 are B and
 * C. */
const nbt::frontend::Profiles& controls();

}  // namespace picodrive

#endif /* NBT_PICODRIVE_CONTROLS_HPP */
