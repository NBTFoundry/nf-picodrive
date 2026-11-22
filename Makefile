# SPDX-License-Identifier: MPL-2.0
SHELL := /bin/bash

BUILD_DIR ?= build
OBJ_DIR := $(BUILD_DIR)/obj

APP_VERSION ?= 0.0.1
APP_SEQ ?= 1
APP_KEY ?=
# Sibling NBTFoundry checkouts; override as needed. The SDK is built into
# $(BUILD_DIR)/sdk; the manager is only needed for packaging.
NBT_SDK_DIR ?= ../sdk
NBT_MGR_DIR ?= ../manager
# The QNX SDP builds only the SDK's nbt-runner, for the VM test. The
# application is a module, built with the NBT toolchain; on the car, NBT
# Manager's own nbt-runner loads it (bridge 1.7, runner).
QNX_ENV ?=
QNX_SCREEN_LIBDIR ?=

CC ?= gcc
CXX ?= g++

NBT_SDK_BUILD_DIR := $(abspath $(BUILD_DIR))/sdk
include $(NBT_SDK_DIR)/nbt-sdk.mk
# Each kind of object rebuilds when its compile command changes (the SDK's
# nbt-stamp.mk; the stamps are written at the end of this file).
stamp = $(OBJ_DIR)/$(1).stamp
ifeq ($(value nbt_stamp),)
$(error $(NBT_SDK_ROOT) has no nbt-stamp.mk: update that SDK checkout)
endif

# --- PicoDrive: built by upstream's own libretro Makefiles, unmodified ---
# Upstream writes its objects next to its sources, so each build kind gets a
# copy of the submodule (its bundled libraries too) under
# $(BUILD_DIR)/core/<kind>/ (objects kept between runs), where upstream's make
# builds them and tools/core.mk archives them (upstream's object list) into a
# static library. Flags reach it through the environment: upstream appends to
# CFLAGS.
CORE_SRC := third_party/picodrive
CORE_REV := $(shell git -C $(CORE_SRC) rev-parse --short=8 HEAD 2>/dev/null)
CORE_LIB_NAME := libpicodrive.a
# The C CPU cores and renderers (FAME/C, CZ80: no Cyclone, DrZ80 or ARM
# assembly, which rely on unaligned access and need a generator), the SH2
# recompiler for the 32X (its ARM back end on the head unit), the bundled zlib
# and Tremor (no system library), CHD images (libchdr).
CORE_MAKE_ARGS := platform=unix fpic= NO_ARM_ASM=1 PLATFORM_ZLIB=1 PLATFORM_TREMOR=1 use_libchdr=1 \
	GIT_REVISION=-$(CORE_REV)
