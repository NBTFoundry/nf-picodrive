# SPDX-License-Identifier: MPL-2.0
"""PicoDrive on the libretro host, under Xvfb, with a small Mega Drive
cartridge made here (no game is shipped): the game list (a Mega-CD BIOS file
left out of it), a battery save, save states and the region setting; and the
signed package's declaration.

`test_picodrive.py --write-rom FILE` writes the cartridge (the VM test's)."""

import os
from pathlib import Path
import re
import select
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = Path(os.environ.get("NBT_PICODRIVE_APP", ROOT / "build/nbt-picodrive-host"))
MGR_DIR = Path(os.environ.get("NBT_MGR_DIR", ROOT.parent / "manager"))

SOUTH, VIEW, MENU, DOWN = 1 << 0, 1 << 6, 1 << 7, 1 << 12
XBOX = 1


def cartridge() -> bytes:
    """128 KiB Mega Drive cartridge with battery-backed RAM on odd bytes at
    0x200001-0x203fff: writes 0x42 to its first byte, then loops (68000
    code; interrupts stay masked)."""
    rom = bytearray(0x20000)
    struct.pack_into(">II", rom, 0, 0x00FFFE00, 0x200)  # stack, reset
    for vector in range(2, 64):  # every exception: RTE at 0x210
        struct.pack_into(">I", rom, vector * 4, 0x210)
    rom[0x100:0x110] = b"SEGA MEGA DRIVE "
    rom[0x120:0x150] = b"NBT TEST CARTRIDGE".ljust(48)
    rom[0x150:0x180] = b"NBT TEST CARTRIDGE".ljust(48)
    rom[0x180:0x18E] = b"GM 00000000-00"
    rom[0x190:0x1A0] = b"J".ljust(16)
    struct.pack_into(">II", rom, 0x1A0, 0, len(rom) - 1)  # ROM
    struct.pack_into(">II", rom, 0x1A8, 0xFF0000, 0xFFFFFF)  # work RAM
    rom[0x1B0:0x1B4] = b"RA\xf8\x20"  # backup RAM, odd bytes
    struct.pack_into(">II", rom, 0x1B4, 0x200001, 0x203FFF)
    rom[0x1F0:0x200] = b"JUE".ljust(16)
    code = bytes([0x13, 0xFC, 0x00, 0x42, 0x00, 0x20, 0x00, 0x01,  # MOVE.B #$42,$200001
                  0x60, 0xFE])  # BRA * (forever)
    rom[0x200 : 0x200 + len(code)] = code
    rom[0x210:0x212] = b"\x4e\x73"  # RTE
    checksum = sum(struct.unpack(">%dH" % ((len(rom) - 0x200) // 2), rom[0x200:])) & 0xFFFF
    struct.pack_into(">H", rom, 0x18E, checksum)
    return bytes(rom)


def xvfb():
    r, w = os.pipe()
    proc = subprocess.Popen(
        ["Xvfb", "-displayfd", str(w), "-screen", "0", "1280x480x24", "-nolisten", "tcp"],
        pass_fds=(w,), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.close(w)
    number = b""
    while not number.endswith(b"\n"):
        ready, _, _ = select.select([r], [], [], 10)
        chunk = os.read(r, 1) if ready else b""
        if not chunk:
            break
        number += chunk
    os.close(r)
    return proc, ":" + number.decode().strip()


class App:
    """The emulator, its log (standard error) read by line."""

    def __init__(self, env, pass_fds):
        full = {k: v for k, v in os.environ.items() if not k.startswith("NBT_")}
        full.update(env)
        self.proc = subprocess.Popen([str(APP)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                     env=full, pass_fds=pass_fds)
        self.lines, self.buf = [], b""

    def wait(self, pattern, timeout=20.0):
        regex, deadline = re.compile(pattern), time.monotonic() + timeout
        while True:
            while b"\n" in self.buf:
                raw, self.buf = self.buf.split(b"\n", 1)
                self.lines.append(raw.decode(errors="replace"))
            for i, line in enumerate(self.lines):
                if regex.search(line):
                    del self.lines[: i + 1]
                    return line
            fd = self.proc.stderr.fileno()
            left = deadline - time.monotonic()
            ready, _, _ = select.select([fd], [], [], max(0.0, left)) if left > 0 else ([], [], [])
            chunk = os.read(fd, 4096) if ready else b""
            if not chunk:
                raise AssertionError(f"no line matching {pattern!r}; saw {self.lines[-20:]!r}")
            self.buf += chunk

    def stop(self):
        if self.proc.poll() is None:
            self.proc.send_signal(signal.SIGTERM)
        _, err = self.proc.communicate(timeout=20)
        self.buf += err
        return self.proc.returncode


@unittest.skipUnless(os.access(APP, os.X_OK), f"{APP} not built")
class CheckTest(unittest.TestCase):
    def test_the_health_check_reports_ready_without_a_window(self):
        """As NBT Manager runs it after an install: ready on --ready-fd with
        no display, then stopped with SIGTERM, exit status 0."""
        with tempfile.TemporaryDirectory() as data:
            lease_fd = os.open(Path(data) / "lease", os.O_CREAT | os.O_RDWR, 0o600)
            rfd, wfd = os.pipe()
            env = {k: v for k, v in os.environ.items() if not k.startswith("NBT_")}
            env.pop("DISPLAY", None)
            env.update({"NBT_LAUNCH": "check", "NBT_DATA_DIR": data, "NBT_NO_AUDIO": "1"})
            proc = subprocess.Popen([str(APP), "--ready-fd", str(wfd), "--lease-fd", str(lease_fd)],
                                    pass_fds=(wfd, lease_fd), env=env, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.PIPE)
            os.close(wfd)
            try:
                readable, _, _ = select.select([rfd], [], [], 10.0)
                first = os.read(rfd, 16) if readable else b""
                self.assertTrue(first.startswith(b"R"), f"expected R (ready), got {first!r}")
                proc.send_signal(signal.SIGTERM)
                _, err = proc.communicate(timeout=10)
                self.assertEqual(proc.returncode, 0, err.decode(errors="replace")[-2000:])
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=5)
                os.close(rfd)
                os.close(lease_fd)


@unittest.skipUnless(os.access(APP, os.X_OK), f"{APP} not built")
@unittest.skipUnless(shutil.which("Xvfb"), "Xvfb not installed")
class PlayTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="nbt-picodrive-"))
        self.files, self.data = self.tmp / "files", self.tmp / "data"
        self.files.mkdir(mode=0o700)
        self.data.mkdir(mode=0o700)
        (self.files / "Test Game.md").write_bytes(cartridge())
        # A Mega-CD BIOS beside the games: used by the core, not listed (it
        # would come first).
        (self.files / "bios_CD_U.bin").write_bytes(bytes(0x20000))
        (self.files / "notes.txt").write_bytes(b"not a game")
        self.x, self.display = xvfb()
        self.pad_app, self.pad = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.seq = 0

    def tearDown(self):
        self.pad_app.close()
        self.pad.close()
        self.x.terminate()
        self.x.wait(timeout=5)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def start(self, **settings):
        env = {
            "NBT_LAUNCH": "user", "DISPLAY": self.display, "LIBGL_ALWAYS_SOFTWARE": "1",
            "NBT_NO_AUDIO": "1", "NBT_FILES_DIR": str(self.files), "NBT_DATA_DIR": str(self.data),
            "NBT_BRIDGE_CAPS": "gamepad", "NBT_GAMEPAD_FD": str(self.pad_app.fileno()),
        }
        env.update({"NBT_SETTING_" + k.upper(): v for k, v in settings.items()})
        app = App(env, (self.pad_app.fileno(),))
        self.addCleanup(lambda: app.proc.poll() is None and app.proc.kill())
        app.wait(r"core PicoDrive ")
        return app

    def press(self, buttons=0, hold=0.15):
        self.seq += 1
        self.pad.send(struct.pack("<BBBBIIhhhhHH", 1, 1, 1, XBOX, self.seq, buttons, 0, 0, 0, 0, 0, 0))
        time.sleep(hold)

    def tap(self, buttons):
        self.press(buttons)
        self.press(0)

    def menu(self, downs):
        """The pause menu (View + Menu), `downs` items down, chosen."""
        self.tap(VIEW | MENU)
        for _ in range(downs):
            self.tap(DOWN)
        self.tap(SOUTH)

    def test_a_game_runs_saves_and_restores_a_state(self):
        app = self.start()
        self.press(0)
        self.tap(SOUTH)  # the only game: the BIOS and notes.txt are not listed
        app.wait(r"game Test Game\.md: \d+x\d+, 60\.\d+ fps")
        self.menu(1)  # Save state
        app.wait(r"State saved in slot 1")
        state = self.data / "states" / "Test Game.md.state1"
        self.assertGreater(state.stat().st_size, 1000)
        self.menu(2)  # Load state
        app.wait(r"State of slot 1 loaded")
        self.assertEqual(app.stop(), 0)
        save = (self.data / "saves" / "Test Game.md.srm").read_bytes()
        self.assertIn(0x42, save[:2])
        self.assertEqual((self.data / "last-game").read_bytes(), b"Test Game.md")

    def test_the_region_setting_reaches_the_core(self):
        app = self.start(region="europe")
        self.press(0)
        self.tap(SOUTH)
        app.wait(r"game Test Game\.md: \d+x\d+, 50\.\d+ fps")
        self.assertEqual(app.stop(), 0)


class PackageTest(unittest.TestCase):
    def test_the_package_declares_files_and_its_settings(self):
        verify = MGR_DIR / "build" / "nbt-verify"
        if not (MGR_DIR / "tools/package.py").exists() or not verify.exists():
            self.skipTest("the manager's tools/package.py or build/nbt-verify is missing")
        if not shutil.which("openssl"):
            self.skipTest("openssl is missing")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            key, public = tmp / "app.key", tmp / "app.pub"
            subprocess.run(["openssl", "genrsa", "-out", key, "3072"], check=True, capture_output=True)
            subprocess.run(["openssl", "rsa", "-in", key, "-pubout", "-out", public], check=True,
                           capture_output=True)
            # A stand-in for the module: ARM ET_DYN with the SDK's NBT ABI note.
            binary = tmp / "stand-in.so"
            note = struct.pack("<III", 4, 12, 1) + b"NBT\0" + struct.pack("<III", 1, 1, 1)
            elf = bytearray(52)
            elf[:7] = b"\x7fELF\x01\x01\x01"
            struct.pack_into("<HHI", elf, 16, 3, 40, 1)
            struct.pack_into("<I", elf, 28, 52)
            struct.pack_into("<HHH", elf, 40, 52, 32, 1)
            phdr = struct.pack("<IIIIIIII", 4, 84, 0, 0, len(note), len(note), 4, 4)
            binary.write_bytes(bytes(elf) + phdr + note)
            subprocess.run(["make", "-s", "-C", str(ROOT), "package", f"BUILD_DIR={tmp}",
                            f"PACKAGE_INPUT={binary}", f"APP_KEY={key}", f"NBT_MGR_DIR={MGR_DIR}",
                            "APP_VERSION=0.1.0"], check=True, capture_output=True)
            package = tmp / "picodrive-0.1.0.nbt"
            out = subprocess.run([str(verify), str(package), str(public), "picodrive",
                                  "nbt_6.5_armv7"], check=True, capture_output=True, text=True).stdout
            self.assertIn("app=picodrive\n", out)
            self.assertIn("bridge=1.7\n", out)
            self.assertIn("bridge-uses=show,controller,files,runner\n", out)
            self.assertIn("bridge-optional=status,live-settings,gamepad\n", out)
            raw = package.read_bytes()
            manifest = raw[24 : 24 + int.from_bytes(raw[8:12], "big")].decode("ascii")
            self.assertIn("bridge-files=md,gen,smd,bin,32x,sms,gg,sg,sc,cue,iso,chd,m3u,wav,mp3,ogg"
                          "|1024|16384|folders=m3u,cue\n", manifest)
            for setting in ("aspect|Aspect|4-3|4-3,pixel,full",
                            "region|Region|auto|auto,us,europe,japan,japan_pal",
                            "recompiler|32X recompiler|on|on,off"):
                self.assertIn(f"setting={setting}\n", manifest)
            # What the phone app shows before an install: upstream's version, project
            # and licence, then text.
            self.assertRegex(manifest, r"\nproperty=PicoDrive\|[0-9.]+ \([0-9a-f]{7}\)\n")
            self.assertIn("property=Project|PicoDrive (https://github.com/irixxxx/picodrive)\n",
                          manifest)
            self.assertIn("property=Licence|PicoDrive licence (non-commercial)\n", manifest)
            self.assertIn("\ntext=\n", manifest)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--write-rom"] and len(sys.argv) == 3:
        Path(sys.argv[2]).write_bytes(cartridge())
    else:
        unittest.main()
