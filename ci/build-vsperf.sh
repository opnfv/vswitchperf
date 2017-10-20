#!/bin/bash
#
# Copyright 2015-2017 Intel Corporation.
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
EXIT_SANITY_TC_FAILED=2
EXIT_PYLINT_FAILED=4
EXIT_NO_RESULTS=128
EXIT_NO_TEST_REPORT_LOG_DIR=256

#
# configuration
#

VSPERF_BIN='./vsperf'
LOG_FILE_PREFIX="/tmp/vsperf_build"
DATE=$(date -u +"%Y-%m-%d_%H-%M-%S")
BRANCH=${GIT_BRANCH##*/}
VSPERFENV_DIR="$HOME/vsperfenv"
RESULTS_ARCHIVE="$HOME/ci_results_archive"

# CI job specific configuration
# VERIFY - run basic set of TCs with default settings
TESTCASES_VERIFY="vswitch_add_del_bridge vswitch_add_del_bridges vswitch_add_del_vport vswitch_add_del_vports vswitch_vports_add_del_flow"
TESTPARAM_VERIFY="--test-params VSWITCH_PMD_CPU_MASK='FF';VSWITCHD_DPDK_CONFIG={'dpdk-init':'true','dpdk-lcore-mask':'0xFF'}  --integration"
TESTCASES_VERIFY_VPP="vswitch_add_del_bridge vswitch_add_del_bridges vswitch_add_del_vport vswitch_add_del_vports vswitch_vports_add_del_connection_vpp"
TESTPARAM_VERIFY_VPP=$TESTPARAM_VERIFY
# MERGE - run selected TCs with default settings
TESTCASES_MERGE=$TESTCASES_VERIFY
TESTPARAM_MERGE=$TESTPARAM_VERIFY
TESTCASES_MERGE_VPP=$TESTCASES_VERIFY_VPP
TESTPARAM_MERGE_VPP=$TESTPARAM_VERIFY_VPP
# DAILY - run selected TCs for defined packet sizes
TESTCASES_DAILY='phy2phy_tput back2back phy2phy_tput_mod_vlan phy2phy_scalability pvp_tput pvp_back2back pvvp_tput pvvp_back2back'
TESTCASES_DAILY_VPP='phy2phy_tput_vpp phy2phy_back2back_vpp pvp_tput_vpp pvp_back2back_vpp pvvp_tput_vpp pvvp_back2back_vpp'
TESTPARAM_DAILY='--test-params TRAFFICGEN_PKT_SIZES=(64,128,512,1024,1518)'
TESTPARAM_DAILY_VPP=$TESTPARAM_DAILY
TESTCASES_SRIOV='pvp_tput'
TESTPARAM_SRIOV='--test-params TRAFFICGEN_PKT_SIZES=(64,128,512,1024,1518)'
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
# check if sriov specific config file exists if not then use default configuration
if [ -f $HOME/vsperf-${BRANCH}.conf.sriov ] ; then
    CONF_FILE_SRIOV="${CONF_FILE}.sriov"
else
    CONF_FILE_SRIOV=$CONF_FILE
fi

# Test report related configuration
TEST_REPORT_PARTIAL="*_test_report.rst"
TEST_REPORT_DIR="${WORKSPACE}/docs/testing/developer/devguide/results"
TEST_REPORT_INDEX="${TEST_REPORT_DIR}/index.rst"
TEST_REPORT_LINK_OLD="https://wiki.opnfv.org/wiki/vsperf_results"
TEST_REPORT_FILE="${WORKSPACE}/docs_output/testing_developer_devguide_results/index.html"
TEST_REPORT_TARBALL="vswitchperf_logs_${DATE}.tar.gz"

if [[ "x${BRANCH}" == "xmaster" ]]; then
    TEST_REPORT_LINK_NEW="https://artifacts.opnfv.org/logs/$PROJECT/$NODE_NAME/$DATE/${TEST_REPORT_TARBALL}"
else
    TEST_REPORT_LINK_NEW="https://artifacts.opnfv.org/logs/$PROJECT/$NODE_NAME/$BRANCH/$DATE/${TEST_REPORT_TARBALL}"
fi

TEST_REPORT_LOG_DIR="${HOME}/opnfv/$PROJECT/results/$BRANCH"

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
        if [ ! -e $1 ] ; then
            printf "    %-70s %-6s\n" "result_${i}" "FAILED"
            EXIT=$EXIT_TC_FAILED
        else
            RES_FILE=`ls -1 $1 | egrep "result_${i}_[0-9a-zA-Z\-]+.csv"`

            if [ "x$RES_FILE" != "x" -a -e "${1}/${RES_FILE}" ]; then
                if grep ^FAILED "${1}/${RES_FILE}" &> /dev/null ; then
                    printf "    %-70s %-6s\n" "result_${i}" "FAILED"
                    EXIT=$EXIT_TC_FAILED
                else
                    printf "    %-70s %-6s\n" "result_${i}" "OK"
                fi
            else
                printf "    %-70s %-6s\n" "result_${i}" "FAILED"
                EXIT=$EXIT_TC_FAILED
            fi
        fi
    done
}