core_dir = $(BUILD_DIR)/core/$(1)
# Changes upstream's sources need on the head unit, applied to the copy
# (none yet). A patched file keeps the time of the newer of its source and its
# patch, so applying the patches again on every build recompiles nothing.
CORE_PATCHES := $(sort $(wildcard $(abspath patches)/*.patch))
CORE_PATCHES_SUM := $(if $(CORE_PATCHES),$(firstword $(shell cat $(CORE_PATCHES) | sha256sum)))
core_lib = $(abspath $(call core_dir,$(1)))/$(CORE_LIB_NAME)

# Our command line's CFLAGS (make passes them on in MAKEFLAGS) would replace
# upstream's own instead of adding to them: they stay ours.
CORE_MAKEFLAGS = MAKEFLAGS='$(filter-out CFLAGS=% CXXFLAGS=%,$(MAKEFLAGS))'
# $(call core_build,kind): upstream's make with CORE_ENV_<kind> in its
# environment and CORE_ARGS_<kind> as arguments. When those or the toolchain
# (the kind's core stamp) changed since the copy's objects were built, they go
# first: upstream's make would keep them.
define core_build
	@mkdir -p $(call core_dir,$(1))/src
	@if ! cmp -s $(call stamp,core-$(1)) $(call core_dir,$(1))/.stamp \
		|| test $(call stamp,core-$(1)) -nt $(call core_dir,$(1))/.stamp; then \
		test ! -f $(call core_dir,$(1))/.stamp || echo "core $(1): build stamp changed, rebuilding it"; \
		find $(call core_dir,$(1)) \( -name '*.o' -o -name '*.d' \) -delete; \
		cp $(call stamp,core-$(1)) $(call core_dir,$(1))/.stamp; fi
	tar -C $(CORE_SRC) --exclude=.git --exclude='*.o' --exclude='*.d' -cf - . \
		| tar -C $(call core_dir,$(1))/src -xf -
	for p in $(CORE_PATCHES); do patch -s -p1 -d $(call core_dir,$(1))/src < $$p || exit 1; \
		for f in $$(sed -n 's#^+++ b/##p' $$p); do \
			if test $$p -nt $(CORE_SRC)/$$f; then r=$$p; else r=$(CORE_SRC)/$$f; fi; \
			touch -r $$r $(call core_dir,$(1))/src/$$f; done; done
	cd $(call core_dir,$(1))/src && $(CORE_ENV_$(1)) $(CORE_MAKEFLAGS) $(MAKE) --no-print-directory \
		-f Makefile.libretro -f $(abspath tools/core.mk) $(CORE_MAKE_ARGS) \
		NBT_CORE_LIB=$(call core_lib,$(1)) $(CORE_ARGS_$(1)) nbt-core
endef

.PHONY: FORCE
FORCE:

# Upstream's own warnings are its business: -w after its flags; no link-time
# optimisation (its objects go into an archive). Its rules have no header
# dependencies: the core stamps hold the pin (GIT_REVISION) and the patches,
# so a copy whose sources may have changed is built again whole.
CORE_FLAGS_AFTER := -w -fno-lto
CORE_ENV_host :=
CORE_ARGS_host := NBT_CORE_CFLAGS="$(CORE_FLAGS_AFTER)"
$(call core_lib,host): FORCE
	$(call core_build,host)

# The sanitizer builds (test-asan, test-align): CORE_SANITIZE adds the
# alignment sanitizer for test-align.
CORE_SANITIZE ?=
CORE_ENV_asan = CFLAGS="-g -fsanitize=address -fno-omit-frame-pointer $(CORE_SANITIZE)"
CORE_ARGS_asan := NBT_CORE_CFLAGS="$(CORE_FLAGS_AFTER)"
$(call core_lib,asan): FORCE
	$(call core_build,asan)

# The module: the NBT toolchain's flags and runtime (sdk/module/flags.mk).
# clang names the machine armv7a: ARCH=arm is upstream's name for it (the SH2
# recompiler's ARM back end, the C sound mixer).
CORE_ENV_mod = CFLAGS="$(NBT_MOD_CFLAGS)"
CORE_ARGS_mod = CC="$(NBT_MOD_CC)" AR="$(NBT_MOD_AR)" ARCH=arm NBT_CORE_CFLAGS="$(CORE_FLAGS_AFTER)"
$(call core_lib,mod): FORCE | nbt-sdk-mod
	$(call core_build,mod)

# --- Ours: the application on the SDK's libretro host ---
APP_SRC := src/controls.cpp src/main.cpp
APP_INC := $(NBT_SDK_INC) $(NBT_SDK_LIBRETRO_INC) -Isrc
APP_CXXFLAGS := -std=c++11 -O2 -Wall -Wextra -Werror -fno-exceptions -fno-rtti $(CXXFLAGS)
app_objs = $(patsubst %.cpp,$(OBJ_DIR)/$(1)/%.o,$(APP_SRC))

HOST_APP := $(BUILD_DIR)/nbt-picodrive-host
ASAN_APP := $(BUILD_DIR)/nbt-picodrive-asan
ASAN_FLAGS := -O1 -g -fsanitize=address -fno-omit-frame-pointer
CORE_HOST_LDLIBS := -lm -lpthread

.PHONY: all host test test-asan test-align check-static-init format module vm-test package \
	package-args notice clean

all: host test

# --- Host (Linux, X11) ---
$(OBJ_DIR)/host/src/%.o: src/%.cpp $(call stamp,host)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) -MMD -MP -c $< -o $@

# The core after the SDK: the libretro host calls it (GNU ld takes from an
# archive only what is already wanted).
$(HOST_APP): $(call app_objs,host) $(NBT_SDK_FRONT_HOST_LIBS) $(call core_lib,host)
	$(CXX) $(call app_objs,host) $(NBT_SDK_FRONT_HOST_LIBS) $(call core_lib,host) $(LDFLAGS) \
		$(NBT_SDK_HOST_LDLIBS) $(CORE_HOST_LDLIBS) -o $@

host: $(HOST_APP) $(BUILD_DIR)/controls-test

# --- Sanitizer build: the core under AddressSanitizer, ours under UBSan too ---
$(OBJ_DIR)/asan/src/%.o: src/%.cpp $(call stamp,asan)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined -MMD -MP -c $< -o $@

$(ASAN_APP): $(call app_objs,asan) $(NBT_SDK_FRONT_ASAN_LIBS) $(call core_lib,asan)
	$(CXX) $(ASAN_FLAGS) -fsanitize=undefined $(CORE_SANITIZE) $(call app_objs,asan) \
		$(NBT_SDK_FRONT_ASAN_LIBS) $(call core_lib,asan) $(LDFLAGS) $(NBT_SDK_HOST_LDLIBS) \
		$(CORE_HOST_LDLIBS) -o $@

# --- Tests ---
$(OBJ_DIR)/host/tests/%.o: tests/%.cpp $(call stamp,host)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) -MMD -MP -c $< -o $@

$(BUILD_DIR)/controls-test: $(OBJ_DIR)/host/tests/controls_test.o $(OBJ_DIR)/host/src/controls.o \
		$(NBT_SDK_FRONT_HOST_LIBS)
	$(CXX) $^ $(LDFLAGS) $(NBT_SDK_HOST_LDLIBS) -o $@

$(BUILD_DIR)/controls-asan: tests/controls_test.cpp src/controls.cpp src/controls.hpp \
		$(NBT_SDK_FRONT_ASAN_LIBS)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined tests/controls_test.cpp \
		src/controls.cpp $(NBT_SDK_FRONT_ASAN_LIBS) $(LDFLAGS) $(NBT_SDK_HOST_LDLIBS) -o $@

test: host
	python3 tools/package_version.py --check release/package.args
	$(BUILD_DIR)/controls-test
	NBT_PICODRIVE_APP=$(abspath $(HOST_APP)) NBT_MGR_DIR=$(abspath $(NBT_MGR_DIR)) \
		python3 -m unittest discover -s tests -v

test-asan: $(ASAN_APP) $(BUILD_DIR)/controls-asan
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
		$(BUILD_DIR)/controls-asan
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
		NBT_PICODRIVE_APP=$(abspath $(ASAN_APP)) NBT_MGR_DIR=$(abspath $(NBT_MGR_DIR)) \
		python3 -m unittest discover -s tests -v -k Play

# The core under the alignment sanitizer too, played by the tests on the
# desktop: the head unit stops a misaligned access with SIGBUS, which x86
# never shows.
test-align:
	$(MAKE) BUILD_DIR=$(BUILD_DIR)/align test-asan \
		CORE_SANITIZE="-fsanitize=alignment -fno-sanitize-recover=alignment"

# Our objects only: the core's are upstream's business.
check-static-init: $(call app_objs,host)
	@set -e; \
	for obj in $^; do \
		ctors="$$(readelf -S "$$obj" | awk '/\.init_array|\.ctors/ {print $$2}')"; \
		if test -n "$$ctors"; then \
			echo "ERROR: static constructor section in $$obj: $$ctors"; exit 1; \
		fi; \
	done; \
	echo "OK: no .init_array/.ctors in our objects"
	+@$(NBT_SDK_MAKE) check-static-init

format:
	clang-format -i src/*.cpp src/*.hpp tests/*.cpp

# --- The module: built without the QNX SDP, loaded by nbt-runner
# (sdk/module). PicoDrive and the code it bundles are not GPL or LGPL (the
# licence gate checks), so it runs in the runner's process. ---
MOD_APP := $(BUILD_DIR)/nbt-picodrive.so
# Every licence of the linked objects (legal/README.md): PicoDrive's own
# (non-commercial, MAME-style), FAME/C's, CZ80's, MAME's (the SH2 core, the
# FM and PSG chips), Genesis Plus GX's (the Mega-CD graphics and drive), the
# libraries it bundles (libchdr, zstd, Tremor: BSD-3-Clause; libretro-common,
# emu2413: MIT; dr_libs: MIT-0; zlib) and ours.
MOD_APP_LICENSE := LicenseRef-PicoDrive AND LicenseRef-FAME AND LicenseRef-CZ80 AND LicenseRef-MAME-SH2 \
	AND LicenseRef-GenesisPlusGX AND BSD-3-Clause AND MIT AND MIT-0 AND Zlib AND MPL-2.0
MOD_APP_CXXFLAGS := $(NBT_MOD_CXXFLAGS) -O2 -std=c++11 -Wall -Wextra -Werror -fno-exceptions -fno-rtti \
	$(APP_INC)

$(OBJ_DIR)/mod/src/%.o: src/%.cpp $(call stamp,mod) | nbt-sdk-mod
	@mkdir -p $(dir $@)
	$(NBT_MOD_CXX) $(MOD_APP_CXXFLAGS) -MMD -MP -c $< -o $@

MOD_OBJ := $(call app_objs,mod) $(call core_lib,mod)

$(MOD_APP): $(MOD_OBJ) $(NBT_SDK_MOD_DEPS)
	$(call nbt_module_link,$@,$(MOD_OBJ),$(MOD_APP_LICENSE))
	@size=$$(stat -c %s $@); echo "$@: $$((size / 1024)) KiB ($$size bytes; a package holds 64 MiB)"

module: $(MOD_APP)

# --- The module in QNX 6.5 SP1 under QEMU (the SDK's tools/qnx65-vm; no GPU,
# no sound: both faked): a health check, then the cartridge of
# tests/test_picodrive.py played, which must draw frames and stop cleanly. ---
VM_GAME := $(BUILD_DIR)/vm/test.md
VM_PLAY := NBT_LAUNCH=user NBT_SURFACE=5 NBT_RUNNER_FAKE_GL=1 NBT_RUNNER_FAKE_AUDIO=1 \
	NBT_DATA_DIR=/dev/shmem NBT_FILES_DIR=/proc/boot

$(VM_GAME): tests/test_picodrive.py
	@mkdir -p $(dir $@)
	python3 tests/test_picodrive.py --write-rom $@

vm-test: $(NBT_SDK_RUNNER) $(MOD_APP) $(VM_GAME)
	QEMU_RUN_SECS=240 $(NBT_SDK_ROOT)/tools/qnx65-vm/run.sh \
		-c "NBT_LAUNCH=check NBT_DATA_DIR=/dev/shmem nbt-runner --nbt-payload /proc/boot/$(notdir $(MOD_APP)) &" \
		-c "waitfor /none 10" -c "slay -s TERM nbt-runner" -c "waitfor /none 3" \
		-c "$(VM_PLAY) nbt-runner --nbt-payload /proc/boot/$(notdir $(MOD_APP)) --game test.md &" \
		-c "waitfor /none 60" -c "slay -s TERM nbt-runner" -c "waitfor /none 3" \
		-x 'stage: check' -x 'game test\.md: ' -x 'fake-gl: closed: [1-9][0-9]* frames' \
		$^

# release/package.args's PicoDrive version (tools/package_version.py): again
# when the pin moves; `make test` fails until then.
package-args:
	python3 tools/package_version.py release/package.args

# --- The signed package (release/package.args describes it) ---
# The module: NBT Manager's nbt-runner runs it (bridge 1.7, runner).
PACKAGE_INPUT ?= $(MOD_APP)
PACKAGE := $(BUILD_DIR)/picodrive-$(APP_VERSION).nbt

package: $(PACKAGE_INPUT)
	@test -f "$(APP_KEY)" || { echo "APP_KEY must name the RSA signing key"; exit 1; }
	@test -f "$(NBT_MGR_DIR)/tools/package.py" || { echo "NBT_MGR_DIR=$(NBT_MGR_DIR) has no tools/package.py"; exit 1; }
	rm -f $(PACKAGE)
	python3 $(NBT_MGR_DIR)/tools/package.py @release/package.args \
		--version "$(APP_VERSION)" \
		--sequence "$(APP_SEQ)" \
		--key "$(APP_KEY)" \
		--output $(PACKAGE) \
		$(PACKAGE_INPUT)

# legal/NOTICE.txt (tools/make_notice.py): again when the pin, a bundled
# library, the SDK or the toolchain changes.
notice:
	NBT_SDK_DIR=$(NBT_SDK_ROOT) NBT_TOOLCHAIN=$(NBT_TOOLCHAIN) python3 tools/make_notice.py

clean:
	rm -rf $(BUILD_DIR)

DEPS := $(shell find $(OBJ_DIR) -name '*.d' 2>/dev/null)
-include $(DEPS)

$(call nbt_stamp,$(call stamp,host),$(CXX) $(APP_INC) $(APP_CXXFLAGS),$(CXX))
$(call nbt_stamp,$(call stamp,asan),$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined,$(CXX))
$(call nbt_stamp,$(call stamp,mod),$(NBT_MOD_CXX) $(MOD_APP_CXXFLAGS),,$(NBT_TOOLCHAIN)/VERSION)
$(call nbt_stamp,$(call stamp,core-host),$(CORE_MAKE_ARGS) $(CORE_ENV_host) $(CORE_ARGS_host) \
	$(CORE_PATCHES_SUM),$(CC))
$(call nbt_stamp,$(call stamp,core-asan),$(CORE_MAKE_ARGS) $(CORE_ENV_asan) $(CORE_ARGS_asan) \
	$(CORE_PATCHES_SUM),$(CC))
$(call nbt_stamp,$(call stamp,core-mod),$(CORE_MAKE_ARGS) $(CORE_ENV_mod) $(CORE_ARGS_mod) $(CORE_PATCHES_SUM),, \
	$(NBT_TOOLCHAIN)/VERSION)
