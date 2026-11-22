# SPDX-License-Identifier: MPL-2.0
# Read after PicoDrive's own libretro Makefiles
# (make -f Makefile.libretro -f core.mk nbt-core, in a copy of upstream's
# tree): upstream's object list (OBJS: the core, its CPU cores, libretro.c,
# libretro-common and the libraries it bundles), built by upstream's rules and
# flags, archived into NBT_CORE_LIB for a static link.
#
# NBT_CORE_CFLAGS comes after upstream's own flags (its -flto, for one), where
# the environment's CFLAGS comes before.
CFLAGS += $(NBT_CORE_CFLAGS)

# The list is long: the archiver reads it from a file. Made again only when
# an object or a makefile (the list, the flags) changed, so what links the
# library does not rebuild every time.
.PHONY: nbt-core
nbt-core: $(NBT_CORE_LIB)
$(NBT_CORE_LIB): $(OBJS) $(MAKEFILE_LIST)
	$(file >$@.in,$(OBJS))
	rm -f $@
	$(AR) rcs $@ @$@.in
	rm -f $@.in
