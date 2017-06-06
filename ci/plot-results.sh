#!/bin/bash
#
# Copyright 2017 Intel Corporation.
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

# Script for graphical representation of VSPERF results
#
# Usage:
#   ./create_graph ["test names" [filter [directory]]]
#
# where:
#       "test names" is a !!! quoted !!! string with vsperf testcase names separated
#           by spaces
#           Default value: "phy2phy_tput"
#
#       "filter" is used to select matching VSPERF results; Its value
#           will be used as PATTERN of grep command executed on selected
#           csv result files.
#           Default value: ",OvsDpdkVhost,"
#
#       "directory" is a directory name, where vsperf results (i.e. results_*
#           subdirectories) are located
#           Default value: "/tmp"
#
# Example of invocation:
#   ./create_graph "phy2phy_tput phy2phy_cont pvp_cont pvvp_cont" ",OvsVanilla,"

TESTS="phy2phy_tput"    # default set of TCs to be plotted
FILTER=",OvsDpdkVhost," # default filter to be applied on matching CSV files
NUMBER_OF_RESULTS=5     # max number of recent results to be compared in graph
CSV_RESULT_COL=2        # column number with result to be plotted, e.g. 2 for rx_throughput_fps
B2B_CSV_RESULT_COL=1    # column number with result to be plotted for back2back TCs
CSV_PKT_SIZE_COL=12     # column number with frame/packet size
B2B_CSV_PKT_SIZE_COL=4  # column number with frame/packet size for back2back TCs
NUMBER_OF_PKT_SIZES=0   # to be detected automatically
MAX_NUMBER_OF_PKT_SIZES=10
DIR="/tmp"              # directory where vsperf results are stored
PNG_PREFIX='vsperf_'

function clean_data() {
    rm -rf *csv
    rm -rf *plot
    rm -rf *png
}

function prepare_data() {
    for test_name in $TESTS; do
        FIRST=1
        CSV_LIST=`grep -r ",${test_name}," ${DIR}/results_*/*csv | grep $FILTER | cut -d':' -f1 | uniq | sort | tail -n ${NUMBER_OF_RESULTS}`
        for result_file in $CSV_LIST ; do
            tmp_dir=`dirname $result_file`
            TIMESTAMP=`basename $tmp_dir | cut -d'_' -f2-`
            if [ $FIRST -eq 1 ] ; then
                NUMBER_OF_PKT_SIZES=$((`wc -l ${result_file} | cut -d' ' -f1`-1))
                if [ $NUMBER_OF_PKT_SIZES -gt $MAX_NUMBER_OF_PKT_SIZES ] ; then
                    NUMBER_OF_PKT_SIZES=$MAX_NUMBER_OF_PKT_SIZES
                fi
                if grep back2back ${result_file} &> /dev/null ; then
                    PKT_SIZE_COL=$B2B_CSV_PKT_SIZE_COL
                    RES_COL=$B2B_CSV_RESULT_COL
                else
                    PKT_SIZE_COL=$CSV_PKT_SIZE_COL
                    RES_COL=$CSV_RESULT_COL
                fi
                RESULT_HEADER=`tail -n+2 ${result_file} | head -n ${NUMBER_OF_PKT_SIZES} | cut -d',' -f${PKT_SIZE_COL} | paste -d',' -s`
                echo "Date/PKT Size [B],${RESULT_HEADER}" > "${test_name}.csv"
                FIRST=0
            fi
            RESULT_4ALL_PKT_SIZES=`tail -n+2 ${result_file} | head -n ${NUMBER_OF_PKT_SIZES} | cut -d',' -f${RES_COL} | paste -d',' -s`
            echo "${TIMESTAMP},${RESULT_4ALL_PKT_SIZES}" >> "${test_name}.csv"
        done
    done
}

function plot_data() {
    echo "Created graphs:"
    SUFFIX=`echo $FILTER | tr -d -C [:alnum:]`
    for TEST_CSV in *csv; do
        [ ! -f $TEST_CSV ] && continue
        TEST_NAME=`basename ${TEST_CSV} .csv`"_${SUFFIX}"
        OUTPUT="$TEST_NAME.plot"
        cat > $OUTPUT <<- EOM
set datafile separator ","
set xdata time
set timefmt "%Y-%m-%d_%H:%M:%S"
set format x "%m-%d"
set xlabel "date"
set format y "%8.0f"
set ylabel "fps"
set yrange [0:]
set term png size 1024,768
EOM
        iter=0
        echo "set title \"$TEST_NAME\"" >> $OUTPUT
        echo "set output \"${PNG_PREFIX}${TEST_NAME}.png\"" >> $OUTPUT
        echo -n "plot " >> $OUTPUT
        SEP=""
        while [ $iter -lt $NUMBER_OF_PKT_SIZES ] ; do
            COL=$((2+$iter))
            echo $"$SEP '$TEST_CSV' using 1:$COL with linespoints title columnheader($COL) \\" >> $OUTPUT
            iter=$(($iter+1))
            SEP=","
        done
        echo -e "\t${PNG_PREFIX}${TEST_NAME}.png"
        gnuplot $OUTPUT
    done
}

#
# Main body
#

# override default set of TESTS if specified by 1st parameter
if [ "$1" != "" ] ; then
    TESTS="$1"
fi

# override default filter if specified by 2nd parameter
if [ "$2" != "" ] ; then
    FILTER="$2"
fi

# override default directory with results by 3rd parameter
if [ "$3" != "" ] ; then
    DIR="$3"
fi
clean_data

echo -e "Plot data input:"
echo -e "\tTESTS: $TESTS"
echo -e "\tFilter: $FILTER"
echo -e "\tResults direcotry: $DIR"

prepare_data
plot_data