# execute tests and display results
# parameters:
#   $1 - vswitch and vnf combination, one of OVS_vanilla, OVS_with_DPDK_and_vHost_User
#   $2 - CI job type, one of verify, merge, daily
function execute_vsperf() {
    OPNFVPOD=""
    # figure out list of TCs and execution parameters
    case $2 in
        "verify")
            if [ "$1" == "VPP" ] ; then
                TESTPARAM=$TESTPARAM_VERIFY_VPP
                TESTCASES=$TESTCASES_VERIFY_VPP
            else
                TESTPARAM=$TESTPARAM_VERIFY
                TESTCASES=$TESTCASES_VERIFY
            fi
            ;;
        "merge")
            if [ "$1" == "VPP" ] ; then
                TESTPARAM=$TESTPARAM_MERGE_VPP
                TESTCASES=$TESTCASES_MERGE_VPP
            else
                TESTPARAM=$TESTPARAM_MERGE
                TESTCASES=$TESTCASES_MERGE
            fi
            ;;
        *)
            # by default use daily build and upload results to the OPNFV databse
            if [ "$1" == "VPP" ] ; then
                TESTPARAM=$TESTPARAM_DAILY_VPP
                TESTCASES=$TESTCASES_DAILY_VPP
                # don't report VPP results into testresults DB, until TC name mapping
                # for VPP tests will be defined
                #OPNFVPOD="--opnfvpod=$NODE_NAME"
            else
                TESTPARAM=$TESTPARAM_DAILY
                TESTCASES=$TESTCASES_DAILY
                OPNFVPOD="--opnfvpod=$NODE_NAME"
            fi
            ;;
    esac

    # execute testcases
    echo -e "\nExecution of VSPERF for $1"

    DATE_SUFFIX=$(date -u +"%Y-%m-%d_%H-%M-%S")

    case $1 in
        "SRIOV")
            # use SRIOV specific TCs and configuration
            TESTPARAM=$TESTPARAM_SRIOV
            TESTCASES=$TESTCASES_SRIOV
            # figure out log file name
            LOG_SUBDIR="SRIOV"
            LOG_FILE="${LOG_FILE_PREFIX}_${LOG_SUBDIR}_${DATE_SUFFIX}.log"

            echo "    $VSPERF_BIN --vswitch none --vnf QemuPciPassthrough $CONF_FILE_SRIOV $TESTPARAM $TESTCASES &> $LOG_FILE"
            $VSPERF_BIN --vswitch none --vnf QemuPciPassthrough $CONF_FILE_SRIOV $TESTPARAM $TESTCASES &> $LOG_FILE
            ;;
        "VPP")
            # figure out log file name
            LOG_SUBDIR="VppDpdkVhost"
            LOG_FILE="${LOG_FILE_PREFIX}_${LOG_SUBDIR}_${DATE_SUFFIX}.log"

            hugepages_info > $LOG_FILE
            echo "    $VSPERF_BIN $OPNFVPOD --vswitch VppDpdkVhost --vnf QemuDpdkVhostUser $CONF_FILE $TESTPARAM $TESTCASES > $LOG_FILE"
            $VSPERF_BIN $OPNFVPOD --vswitch VppDpdkVhost --vnf QemuDpdkVhostUser $CONF_FILE $TESTPARAM $TESTCASES &>> $LOG_FILE
            hugepages_info >> $LOG_FILE
            ;;
        "OVS_vanilla")
            # figure out log file name
            LOG_SUBDIR="OvsVanilla"
            LOG_FILE="${LOG_FILE_PREFIX}_${LOG_SUBDIR}_${DATE_SUFFIX}.log"

            echo "    $VSPERF_BIN $OPNFVPOD --vswitch OvsVanilla --vnf QemuVirtioNet $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE"
            $VSPERF_BIN $OPNFVPOD --vswitch OvsVanilla --vnf QemuVirtioNet $CONF_FILE $TESTPARAM $TESTCASES &> $LOG_FILE
            ;;
        *)
            # figure out log file name
            LOG_SUBDIR="OvsDpdkVhost"
            LOG_FILE="${LOG_FILE_PREFIX}_${LOG_SUBDIR}_${DATE_SUFFIX}.log"

            hugepages_info > $LOG_FILE
            echo "    $VSPERF_BIN $OPNFVPOD --vswitch OvsDpdkVhost --vnf QemuDpdkVhostUser $CONF_FILE $TESTPARAM $TESTCASES > $LOG_FILE"
            $VSPERF_BIN $OPNFVPOD --vswitch OvsDpdkVhost --vnf QemuDpdkVhostUser $CONF_FILE $TESTPARAM $TESTCASES &>> $LOG_FILE
            hugepages_info >> $LOG_FILE
            ;;
    esac

    # evaluation of results
    echo -e "\nResults for $1"
    RES_DIR="/$(grep "Creating result directory" $LOG_FILE | cut -d'/' -f2-)"
    if [[ "/" == "${RES_DIR}" ]] ; then
        echo "FAILURE: Results are not available."
        echo "-------------------------------------------------------------------"
        cat $LOG_FILE
        echo "-------------------------------------------------------------------"
        exit $EXIT_NO_RESULTS
    else
        print_results "${RES_DIR}"
        if [ $(($EXIT & $EXIT_TC_FAILED)) -gt 0 ] ; then
            echo "-------------------------------------------------------------------"
            cat $LOG_FILE
            echo "-------------------------------------------------------------------"
        fi
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

    # prepare final tarball with all logs...
    tar --exclude "${TEST_REPORT_TARBALL}" -czf "${TEST_REPORT_LOG_DIR}/${TEST_REPORT_TARBALL}" $(find "${TEST_REPORT_LOG_DIR}" -mindepth 1 -maxdepth 1 -type d)
    # ...and move original log files to the archive directory...
    find "${TEST_REPORT_LOG_DIR}" -maxdepth 2 -name "results_*" -type d -exec mv \{\} ${RESULTS_ARCHIVE} \;
    # ...and remove the rest
    find "${TEST_REPORT_LOG_DIR}" -mindepth 1 -maxdepth 1 -type d -exec rm -rf \{\} \;

    # clone opnfvdocs repository
    echo "Cloning opnfvdocs repository..."
    [ -d opnfvdocs ] && rm -rf opnfvdocs
    git clone https://gerrit.opnfv.org/gerrit/opnfvdocs &> /dev/null

    # generate final docs with test results
    echo "Generating test report..."
    sed -ie 's,python ,python2 ,g' ./opnfvdocs/scripts/docs-build.sh
    OPNFVDOCS_DIR='./opnfvdocs' ./opnfvdocs/scripts/docs-build.sh &> /dev/null

    # store HTML report with test results into dedicated directory
    if [ -f $TEST_REPORT_FILE ] ; then
        cp -ar $TEST_REPORT_FILE $(dirname $TEST_REPORT_FILE)/_static $TEST_REPORT_LOG_DIR
        echo "Final test report has been created."
    else
        echo "FAILURE: Generation of final test report has failed."
    fi
}

