#!/bin/bash
#
# Top level scripts to build basic setup for the host
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
#   ...

# function to emit error message before quitting
function die() {
    echo $1
    exit 1
}

# determine this machine's distro-version

distro=`lsb_release -i  | cut -f 2`
release=`lsb_release -r  | cut -f 2`
distro_dir=$distro-$release

if [ -d "$distro_dir" ] && [ -e $distro_dir/build_base_machine.sh ]; then
   $distro_dir/build_base_machine.sh
else
   die "$distro_dir is not yet supported"
fi
