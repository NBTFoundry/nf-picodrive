// SPDX-License-Identifier: MPL-2.0
#include "controls.hpp"

#include <stddef.h>

#include "libretro.h"
#include "nbt/app/video.hpp"

namespace picodrive {

namespace {

using nbt::frontend::Binding;
using nbt::frontend::ControllerProfile;
using nbt::frontend::KeyboardProfile;
using nbt::frontend::PadProfile;
using nbt::frontend::Profiles;

/* The RetroPad buttons PicoDrive reads as the Sega pad's
 * (platform/libretro/libretro.c, retro_pico_map). */
const int kA = RETRO_DEVICE_ID_JOYPAD_Y;
const int kB = RETRO_DEVICE_ID_JOYPAD_B;
const int kC = RETRO_DEVICE_ID_JOYPAD_A;
const int kX = RETRO_DEVICE_ID_JOYPAD_L;
const int kY = RETRO_DEVICE_ID_JOYPAD_X;
const int kZ = RETRO_DEVICE_ID_JOYPAD_R;
const int kMode = RETRO_DEVICE_ID_JOYPAD_SELECT;
const int kStart = RETRO_DEVICE_ID_JOYPAD_START;

/* NBT_GAMEPAD_* name buttons by position, so one layout serves every family:
 * Xbox A, DualShock and DualSense Cross are the bottom button, the Sega B. */
const Binding kPadButtons[] = {{NBT_GAMEPAD_WEST, kA},
                               {NBT_GAMEPAD_SOUTH, kB},
                               {NBT_GAMEPAD_EAST, kC},
                               {NBT_GAMEPAD_LB, kX},
                               {NBT_GAMEPAD_NORTH, kY},
                               {NBT_GAMEPAD_RB, kZ},
                               {NBT_GAMEPAD_VIEW, kMode},
                               {NBT_GAMEPAD_MENU, kStart},
                               {NBT_GAMEPAD_UP, RETRO_DEVICE_ID_JOYPAD_UP},
                               {NBT_GAMEPAD_DOWN, RETRO_DEVICE_ID_JOYPAD_DOWN},
                               {NBT_GAMEPAD_LEFT, RETRO_DEVICE_ID_JOYPAD_LEFT},
                               {NBT_GAMEPAD_RIGHT, RETRO_DEVICE_ID_JOYPAD_RIGHT}};

/* The left stick is the D-pad, the triggers are X and Z too. View and Menu
 * held together (Share/Create and Options), or the Xbox or PS button, open
 * the emulator's menu. */
const PadProfile kPad = {kPadButtons,
                         sizeof(kPadButtons) / sizeof(kPadButtons[0]),
                         RETRO_DEVICE_ID_JOYPAD_UP,
                         RETRO_DEVICE_ID_JOYPAD_DOWN,
                         RETRO_DEVICE_ID_JOYPAD_LEFT,
                         RETRO_DEVICE_ID_JOYPAD_RIGHT,
                         kX,
                         kZ,
                         NBT_GAMEPAD_VIEW | NBT_GAMEPAD_MENU,
                         NBT_GAMEPAD_GUIDE};

/* The iDrive controller: push is B and a BACK tap C, tilts the D-pad, the
 * knob X and Z, MEDIA Mode, OPTION Start; the first two favourite keys A and
 * Y. MENU or a BACK hold opens the menu, a long hold quits. */
const Binding kControllerKeys[] = {{NBT_CONTROLLER_PUSH, kB},
                                   {NBT_CONTROLLER_TILT_UP, RETRO_DEVICE_ID_JOYPAD_UP},
                                   {NBT_CONTROLLER_TILT_DOWN, RETRO_DEVICE_ID_JOYPAD_DOWN},
                                   {NBT_CONTROLLER_TILT_LEFT, RETRO_DEVICE_ID_JOYPAD_LEFT},
                                   {NBT_CONTROLLER_TILT_RIGHT, RETRO_DEVICE_ID_JOYPAD_RIGHT},
                                   {NBT_CONTROLLER_MEDIA, kMode},
                                   {NBT_CONTROLLER_OPTION, kStart},
                                   {NBT_CONTROLLER_FAVOURITE(0), kA},
                                   {NBT_CONTROLLER_FAVOURITE(1), kY}};
const ControllerProfile kController = {
    kControllerKeys,    sizeof(kControllerKeys) / sizeof(kControllerKeys[0]), kX, kZ, 150, kC,
    NBT_CONTROLLER_MENU};

/* The desktop: the arrows; Z, X, C are A, B, C and A, S, D are X, Y, Z (the
 * pad's two rows); Return Start, Right Shift Mode; Escape the menu. */
const Binding kKeys[] = {{'z', kA},
                         {'x', kB},
                         {'c', kC},
                         {'a', kX},
                         {'s', kY},
                         {'d', kZ},
                         {nbt::app::kHostKeyReturn, kStart},
                         {nbt::app::kHostKeyRightShift, kMode},
                         {nbt::app::kHostKeyUp, RETRO_DEVICE_ID_JOYPAD_UP},
                         {nbt::app::kHostKeyDown, RETRO_DEVICE_ID_JOYPAD_DOWN},
                         {nbt::app::kHostKeyLeft, RETRO_DEVICE_ID_JOYPAD_LEFT},
                         {nbt::app::kHostKeyRight, RETRO_DEVICE_ID_JOYPAD_RIGHT}};
const KeyboardProfile kKeyboard = {kKeys, sizeof(kKeys) / sizeof(kKeys[0]),
                                   nbt::app::kHostKeyEscape};

const Profiles kProfiles = {{&kPad, &kPad, &kPad, &kPad}, &kController, &kKeyboard};

}  // namespace

const nbt::frontend::Profiles& controls() {
  return kProfiles;
}

}  // namespace picodrive
