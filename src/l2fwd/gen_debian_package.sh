#!/bin/bash
# Copyright 2015 Futurewei Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# A copy of the license is included with this distribution. If you did not
# recieve a copy you may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

which dpkg-architecture 2>&1 1>/dev/null
if [ $? -ne 0 ]; then
	echo "Can't locate dpkg-architecture"
	echo "try 'sudo apt-get install dpkg-dev"
	exit 1
fi
KERNEL_VERSION=${KERNEL_VERSION-`uname -r`}
PACKAGE_NAME=l2fwd
PACKAGE_ARCH=`dpkg-architecture -qDEB_BUILD_ARCH`
GIT_VERSION=`git ls-remote 2>/dev/null | awk '{print $2}' | sed 's/\// /g' | sort -n -k4| awk '/[0-9]+/{print $(NF-1)"-"$NF}' | tail -n -1`
PACKAGE_VERSION="1.0.$GIT_VERSION-${KERNEL_VERSION}"

MODULE_NAME=l2fwd
PACKAGE_DEPENDS=linux-image-${KERNEL_VERSION}

rm -rf  ${PACKAGE_NAME}-${PACKAGE_VERSION}
mkdir -p ${PACKAGE_NAME}-${PACKAGE_VERSION}/DEBIAN
# put this in with pktgen
mkdir -p ${PACKAGE_NAME}-${PACKAGE_VERSION}/lib/modules/${KERNEL_VERSION}/kernel/net/core/
cat >>${PACKAGE_NAME}-${PACKAGE_VERSION}/DEBIAN/control <<EOF
Package:  ${PACKAGE_NAME}
Version: ${PACKAGE_VERSION}
Section: kernel
Priority: optional
Architecture: ${PACKAGE_ARCH}
Maintainer: eugene.snider@huawei.com
Depends: ${PACKAGE_DEPENDS}
Description: simple l2 fowarding driver
    This package provides the l2fwd driver
EOF
cat >>${PACKAGE_NAME}-${PACKAGE_VERSION}/DEBIAN/preinst <<EOF
#!/bin/bash
rmmod ${MODULE_NAME}
if [ upgrade != "$1" ] || dpkg --compare-versions "$2" lt ${PACKAGE_VERSION}; then
    dpkg-divert --package ${PACKAGE_NAME} --add --rename \
        --divert  /lib/modules/${KERNEL_VERSION}/kernel/net/core/${MODULE_NAME}.ko.dist  /lib/modules/${KERNEL_VERSION}/kernel/net/core/${MODULE_NAME}.ko
fi
EOF
chmod 555 ${PACKAGE_NAME}-${PACKAGE_VERSION}/DEBIAN/preinst
cat >>${PACKAGE_NAME}-${PACKAGE_VERSION}/DEBIAN/postinst <<EOF
#!/bin/bash
/sbin/depmod -a `uname -r`
EOF
chmod 555 ${PACKAGE_NAME}-${PACKAGE_VERSION}/DEBIAN/postinst
cat >>${PACKAGE_NAME}-${PACKAGE_VERSION}/DEBIAN/postrm <<EOF
#!/bin/bash
rmmod ${MODULE_NAME}
if [ upgrade != "$1" ] || dpkg --compare-versions "$2" lt ${PACKAGE_VERSION}; then
    dpkg-divert --package ${PACKAGE_NAME} --remove --rename \
        --divert  /lib/modules/${KERNEL_VERSION}/kernel/net/core/${MODULE_NAME}.ko.dist  /lib/modules/${KERNEL_VERSION}/kernel/net/core/${MODULE_NAME}.ko
fi
EOF
chmod 555 ${PACKAGE_NAME}-${PACKAGE_VERSION}/DEBIAN/postrm
cp -p ${MODULE_NAME}.ko ${PACKAGE_NAME}-${PACKAGE_VERSION}/lib/modules/${KERNEL_VERSION}/kernel/net/core/${MODULE_NAME}.ko
sudo dpkg-deb --build ${PACKAGE_NAME}-${PACKAGE_VERSION}
sudo rm -rf ${PACKAGE_NAME}-${PACKAGE_VERSION}
