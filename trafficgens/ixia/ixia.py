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
IXIA traffic generator model.

Provides a model for the IXIA traffic generator. In addition, provides
a number of generic "helper" functions that are used to do the "heavy
lifting".

This requires the following settings in your config file:

* TRAFFICGEN_IXIA_LIB_PATH
    IXIA libraries path
* TRAFFICGEN_IXIA_HOST
    IXIA chassis IP address
* TRAFFICGEN_IXIA_CARD
    IXIA card
* TRAFFICGEN_IXIA_PORT1
    IXIA Tx port
* TRAFFICGEN_IXIA_PORT2
    IXIA Rx port

If any of these don't exist, the application will raise an exception
(EAFP).

Part of 'toit' - The OVS Integration Testsuite.
"""

from __future__ import print_function

import Tkinter
import logging
import os

from toit import trafficgen
from toit.conf import settings

_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
_IXIA_ROOT_DIR = getattr(settings, 'TRAFFICGEN_IXIA_ROOT_DIR')


def configure_env():
    """
    Configure envionment for TCL.

    This replaces the `ixwish_sie` file usually used with IXIA.
    """
    os.environ['IXIA_HOME'] = _IXIA_ROOT_DIR

    # USER MAY NEED TO CHANGE THESE IF USING OWN TCL LIBRARY
    os.environ['TCL_HOME'] = _IXIA_ROOT_DIR
    os.environ['TCLver'] = '8.5'

    # USER NORMALLY DOES NOT CHANGE ANY LINES BELOW
    os.environ['IxiaLibPath'] = os.path.expandvars('$IXIA_HOME/lib')
    os.environ['IxiaBinPath'] = os.path.expandvars('$IXIA_HOME/bin')

    os.environ['TCLLibPath'] = os.path.expandvars('$TCL_HOME/lib')
    os.environ['TCLBinPath'] = os.path.expandvars('$TCL_HOME/bin')

    os.environ['TCL_LIBRARY'] = os.path.expandvars('$TCLLibPath/tcl$TCLver')
    os.environ['TK_LIBRARY'] = os.path.expandvars('$TCLLibPath/tk$TCLver')

    os.environ['PATH'] = os.path.expandvars('$IxiaBinPath:.:$TCLBinPath:$PATH')
    os.environ['TCLLIBPATH'] = os.path.expandvars('$IxiaLibPath')
    os.environ['LD_LIBRARY_PATH'] = os.path.expandvars(
        '$IxiaLibPath:$TCLLibPath:$LD_LIBRARY_PATH')

    os.environ['IXIA_RESULTS_DIR'] = '/tmp/Ixia/Results'
    os.environ['IXIA_LOGS_DIR'] = '/tmp/Ixia/Logs'
    os.environ['IXIA_TCL_DIR'] = os.path.expandvars('$IxiaLibPath')
    os.environ['IXIA_SAMPLES'] = os.path.expandvars('$IxiaLibPath/ixTcl1.0')
    os.environ['IXIA_VERSION'] = '6.60.1000.11'


def _build_set_cmds(values, prefix='dict set'):
    """
    Generate a list of 'dict set' args for Tcl.

    Parse a dictionary and recursively build the arguments for the
    'dict set' Tcl command, given that this is of the format:

        dict set [name...] [key] [value]

    For example, for a non-nested dict (i.e. a non-dict element):

        dict set mydict mykey myvalue

    For a nested dict (i.e. a dict element):

        dict set mydict mysubdict mykey myvalue

    :param values: Dictionary to yield values for
    :param prefix: Prefix to append to output string. Generally the
        already generated part of the command.

    :yields: Output strings to be passed to a `Tcl` instance.
    """
    for key in values:
        value = values[key]
        if type(value) == dict:
            _prefix = ' '.join([prefix, key]).strip()
            for subkey in _build_set_cmds(value, _prefix):
                yield subkey
            continue

        # tcl doesn't recognise the strings "True" or "False", only "1"
        # or "0". Special case to convert them
        if type(value) == bool:
            value = str(int(value))
        else:
            value = str(value)

        if prefix:
            yield ' '.join([prefix, key, value]).strip()
        else:
            yield ' '.join([key, value]).strip()


class Ixia(trafficgen.TrafficGenerator):
    """
    A wrapper around the IXIA traffic generator.

    Runs different traffic generator tests through an Ixia traffic
    generator chassis by generating TCL scripts from templates.
    """
    _script = os.path.join(os.path.dirname(__file__), 'pass_fail.tcl')
    _tclsh = Tkinter.Tcl()
    _logger = logging.getLogger(__name__)

    def run_tcl(self, cmd):
        """
        Run a TCL script using the TCL interpreter found in ``tkinter``.

        :param cmd: Command to execute

        :returns: Output of command, where applicable.
        """
        self._logger.debug('%s%s', trafficgen.CMD_PREFIX, cmd)

        output = self._tclsh.eval(cmd)

        return output.split()

    def connect(self):
        """
        Connect to Ixia chassis.
        """
        ixia_cfg = {
            'lib_path': os.path.join(_IXIA_ROOT_DIR, 'lib', 'ixTcl1.0'),
            'host': getattr(settings, 'TRAFFICGEN_IXIA_HOST'),
            'card': getattr(settings, 'TRAFFICGEN_IXIA_CARD'),
            'port1': getattr(settings, 'TRAFFICGEN_IXIA_PORT1'),
            'port2': getattr(settings, 'TRAFFICGEN_IXIA_PORT2'),
        }

        self._logger.info('Connecting to IXIA...')

        self._logger.debug('IXIA configuration configuration : %s', ixia_cfg)

        configure_env()

        for cmd in _build_set_cmds(ixia_cfg, prefix='set'):
            self.run_tcl(cmd)

        output = self.run_tcl('source {%s}' % self._script)
        if output:
            self._logger.critical(
                'An error occured when connecting to IXIA...')
            raise RuntimeError('Ixia failed to initialise.')

        self._logger.info('Connected to IXIA...')

        return self

    def disconnect(self):
        """
        Disconnect from Ixia chassis.
        """
        self._logger.info('Disconnecting from IXIA...')

        self.run_tcl('cleanUp')

        self._logger.info('Disconnected from IXIA...')

    def _send_traffic(self, flow, traffic):
        """
        Send regular traffic.

        :param flow: Flow specification
        :param traffic: Traffic specification

        :returns: Results from IXIA
        """
        params = {}

        params['flow'] = flow
        params['traffic'] = self.traffic_defaults.copy()

        if traffic:
            params['traffic'] = trafficgen.merge_spec(
                params['traffic'], traffic)

        for cmd in _build_set_cmds(params):
            self.run_tcl(cmd)

        result = self.run_tcl('sendTraffic $flow $traffic')

        return result

    def send_burst_traffic(self, traffic=None, numpkts=100, time=20):
        flow = {
            'numpkts': numpkts,
            'time': time,
            'type': 'stopStream',
            'framerate': 100,
        }

        result = self._send_traffic(flow, traffic)

        assert len(result) == 6  # fail-fast if underlying Tcl code changes

        # ensure output is formatted as expected
        return trafficgen.BurstResult(*[int(x) for x in result])

    def send_cont_traffic(self, traffic=None, time=20, framerate=100):
        flow = {
            'numpkts': 100,
            'time': time,
            'type': 'contPacket',
            'framerate': framerate,
        }

        result = self._send_traffic(flow, traffic)

        assert len(result) == 8  # fail-fast if underlying Tcl code changes

        # drop the first 4 elements as we don't use/need them. In
        # addition, IxExplorer does not support latency or % line rate
        # metrics so we have to return dummy values for these metrics
        return trafficgen.ContResult(*[
            float(x) for x in result[4:]] + [0.0, 0.0, 0.0, 0.0, 0.0])

    def start_cont_traffic(self, traffic=None, framerate=100):
        return self.send_cont_traffic(traffic, 0, framerate)

    def stop_cont_traffic(self):
        return self.run_tcl('stopTraffic')

    def send_rfc2544_throughput(self, traffic=None, trials=3, duration=20,
                                lossrate=0.0, multistream=False):
        params = {}

        params['config'] = {
            'trials': trials,
            'duration': duration,
            'lossrate': lossrate,
            'multipleStreams': multistream,
        }
        params['traffic'] = self.traffic_defaults.copy()

        if traffic:
            params['traffic'] = trafficgen.merge_spec(
                params['traffic'], traffic)

        for cmd in _build_set_cmds(params):
            self.run_tcl(cmd)

        # this will return a list with one result
        result = self.run_tcl('rfcThroughputTest $config $traffic')

        assert len(result) == 8  # fail-fast if underlying Tcl code changes

        # drop the first 4 elements as we don't use/need them. In
        # addition, IxExplorer does not support latency or % line rate
        # metrics so we have to return dummy values for these metrics
        return trafficgen.ThroughputResult(*[
            float(x) for x in result[4:]] + [0.0, 0.0, 0.0, 0.0, 0.0])


if __name__ == '__main__':
    TRAFFIC = {
        'l3': {
            'proto': 'udp',
            'srcip': '10.1.1.1',
            'dstip': '10.1.1.254',
        },
    }

    with Ixia() as dev:
        print(dev.send_burst_traffic(traffic=TRAFFIC))
        print(dev.send_cont_traffic(traffic=TRAFFIC))
        print(dev.send_rfc2544_throughput(traffic=TRAFFIC))
