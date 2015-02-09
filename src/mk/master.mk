# Master makefile definitions for project opnfv vswitchperf
#
# Copyright (C) 2015 OPNFV
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without warranty of any kind.
#
# Contributors:
#   Aihua Li, Huawei Technologies.

# user has the full control to decide where to put the build by
# specifying INSTALL_DIR from the make input

# try to read it in from environment
INSTALL_DIR ?= $(shell echo $$INSTALL_DIR)

# if it is stillnot set, then set it to default
ifeq ($(INSTALL_DIR),)
INSTALL_DIR = /opt/opnfv
endif

# for debugging Makefile
# Make V as a synonum for VERBOSE
ifdef V
VERBOSE = $(V)
endif

VERBOSE ?= 0

ifeq ($(VERBOSE),0)
    AT = @
else
    BASH_X = -x
endif

.DEFAULT_GOAL := all

.PHONY: all clean clobber
