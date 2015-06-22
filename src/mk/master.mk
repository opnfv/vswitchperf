# Master makefile definitions for project opnfv vswitchperf
#

# Copyright 2015 OPNFV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Contributors:
#   Aihua Li, Huawei Technologies.

# user has the full control to decide where to put the build by
# specifying INSTALL_DIR from the make input

# try to read it in from environment
INSTALL_DIR ?= $(shell echo $$INSTALL_DIR)

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

.PHONY: all clean cleanse clobber
