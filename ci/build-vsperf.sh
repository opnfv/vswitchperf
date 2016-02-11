#!/bin/bash
#
# Copyright 2015-2016 Intel Corporation.
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
# exit codes
#

EXIT=0
EXIT_TC_FAILED=1
EXIT_NO_RESULTS=10
EXIT_NO_TEST_REPORT_LOG_DIR=11

#
# configuration
#

VSPERF_BIN='./vsperf'
LOG_FILE_USER='/tmp/vsperf_user.log'
LOG_FILE_VANILLA='/tmp/vsperf_vanilla.log'
LOG_FILE_PREFIX="/tmp/vsperf_build"
OPNFV_POD="intel-pod3"
DATE=$(date -u +"%Y-%m-%d_%H-%M-%S")
BRANCH=${GIT_BRANCH##*/}

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
if [ -f $HOME/vsperf-${BRANCH}.conf ] ; then
    # branch specific config was found
    CONF_FILE="--conf-file ${HOME}/vsperf-${BRANCH}.conf"
else
    if [ -f $HOME/vsperf.conf ] ; then
        CONF_FILE="--conf-file ${HOME}/vsperf.conf"
    else
        CONF_FILE=""
    fi
fi

# Test report related configuration
TEST_REPORT_PARTIAL="*_test_report.rst"
TEST_REPORT_DIR="../docs/results"
TEST_REPORT_INDEX="${TEST_REPORT_DIR}/index.rst"
TEST_REPORT_LINK_OLD="https://wiki.opnfv.org/wiki/vsperf_results"
TEST_REPORT_FILE="docs_output/results/results.pdf"
TEST_REPORT_TARBALL="vswitchperf_logs_${DATE}.tar.gz"

if [[ "x${BRANCH}" == "xmaster" ]]; then
    TEST_REPORT_LINK_NEW="https://artifactory.opnfv.org/logs/$PROJECT/$NODE_NAME/$DATE/${TEST_REPORT_TARBALL}"
else
    TEST_REPORT_LINK_NEW="https://artifactory.opnfv.org/logs/$PROJECT/$NODE_NAME/$BRANCH/$DATE/${TEST_REPORT_TARBALL}"
fi

TEST_REPORT_LOG_DIR="${HOME}/opnfv/$PROJECT/results/$BRANCH"

# store VSPERF root dir
cd ..
VSPERF_ROOT=$(pwd)
cd - &> /dev/null

#
# functions
#

# terminate vsperf and all its utilities
# it is expected that vsperf is the only python3 app
# and no other ovs or qemu instances are running
# at CI machine
# parameters:
#   none
function terminate_vsperf() {
    sudo pkill stress &> /dev/null
    sudo pkill python3 &> /dev/null
    sudo killall -9 qemu-system-x86_64 &> /dev/null

    # sometimes qemu resists to terminate, so wait a bit and kill it again
    if pgrep qemu-system-x86_64 &> /dev/null ; then
        sleep 5
        sudo killall -9 qemu-system-x86_64 &> /dev/null
        sleep 5
    fi

    sudo pkill ovs-vswitchd &> /dev/null
    sleep 1
    sudo pkill ovsdb-server &> /dev/null
    sleep 1
}

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
            EXIT=$EXIT_TC_FAILED
        fi
    done
}