# generates graphs from recent test results
function generate_and_push_graphs() {
    # create graphs from results in archive directory
    ./ci/plot-results.sh "$1" "$2" "$RESULTS_ARCHIVE"

    # push graphs into artifactory
    if ls *png &> /dev/null ; then
        gsutil cp *png gs://artifacts.opnfv.org/logs/vswitchperf/intel-pod12/graphs/
    else
        echo "Graphs were not created."
    fi
}

# pushes test report and logs collected during test execution into artifactory
function push_results_to_artifactory() {
    # clone releng repository
    echo "Cloning releng repository..."
    [ -d releng ] && rm -rf releng
    git clone https://gerrit.opnfv.org/gerrit/releng &> /dev/null

    echo "Pushing results and logs into artifactory..."
    . ./releng/utils/push-test-logs.sh "$DATE"

    # enter workspace as it could be modified by 3rd party script
    cd $WORKSPACE
}

# removes any local changes of repository
function cleanup() {
    echo "Cleaning up..."
    git stash -u
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

# verify basic vsperf functionality
function execute_vsperf_sanity() {
    DATE_SUFFIX=$(date -u +"%Y-%m-%d_%H-%M-%S")
    LOG_FILE="${LOG_FILE_PREFIX}_sanity_${DATE_SUFFIX}.log"
    echo "Execution of VSPERF sanity checks:"
    for PARAM in '--version' '--help' '--list-trafficgens' '--list-collectors' '--list-vswitches' '--list-fwdapps' '--list-vnfs' '--list-settings' '--list' '--integration --list'; do
        echo -e "-------------------------------------------------------------------" >> $LOG_FILE
        echo "$VSPERF_BIN $PARAM $CONF_FILE" >> $LOG_FILE
        echo -e "-------------------------------------------------------------------" >> $LOG_FILE
        $VSPERF_BIN $PARAM $CONF_FILE &>> $LOG_FILE
        if $VSPERF_BIN $PARAM $CONF_FILE &>> $LOG_FILE ; then
            printf "    %-70s %-6s\n" "$VSPERF_BIN $PARAM" "OK"
        else
            printf "    %-70s %-6s\n" "$VSPERF_BIN $PARAM" "FAILED"
            EXIT=$EXIT_SANITY_TC_FAILED
        fi
        echo >> $LOG_FILE
    done
    echo "Sanity log file $LOG_FILE"
    if [ $(($EXIT & $EXIT_SANITY_TC_FAILED)) -gt 0 ] ; then
        echo "-------------------------------------------------------------------"
        cat $LOG_FILE
        echo "-------------------------------------------------------------------"
    fi
}

# execute pylint to check code quality
function execute_vsperf_pylint_check() {
    if ! ./check -b ; then
        EXIT=$EXIT_PYLINT_FAILED
    fi
}

# check and install required packages at nodes running VERIFY and MERGE jobs
function dependencies_check() {
    . /etc/os-release
    if [ $ID == "ubuntu" ] ; then
        echo "Dependencies check"
        echo "=================="
        # install system packages
        for PACKAGE in "python3-tk" "sysstat" "bc" ; do
            if dpkg -s $PACKAGE &> /dev/null ; then
                printf "    %-70s %-6s\n" $PACKAGE "OK"
            else
                printf "    %-70s %-6s\n" $PACKAGE "missing"
                sudo apt-get install -y $PACKAGE
            fi
        done
        # install additional python packages into python environment
        for PACKAGE in "pylint" ; do
            if pip show $PACKAGE &> /dev/null ; then
                printf "    %-70s %-6s\n" $PACKAGE "OK"
            else
                printf "    %-70s %-6s\n" $PACKAGE "missing"
                pip install $PACKAGE
            fi
        done
        echo
    fi
}

# configure hugepages
function configure_hugepages() {
    HP_MAX=10240
    HP_REQUESTED=3072
    HP_NR=`cat /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages`
    HP_FREE=`cat /sys/devices/system/node/node0/hugepages/hugepages-2048kB/free_hugepages`
    # check if HP must be (re)configured
    if [ $HP_FREE -lt $HP_REQUESTED ] ; then
        HP_NR_NEW=$(($HP_NR+($HP_REQUESTED-$HP_FREE)))
        if [ $HP_NR_NEW -gt $HP_MAX ] ; then
            HP_NR_NEW=$HP_MAX
        fi
        sudo bash -c "echo $HP_NR_NEW > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages"
    fi

    if [ -f /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages ] ; then
        sudo bash -c "echo 0 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages"
    fi
}

# dump hugepages configuration
function hugepages_info() {
    echo "-------------------------------------------------------------------"
    head /sys/devices/system/node/node*/hugepages/hugepages*/*
    echo "-------------------------------------------------------------------"
}

#
# main
#

echo

# enter workspace dir
cd $WORKSPACE

# create virtualenv if needed
if [ ! -e $VSPERFENV_DIR ] ; then
    echo "Create VSPERF environment"
    echo "========================="
    virtualenv --python=python3 "$VSPERFENV_DIR"
    echo
fi

# acivate and update virtualenv
echo "Update VSPERF environment"
echo "========================="
source "$VSPERFENV_DIR"/bin/activate
pip install -r ./requirements.txt
echo

# VERFIY&MERGE job specific - check if required packages are installed
dependencies_check

# initialization
initialize_logdir

# configure hugepages
echo "Configure hugepages"
echo "==================="
configure_hugepages
hugepages_info | grep -v '^--'
echo

# execute job based on passed parameter
case $1 in
    "verify")
        echo "================="
        echo "VSPERF verify job"
        echo "================="

        execute_vsperf_pylint_check
        terminate_vsperf
        execute_vsperf_sanity
        terminate_vsperf
        execute_vsperf OVS_with_DPDK_and_vHost_User $1
        terminate_vsperf
        execute_vsperf OVS_vanilla $1
        terminate_vsperf
        execute_vsperf VPP $1
        terminate_vsperf

        exit $EXIT
        ;;
    "merge")
        echo "================"
        echo "VSPERF merge job"
        echo "================"

        execute_pylint_check
        terminate_vsperf
        execute_vsperf_sanity
        terminate_vsperf
        execute_vsperf OVS_with_DPDK_and_vHost_User $1
        terminate_vsperf
        execute_vsperf OVS_vanilla $1
        terminate_vsperf
        execute_vsperf VPP $1
        terminate_vsperf

        exit $EXIT
        ;;
    *)
        echo "================"
        echo "VSPERF daily job"
        echo "================"

        terminate_vsperf
        execute_vsperf OVS_with_DPDK_and_vHost_User $1
        terminate_vsperf
        execute_vsperf OVS_vanilla $1
        terminate_vsperf
        execute_vsperf VPP $1
        terminate_vsperf
        execute_vsperf SRIOV $1
        terminate_vsperf

        generate_report

        push_results_to_artifactory

        generate_and_push_graphs "$TESTCASES_DAILY" ",OvsDpdkVhost,"
        generate_and_push_graphs "$TESTCASES_DAILY" ",OvsVanilla,"
        generate_and_push_graphs "$TESTCASES_DAILY_VPP" ",VppDpdkVhost,"
        generate_and_push_graphs "$TESTCASES_SRIOV" ",none,"

        cleanup

        exit $EXIT
        ;;
esac

exit $EXIT

#
# end
#
