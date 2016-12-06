#!/bin/bash
#
# Build a base machine for RHEL 7.2
#
# Copyright 2016 OPNFV, Intel Corporation & Red Hat Inc.
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
#   Martin Klozik, Intel Corporation.
#   Abdul Halim, Intel Corporation.
#   Christian Trautman, Red Hat Inc.

# Make and Compilers
pkglist=(\
 automake\
 fuse-devel\
 gcc\
 gcc-c++\
 glib2-devel\
 glibc\
 kernel-devel\
 openssl-devel\
 pixman-devel\
 sysstat\
)

# Tools
pkglist=(
 "${pkglist[@]}"\
 git\
 libtool\
 libpcap-devel\
 libnet\
 net-tools\
 openssl\
 openssl-devel\
 pciutils\
 socat\
 tk-devel\
 wget\
 numactl\
 numactl-devel\
)

# python tools for proper QEMU, DPDK, and OVS make
pkglist=(
 "${pkglist[@]}"\
 python-six\
)

# Iterate installing each package. If packages fail to install, record those
# packages and exit with an error message on completion. Customer may need to
# add repo locations and subscription levels.
failedinstall=()
for pkg in ${pkglist[*]}; do
    echo "Installing ${pkg}"
    yum -y install ${pkg} || failedinstall=("${failedinstall[*]}" "$pkg")
done

if [ "${#failedinstall[*]}" -gt 0 ]; then
    echo "The following packages failed to install. Please add appropriate repo\
 locations and/or subscription levels. Then run the build script again."
    for fail in ${failedinstall[*]}; do
        echo $fail
    done
    exit 1
fi

# install SCL for python33 by adding a repo to find its location to install it
cat <<'EOT' >> /etc/yum.repos.d/python33.repo
[rhscl-python33-el7]
name=Copr repo for python33-el7 owned by rhscl
baseurl=https://copr-be.cloud.fedoraproject.org/results/rhscl/python33-el7/epel-7-$basearch/
type=rpm-md
skip_if_unavailable=True
gpgcheck=1
gpgkey=https://copr-be.cloud.fedoraproject.org/results/rhscl/python33-el7/pubkey.gpg
repo_gpgcheck=0
enabled=1
enabled_metadata=1
EOT

# install python33 packages and git-review tool
yum -y install $(echo "
python33
python33-python-tkinter
" | grep -v ^#)

# cleanup python 33 repo file
rm -f /etc/yum.repos.d/python33.repo

# Create hugepage dirs
mkdir -p /dev/hugepages