# execute tests and display results
# parameters:
#   $1 - vswitch and vnf combination, one of OVS_vanilla, OVS_with_DPDK_and_vHost_Cuse, OVS_with_DPDK_and_vHost_User
#   $2 - CI job type, one of verify, merge, daily
function execute_vsperf() {
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

    DATE_SUFFIX=$(date -u +"%Y-%m-%d_%H-%M-%S")

    case $1 in
        "OVS_vanilla")
            # figure out log file name
            LOG_SUBDIR="OvsVanilla"
            LOG_FILE="${LOG_FILE_PREFIX}_${LOG_SUBDIR}_${DATE_SUFFIX}.log"

            echo "$VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsVanilla --vnf QemuVirtioNet $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE"
            $VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsVanilla --vnf QemuVirtioNet $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE
            ;;
        "OVS_with_DPDK_and_vHost_Cuse")
            # figure out log file name
            LOG_SUBDIR="OvsDpdkVhostCuse"
            LOG_FILE="${LOG_FILE_PREFIX}_${LOG_SUBDIR}_${DATE_SUFFIX}.log"

            echo "$VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsDpdkVhost --vnf QemuDpdkVhostCuse $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE"
            $VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsDpdkVhost --vnf QemuDpdkVhostCuse $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE
            ;;
        *)
            # figure out log file name
            LOG_SUBDIR="OvsDpdkVhost"
            LOG_FILE="${LOG_FILE_PREFIX}_${LOG_SUBDIR}_${DATE_SUFFIX}.log"

            echo "$VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsDpdkVhost --vnf QemuDpdkVhostUser $CONF_FILE $TESTPARAM $TESTCASES > $LOG_FILE"
            $VSPERF_BIN --opnfvpod="$OPNFV_POD" --vswitch OvsDpdkVhost --vnf QemuDpdkVhostUser $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE
            ;;
    esac
    # let's go back to CI dir
    cd - &> /dev/null

    # evaluation of results
    echo -e "\nResults for $1"
    RES_DIR="/$(grep "Creating result directory" $LOG_FILE | cut -d'/' -f2-)"
    if [[ "/" == "${RES_DIR}" ]] ; then
        echo "FAILURE: Results are not available."
        exit $EXIT_NO_RESULTS
    else
        print_results "${RES_DIR}"
    fi

    # show detailed result figures
    for md_file in $(grep '\.md"$' $LOG_FILE | cut -d'"' -f2); do
        # TC resut file header
        echo -e "\n-------------------------------------------------------------------"
        echo -e " $md_file"
        echo -e "-------------------------------------------------------------------\n"
        # TC details
        sed -n '/^- Test ID/,/Bidirectional/{/Packet size/b;p;/Bidirectional/q};/Results\/Metrics Collected/,/Statistics collected/{/^$/p;/^|/p}' $md_file
        # TC results
        sed -n '/Results\/Metrics Collected/,/Statistics collected/{/^$/p;/^|/p}' $md_file | grep -v "Unknown" | cat -s
    done

    # add test results into the final doc template
    for report in ${RES_DIR}/${TEST_REPORT_PARTIAL} ; do
        # modify link to the artifactory with test report and logs
        if [ -f $report ] ; then
            sed -i -e "s,$TEST_REPORT_LINK_OLD,$TEST_REPORT_LINK_NEW," "$report"
            cp $report $TEST_REPORT_DIR
            echo "   $(basename $report)" >> $TEST_REPORT_INDEX
        fi
    done

    # copy logs into dedicated directory
    mkdir ${TEST_REPORT_LOG_DIR}/${LOG_SUBDIR}
    [ -f "$LOG_FILE" ] && cp -a "${LOG_FILE}" "${TEST_REPORT_LOG_DIR}/${LOG_SUBDIR}" &> /dev/null
    [ -d "$RES_DIR" ] && cp -ar "$RES_DIR" "${TEST_REPORT_LOG_DIR}/${LOG_SUBDIR}" &> /dev/null
}

# generates final test_report in PDF and HTML formats
function generate_report() {

    cd $VSPERF_ROOT

    # prepare final tarball with all logs...
    tar --exclude "${TEST_REPORT_TARBALL}" -czf "${TEST_REPORT_LOG_DIR}/${TEST_REPORT_TARBALL}" $(find "${TEST_REPORT_LOG_DIR}" -mindepth 1 -maxdepth 1 -type d)
    # ...and remove original log files
    find "${TEST_REPORT_LOG_DIR}" -mindepth 1 -maxdepth 1 -type d -exec rm -rf \{\} \;

    # clone releng repository
    echo "Cloning releng repository..."
    [ -d releng ] && rm -rf releng
    git clone https://gerrit.opnfv.org/gerrit/releng &> /dev/null

    # generate final docs with test results
    echo "Generating test report..."
    sed -ie 's,python ,python2 ,g' ./releng/utils/docs-build.sh
    ./releng/utils/docs-build.sh &> /dev/null

    # store PDF with test results into dedicated directory
    if [ -f $TEST_REPORT_FILE ] ; then
        cp -a $TEST_REPORT_FILE $TEST_REPORT_LOG_DIR
        echo "Final test report has been created."
    else
        echo "FAILURE: Generation of final test report has failed."
    fi

    cd - &> /dev/null
}

# pushes test report and logs collected during test execution into artifactory
function push_results_to_artifactory() {
    cd $VSPERF_ROOT
    echo "Pushing results and logs into artifactory..."
    . ./releng/utils/push-test-logs.sh "$DATE"
    cd - &> /dev/null
}

# removes any local changes of repository
function cleanup() {
    cd $VSPERF_ROOT
    echo "Cleaning up..."
    git stash -u
    cd - &> /dev/null
}

# prepares directory for logs collection and removes old logs
function initialize_logdir() {
    if [[ "x$TEST_REPORT_LOG_DIR" == "x" ]] ; then
        echo "FAILURE: Logging directory is not defined. Logs and report cannot be published!"
        exit $EXIT_NO_TEST_REPORT_LOG_DIR
    else
        # remove TEST_REPORT_LOG_DIR if it exists
        if [ -e $TEST_REPORT_LOG_DIR ] ; then
            if [ -f $TEST_REPORT_LOG_DIR ] ; then
                rm $TEST_REPORT_LOG_DIR
            else
                rm -rf ${TEST_REPORT_LOG_DIR}
            fi
        fi
        # create TEST_REPORT_LOG_DIR
        mkdir -p $TEST_REPORT_LOG_DIR
    fi
}

#
# main
#

# initialization
initialize_logdir

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

        terminate_vsperf
        execute_vsperf OVS_with_DPDK_and_vHost_User $1
        terminate_vsperf
        execute_vsperf OVS_vanilla $1
        terminate_vsperf

        generate_report

        push_results_to_artifactory

        cleanup

        exit $EXIT
        ;;
esac

exit $EXIT

#
# end
#
