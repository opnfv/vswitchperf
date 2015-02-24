# Copyright 2015 Intel Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Default settings. The should be overriden where required.

Part of 'toit' - The OVS Integration Testsuite.
"""

import os

# ############################
# Directories
# ############################

# test directories
ROOT_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '../../'))
TEST_DIR = os.path.join(ROOT_DIR, 'tests')
TRAFFICGEN_DIR = os.path.join(ROOT_DIR, 'trafficgens')
SYSMETRICS_DIR = os.path.join(ROOT_DIR, 'sysmetrics')

# source code directories
RTE_SDK = '~/dpdk'
OVS_DIR = '~/openvswitch'
QEMU_DIR = ''
QEMU_WRAP_DIR = ''

# ############################
# Executables
# ############################

QEMU_BIN = 'qemu-system-x86_64'
QEMU_WRAP_BIN = 'qemu-wrap.py'

# ############################
# Process configuration
# ############################

# shell command to use when running commands through Pexpect
SHELL_CMD = ['/bin/bash', '-c']

# ############################
# DPDK configuration
# ############################

# DPDK target used when builing DPDK
RTE_TARGET = 'x86_64-ivshmem-linuxapp-gcc'

# list of NIC HWIDs which will be bound to the 'igb_uio' driver on
# system init
WHITELIST_NICS = ['05:00.0', '05:00.1']

# list of NIC HWIDs which will be ignored by the 'igb_uio' driver on
# system init
BLACKLIST_NICS = ['0000:09:00.0', '0000:09:00.1', '0000:09:00.2',
                  '0000:09:00.3']

# directory where hugepages will be mounted on system init
HUGEPAGE_DIR = '/dev/hugepages'

# list of tuples of format (path, module_name), which will be inserted
# using 'insmod' on system init

# for OVS modules the path is in reference to the OVS directory.
OVS_MODULES = []

# for DPDK_MODULES the path is in reference to the build directory
DPDK_MODULES = [
    ('kmod', 'igb_uio'),
]

# list of modules that will be inserted using 'modprobe' on system init
SYS_MODULES = ['uio', 'cuse']

# ############################
# Guest configuration
# ############################

# directory which is shared to QEMU guests. Useful for exchanging files
# between host and guest
GUEST_SHARE_DIR = '/tmp/qemu_share'

# location of guest 'qcow2' image
GUEST_IMAGE = '/root/ovdk_guest_release.qcow2'

# username for guest image
GUEST_USERNAME = 'root'

# password for guest image
GUEST_PASSWORD = 'root'

# login username prompt for guest image
GUEST_PROMPT_LOGIN = 'ovdk_guest login:'

# login password prompt for guest image
GUEST_PROMPT_PASSWORD = 'Password:'

# standard prompt for guest image
GUEST_PROMPT = r'\[root@ovdk_guest '

# ############################
# Logging configuration
# ############################

# default log output directory for all logs
LOG_DIR = '/tmp'

# default log for all "small" executables
LOG_FILE_DEFAULT = 'overall.log'

# log file for ovs-vswitchd
LOG_FILE_VSWITCHD = 'vswitchd.log'

# log file for ovs-dpdk
LOG_FILE_OVS = 'ovs.log'

# log file for qemu
LOG_FILE_QEMU = 'qemu.log'

# log file for all traffic generator related commands
LOG_FILE_TRAFFIC_GEN = 'traffic-gen.log'

# log file for all traffic generator related commands
LOG_FILE_SYS_METRICS = 'system-metrics.log'

# log file for all commands executed on host
LOG_FILE_HOST_CMDS = 'host-cmds.log'

# log file for all commands executed on guest(s)
# multiple guests will result in log files with the guest number appended
LOG_FILE_GUEST_CMDS = 'guest-cmds.log'

# enable or disable xunit output
XUNIT = False

# default output directory of xUnit-formatted results
XUNIT_DIR = '/tmp'

# ############################
# Test configuration
# ############################

# verbosity of output to 'stdout'
# NOTE: output to log files is always 'debug' level
VERBOSITY = 'debug'

# dictionary of test-specific parameters. These values are accessible
# from anywhere in the test framework so be careful with naming
# conventions
TEST_PARAMS = {}

# ############################
# Test results
# ############################

# these are the expected throughput rates for the performance tests,
# and should represent the ideal value.
#
# the format of each element should be defined like so:
#
#   module : {
#       test_name : [
#           pkt_size_a : value,
#           pkt_size_b : value,
#           ...
#       ], ...
#   }, ...
PERF_TARGETS = {
    'dpdkport': {
        'LoopbackPerfDPCTL': {
            64: 10850000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'LoopbackPerf': {
            64: 10850000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
    },
    'dpdkrport': {
        'HostOnlyPerf': {
            64: 6200000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'LoopbackPerf': {
            64: 6900000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'VM2VMPerf': {
            64: 2550000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
    },
    'dpdkvhostport': {
        'LoopbackPerf': {
            64: 7260000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'VM2VMPerf': {
            64: 995000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'LoopbackVirtioPerf': {
            64: 995000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'VM2VMVirtioPerf': {
            64: 985000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
    },
}

THROUGHPUT_TARGETS = {
    'dpdkport': {
        'LoopbackThroughput': {
            64: 100,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
    },
    'dpdkrport': {
        'HostOnlyThroughput': {
            64: 100,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'LoopbackThroughput': {
            64: 490000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'VM2VMThroughput': {
            64: 300000,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
    },
    'dpdkvhostport': {
        'LoopbackThroughput': {
            64: 100,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'VM2VMThroughput': {
            64: 100,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'LoopbackVirtioThroughput': {
            64: 100,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
        'VM2VMVirtioThroughput': {
            64: 100,
            128: 101,
            256: 102,
            512: 103,
            1024: 104,
        },
    },
}

# ############################
# Traffic gen configuration
# ############################

# traffic generator to use in tests
TRAFFICGEN = 'Ixia'

# path to 'ixos' install path
TRAFFICGEN_IXIA_ROOT_DIR = '/opt/ixos'

# network address of IXIA chassis
TRAFFICGEN_IXIA_HOST = '10.237.212.7'

TRAFFICGEN_IXIA_CARD = '5'

TRAFFICGEN_IXIA_PORT1 = '13'

TRAFFICGEN_IXIA_PORT2 = '14'

TRAFFICGEN_IXNET_LIB_PATH = '/opt/ixnetwork/lib/IxTclNetwork'

# IxNetwork host IP address
TRAFFICGEN_IXNET_MACHINE = '10.237.213.164'
TRAFFICGEN_IXNET_PORT = '8206'
TRAFFICGEN_IXNET_USER = 'sfinucan'
TRAFFICGEN_IXNET_CHASSIS = '10.237.212.7'

# ############################
# Sysmetrics configuration
# ############################

SYSMETRICS = 'LinuxMetrics'

# the number of seconds between samples when calculating CPU percentage
SYSMETRICS_LINUX_METRICS_CPU_SAMPLES_INTERVAL = 5
