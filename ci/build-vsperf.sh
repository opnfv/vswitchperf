#!/bin/bash
#
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

# VSPERF nightly build execution script

# Usage:
#       build-vsperf.sh job_type
#   where job_type is one of "verify", "merge", "daily"

#
# configuration
#

EXIT=0
VSPERF_BIN='./vsperf'
LOG_FILE_USER='/tmp/vsperf_user.log'
LOG_FILE_VANILLA='/tmp/vsperf_vanilla.log'
LOG_FILE_PREFIX="/tmp/vsperf_build_"
OPNFV_POD="intel-pod3"

# CI job specific configuration
# VERIFY - run basic set of TCs with default settings
TESTCASES_VERIFY="phy2phy_tput pvp_tput"
TESTPARAM_VERIFY=""
# MERGE - run selected TCs with default settings
TESTCASES_MERGE="phy2phy_tput back2back phy2phy_cont pvp_tput pvvp_tput"
TESTPARAM_MERGE=""
# DAILY - run selected TCs for defined packet sizes
TESTCASES_DAILY='phy2phy_tput back2back phy2phy_tput_mod_vlan phy2phy_scalability pvp_tput pvp_back2back pvvp_tput pvvp_back2back'
TESTPARAM_DAILY='--test-params pkt_sizes=64,128,512,1024,1518'
# check if user config file exists if not then we will use default settings
[ -f $HOME/vsperf.conf ] && CONF_FILE="--conf-file ${HOME}/vsperf.conf" || CONF_FILE=""

#
# functions
#

# check and print testcase execution status
# parameters:
#   $1 - directory with results
function print_results() {
    for i in $TESTCASES ; do
        if [[ $i == *"pvp"* ]]; then
            DEPLOYMENT="pvp"
        elif [[ $i == *"pvvp"* ]]; then
            DEPLOYMENT="pvvp"
        else
            DEPLOYMENT="p2p"
        fi
        RES_FILE="result_${i}_${DEPLOYMENT}.csv"

        if [ -e "${1}/${RES_FILE}" ]; then
            printf "    %-70s %-6s\n" $RES_FILE "OK"
        else
            printf "    %-70s %-6s\n" $RES_FILE "FAILED"
            EXIT=1
        fi
    done
}

# execute tests and display results
# parameters:
#   $1 - vswitch and vnf combination, one of OVS_vanilla, OVS_with_DPDK_and_vHost_Cuse, OVS_with_DPDK_and_vHost_User
#   $2 - CI job type, one of verify, merge, daily
function execute_vsperf() {
    # figure out log file name
    LOG_FILE="${LOG_FILE_PREFIX}"`date "+%Y%m%d_%H%M%S%N"`".log"

    # figure out list of TCs and execution parameters
    case $2 in
        "verify")
            TESTPARAM=$TESTPARAM_VERIFY
            TESTCASES=$TESTCASES_VERIFY
            ;;
        "merge")
            TESTPARAM=$TESTPARAM_MERGE
            TESTCASES=$TESTCASES_MERGE
            ;;
        *)
            # by default use daily build
            TESTPARAM=$TESTPARAM_DAILY
            TESTCASES=$TESTCASES_DAILY
            ;;
    esac

    # execute testcases
    echo -e "\nExecution of VSPERF for $1"
    # vsperf must be executed directly from vsperf directory
    cd ..
    case $1 in
        "OVS_vanilla")
            echo "$VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsVanilla --vnf QemuVirtioNet $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE"
            $VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsVanilla --vnf QemuVirtioNet $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE
            ;;
        "OVS_with_DPDK_and_vHost_Cuse")
            echo "$VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsDpdkVhost --vnf QemuDpdkVhostCuse $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE"
            $VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsDpdkVhost --vnf QemuDpdkVhostCuse $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE
            ;;
        *)
            echo "$VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsDpdkVhost --vnf QemuDpdkVhostUser $CONF_FILE $TESTPARAM $TESTCASES > $LOG_FILE"
            $VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsDpdkVhost --vnf QemuDpdkVhostUser $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE
            ;;
    esac
    # let's go back to CI dir
    cd -

    # evaluation of results
    echo -e "\nResults for $1"
    RES_DIR=`grep "Creating result directory" $LOG_FILE | cut -d'/' -f2-`
    if [ "x" == "x${RES_DIR}" ] ; then
        echo "FAILURE: Results are not available."
    else
        print_results "/${RES_DIR}"
    fi
}

#
# main
#

# execute job based on passed parameter
case $1 in
    "verify")
        echo "VSPERF verify job"
        echo "================="

        #execute_vsperf OVS_with_DPDK_and_vHost_User $1

        exit $EXIT
        ;;
    "merge")
        echo "VSPERF merge job"
        echo "================"

        #execute_vsperf OVS_with_DPDK_and_vHost_User $1

        exit $EXIT
        ;;
    *)
        echo "VSPERF daily job"
        echo "================"

        execute_vsperf OVS_with_DPDK_and_vHost_User $1
        execute_vsperf OVS_vanilla $1

        exit $EXIT
        ;;
esac

exit $EXIT

#
# end
#
