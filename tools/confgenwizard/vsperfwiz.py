# Copyright 2019-2020 Spirent Communications.
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
Tool to create configuration file for VSPERF
"""

from __future__ import print_function
import signal
import sys
from pypsi import wizard as wiz
from pypsi.shell import Shell
import nicinfo


#pylint: disable=too-many-instance-attributes
class VsperfWizard(object):
    """
    Class to create wizards
    """

    def __init__(self):
        """
        Perform Initialization.
        """
        self.shell = Shell()
        self.vpp_values = {}
        self.dut_values = {}
        self.main_values = {}
        self.guest_values = {}
        self.ovs_values = {}
        self.ixnet_values = {}
        self.stc_values = {}
        self.trex_values = {}
        self.traffic_values = {}
        self.vpp_values = {}
        self.wiz_dut = None
        self.wiz_ixnet = None
        self.wiz_stc = None
        self.wiz_ovs = None
        self.wiz_traffic = None
        self.wiz_main = None
        self.wiz_guest = None
        self.wiz_trex = None
        self.wiz_vpp = None
        self.rhi = None
        self.devices = ''
        self.devs = {}



######## Support Functions ############################
    def get_nicpcis(self):
        """
        Get NIC information from Remote Host
        """
        self.rhi = nicinfo.RemoteInfo(self.dut_values['dutip'],
                                      self.dut_values['dutuname'],
                                      self.dut_values['dutpwd'])
        dev_list = self.rhi.get_nic_details()
        index = 0
        for dev in dev_list:
            self.devices += str("(" + str(index) + ")" + " "
                                + str(dev["Slot"]) + ', ')
            self.devs[str(index)] = str(dev["Slot"])
            index = index + 1

    def get_nics_string(self):
        """
        Create string that's acceptable to configuration
        """
        indexes = self.main_values['nics'].split(',')
        wlns = ''
        for index in indexes:
            wlns += "'" + self.devs[index] + "' ,"
        print(wlns)
        return wlns.rstrip(',')


############# All the Wizards ##################################

    def dut_wizard(self):
        """
        Wizard to collect DUT information
        """
        self.wiz_dut = wiz.PromptWizard(
            name="VSPERF DUT Info Collection",
            description="This collects DUT info",
            steps=(
                # The list of input prompts to ask the user.
                wiz.WizardStep(
                    # ID where the value will be stored
                    id="dutip",
                    # Display name
                    name="Enter the IP address of the DUT [local]",
                    # Help message
                    help="IP address of the DUT host",
                    # List of validators to run on the input
                    validators=(wiz.required_validator)
                ),
                wiz.WizardStep(
                    # ID where the value will be stored
                    id="dutuname",
                    # Display name
                    name="Enter the username to connect to DUT",
                    # Help message
                    help="Username for DUT host",
                    # List of validators to run on the input
                    validators=(wiz.required_validator)
                ),
                wiz.WizardStep(
                    # ID where the value will be stored
                    id="dutpwd",
                    # Display name
                    name="Enter the Password to connect to DUT",
                    # Help message
                    help="Password for the DUT host",
                    # List of validators to run on the input
                    validators=(wiz.required_validator)
                ),
            )
        )

    def main_wizard(self):
        """
        The Main Wizard
        """
        # First get the nics.
        self.get_nicpcis()
        self.wiz_main = wiz.PromptWizard(
            name="VSPERF Common Configuration",
            description="This configuration covers Basic inputs",
            steps=(
                # The list of input prompts to ask the user.
                wiz.WizardStep(
                    # ID where the value will be stored
                    id="vswitch",
                    # Display name
                    name="VSwitch to use? - OVS or VPP?",
                    # Help message
                    help=" Enter the vswitch to use - either OVS or VPP",
                    # List of validators to run on the input
                    default='OVS'
                ),
                wiz.WizardStep(
                    id='nics',
                    name="NICs to Whitelist: " + self.devices,
                    help="Enter the list (separated by comma) of PCI-IDs",
                    validators=(wiz.required_validator),
                ),
                wiz.WizardStep(
                    id='tgen',
                    name=("What trafficgen to use: [TestCenter" +
                          " IxNet, Moongen, Trex]?"),
                    help=("Enter the trafficgen to use -" +
                          " TestCenter, IxNet, Moongen, Trex"),
                    validators=(wiz.required_validator),
                    default="Trex"
                ),
                wiz.WizardStep(
                    id='guest',
                    name=("Is Scenario either PVP or PVVP?"),
                    help=("This is ti capture guest Configuration"),
                    validators=(wiz.required_validator),
                    default="YES"
                )
            )
        )

    def traffic_wizard(self):
        """
        Wizard to collectd Traffic Info.
        """
        self.wiz_traffic = wiz.PromptWizard(
            name="Traffic Configuration",
            description="This configuration covers Traffic specifc inputs",
            steps=(
                wiz.WizardStep(
                    id='pktsizes',
                    name='Enter the Packet Sizes - comma separated',
                    help="Allowed values: (64,128,256,512,1024,1280,1518)",
                    validators=(wiz.required_validator)
                ),
                wiz.WizardStep(
                    id='duration',
                    name='Enter the Duration (in secs) for the traffic',
                    help="Enter for how long each iteration should be",
                    default='60',
                ),
                # wiz.WizardStep(
                #    id='multistream',
                #    name='Multistream preferred?',
                #    help="Multistream preference - Yes or No",
                #    default='No',
                # validators=(wiz.required_validator)
                #),
                wiz.WizardStep(
                    id='count',
                    name='Number of flows?',
                    help="Enter the number of flows - 2 - 1,000,000",
                    default='2',
                    # validators=(wiz.required_validator)
                ),
            )
        )

    def ovs_wizard(self):
        """
        Wizard to collect OVS Information
        """
        self.wiz_ovs = wiz.PromptWizard(
            name="Vswitch Configuration",
            description="Specific configurations of the virtual-Switch",
            steps=(
                wiz.WizardStep(
                    id='type',
                    name='OVS Type? [Vanilla or DPDK]',
                    help='Enter either Vanilla or DPDK',
                    default='Vanilla',
                ),
                wiz.WizardStep(
                    id='mask',
                    name='Enter the CPU Mask for OVS to use',
                    help='Mask for OVS PMDs',
                    default='30',
                ),
            )
        )

    def vpp_wizard(self):
        """
        Wizard to collect VPP configuration
        """
        self.wiz_vpp = wiz.PromptWizard(
            name="Vswitch Configuration",
            description="Specific configurations of the virtual-Switch",
            steps=(
                wiz.WizardStep(
                    id='mode',
                    name='L2 Connection mode xconnect|bridge|l2patch to use?',
                    help='Select the l2 connection mode',
                    default='xconnect',
                ),
            )
        )

    def trex_wizard(self):
        """
        Wizard to collect Trex configuration
        """
        self.wiz_trex = wiz.PromptWizard(
            name="Trex Traffic Generator Configuration",
            description="Specific configurations of Trex TGen",
            steps=(
                wiz.WizardStep(
                    id='hostip',
                    name='What is IP address of the T-Rex Host?',
                    help='Enter the IP address of host where Trex is running',
                    validators=(wiz.required_validator)
                ),
                wiz.WizardStep(
                    id='user',
                    name='What is Usernameof the T-Rex Host?',
                    help='Enter the Username of host where Trex is running',
                    default='root',
                ),
                wiz.WizardStep(
                    id='bdir',
                    name='What is Dir where the T-Rex Binary resides?',
                    help='Enter the Location where Trex Binary is',
                    default='/root/trex_2.37/scripts/',
                ),
                wiz.WizardStep(
                    id='pci1',
                    name='What is PCI address of the port-1?',
                    help='Enter the PCI address of Data port 1',
                    validators=(wiz.required_validator)
                ),
                wiz.WizardStep(
                    id='pci2',
                    name='What is PCI address of the port-2?',
                    help='Enter the PCI address of Data port 2',
                    validators=(wiz.required_validator)
                ),
                wiz.WizardStep(
                    id='rate',
                    name='What is Line rate (in Gbps) of the ports?',
                    help='Enter the linerate of the ports',
                    default='10',
                ),
                wiz.WizardStep(
                    id='prom',
                    name='T-Rex Promiscuous enabled?',
                    help='Do you want to enable the Promiscuous mode?',
                    default='False',
                ),
                wiz.WizardStep(
                    id='lat',
                    name='Whats the Trex Latency PPS?',
                    help='Enter the Latency value in PPS',
                    default='1000',
                ),
                wiz.WizardStep(
                    id='bslv',
                    name='Do you want Binary Loss Verification Enabled?',
                    help='Enter True if you want it to be enabled.',
                    default='True',
                ),
                wiz.WizardStep(
                    id='maxrep',
                    name='If Loss Verification, what the max rep?',
                    help='If BSLV is enabled, whats the max repetition value?',
                    default='2',
                ),
            )
        )

    def stc_wizard(self):
        """
        Wizard to collect STC configuration
        """
        self.wiz_stc = wiz.PromptWizard(
            name="Spirent STC Traffic Generator Configuration",
            description="Specific configurations of Spirent-STC TGen",
            steps=(
                wiz.WizardStep(
                    id='lab',
                    name='Lab Server IP?',
                    help='Enter the IP of Lab Server',
                    default='10.10.120.244',
                ),
                wiz.WizardStep(
                    id='lisc',
                    name='License Server IP?',
                    help='Enter the IP of the License Server',
                    default='10.10.120.246',
                ),
                wiz.WizardStep(
                    id='eaddr',
                    name='East Port Chassis Address?',
                    help='IP address of the East-Port',
                    default='10.10.120.245',
                ),
                wiz.WizardStep(
                    id='eslot',
                    name='East Port Slot Number',
                    help='Slot Number of the East Port',
                    default='1',
                ),
                wiz.WizardStep(
                    id='eport',
                    name='Port Number of the East-Port',
                    help='Port Number for the East Port',
                    default='1',
                ),
                wiz.WizardStep(
                    id='eint',
                    name='East port Interface Address',
                    help='IP to use for East Port?',
                    default='192.85.1.3',
                ),
                wiz.WizardStep(
                    id='egw',
                    name='Gateway Address for East Port',
                    help='IP of the East-Port Gateway',
                    default='192.85.1.103',
                ),
                wiz.WizardStep(
                    id='waddr',
                    name='West Port Chassis Address?',
                    help='IP address of the West-Port',
                    default='10.10.120.245',
                ),
                wiz.WizardStep(
                    id='wslot',
                    name='West Port Slot Number',
                    help='Slot Number of the West Port',
                    default='1',
                ),
                wiz.WizardStep(
                    id='wport',
                    name='Port Number of the West-Port',
                    help='Port Number for the West Port',
                    default='2',
                ),
                wiz.WizardStep(
                    id='wint',
                    name='West port Interface Address',
                    help='IP to use for West Port?',
                    default='192.85.1.103',
                ),
                wiz.WizardStep(
                    id='wgw',
                    name='Gateway Address for West Port',
                    help='IP of the West-Port Gateway',
                    default='192.85.1.3',
                ),
                wiz.WizardStep(
                    id='script',
                    name='Name of the Script to use for RFC2544 Tests?',
                    help='Script Name to use for RFC 2544 Tests.',
                    default='testcenter-rfc2544-rest.py',
                ),
            )
        )

    def ixnet_wizard(self):
        """
        Wizard to collect ixnet configuration
        """
        self.wiz_ixnet = wiz.PromptWizard(
            name="Ixia IxNet Traffic Generator Configuration",
            description="Specific configurations of Ixia-Ixnet TGen",
            steps=(
                wiz.WizardStep(
                    id='card',
                    name='Card Number?',
                    help='Chassis Card Number',
                    default='1',
                ),
                wiz.WizardStep(
                    id='port1',
                    name='Port-1 Number?',
                    help='Chassis Port-1 Number',
                    default='5',
                ),
                wiz.WizardStep(
                    id='port2',
                    name='Port-2 Number?',
                    help='Chassis Port-2 Number',
                    default='6',
                ),
                wiz.WizardStep(
                    id='libp1',
                    name='IXIA Library path?',
                    help='Library path of Ixia',
                    default='/opt/ixnet/ixos-api/8.01.0.2/lib/ixTcl1.0',
                ),
                wiz.WizardStep(
                    id='libp2',
                    name='IXNET Library Path',
                    help='Library Path for the IXNET',
                    default='/opt/ixnet/ixnetwork/8.01.1029.6/lib/IxTclNetwork',
                ),
                wiz.WizardStep(
                    id='host',
                    name='IP of the CHassis?',
                    help='Chassis IP',
                    default='10.10.50.6',
                ),
                wiz.WizardStep(
                    id='machine',
                    name='IP of the API Server?',
                    help='API Server IP ',
                    default='10.10.120.6',
                ),
                wiz.WizardStep(
                    id='port',
                    name='Port of the API Server?',
                    help='API Server Port',
                    default='9127',
                ),
                wiz.WizardStep(
                    id='user',
                    name='Username for the API server?',
                    help='Username to use to connect to API Server',
                    default='vsperf_sandbox',
                ),
                wiz.WizardStep(
                    id='tdir',
                    name='Path for Results Directory on API Server',
                    help='Results Path on API Server',
                    default='c:/ixia_results/vsperf_sandbox',
                ),
                wiz.WizardStep(
                    id='rdir',
                    name='Path for Results directory on DUT',
                    help='DUT Results Path',
                    default='/mnt/ixia_results/vsperf_sandbox',
                ),
            )
        )

    def guest_wizard(self):
        """
        Wizard to collect guest configuration
        """
        self.wiz_guest = wiz.PromptWizard(
            name="Guest Configuration for PVP and PVVP Scenarios",
            description="Guest configurations",
            steps=(
                wiz.WizardStep(
                    id='image',
                    name='Enter the Path for the iamge',
                    help='Complete path where image resides',
                    default='/home/opnfv/vloop-vnf-ubuntu-14.04_20160823.qcow2',
                ),
                wiz.WizardStep(
                    id='mode',
                    name='Enter the forwarding mode to use',
                    help='one of io|mac|mac_retry|macswap|flowgen|rxonly|....',
                    default='io',
                ),
                wiz.WizardStep(
                    id='smp',
                    name='Number of SMP to use?',
                    help='While Spawning the guest, how many SMPs to use?',
                    default='2',
                ),
                wiz.WizardStep(
                    id='cores',
                    name="Guest Core binding. For 2 cores a & b: ['a', 'b']",
                    help='Enter the cores to use in the specified format',
                    default="['8', '9']",
                ),
            )
        )

############### All the Run Operations ######################

    def run_dutwiz(self):
        """
        Run the DUT wizard
        """
        self.dut_wizard()
        self.dut_values = self.wiz_dut.run(self.shell)

    def run_mainwiz(self):
        """
        Run the Main wizard
        """
        self.main_wizard()
        self.main_values = self.wiz_main.run(self.shell)
        print(self.main_values['nics'])

    def run_vswitchwiz(self):
        """
        Run the vSwitch wizard
        """
        if self.main_values['vswitch'] == "OVS":
            self.ovs_wizard()
            self.ovs_values = self.wiz_ovs.run(self.shell)
        elif self.main_values['vswitch'] == 'VPP':
            self.vpp_wizard()
            self.vpp_values = self.wiz_vpp.run(self.shell)

    def run_trafficwiz(self):
        """
        Run the Traffic wizard
        """
        self.traffic_wizard()
        self.traffic_values = self.wiz_traffic.run(self.shell)

    def run_tgenwiz(self):
        """
        Run the Tgen wizard
        """
        if self.main_values['tgen'] == "Trex":
            self.trex_wizard()
            self.trex_values = self.wiz_trex.run(self.shell)
        elif self.main_values['tgen'] == "TestCenter":
            self.stc_wizard()
            self.stc_values = self.wiz_stc.run(self.shell)
        elif self.main_values['tgen'] == 'IxNet':
            self.ixnet_wizard()
            self.ixnet_values = self.wiz_ixnet.run(self.shell)

    def run_guestwiz(self):
        """
        Run the Guest wizard
        """
        if self.main_values['guest'] == 'YES':
            self.guest_wizard()
            self.guest_values = self.wiz_guest.run(self.shell)

################ Prepare Configuration File ##################
    #pylint: disable=too-many-statements
    def prepare_conffile(self):
        """
        Create the Configuration file that can be used with VSPERF
        """
        with open("./vsperf.conf", 'w+') as ofile:
            ofile.write("#### This file is Automatically Created ####\n\n")
            if self.main_values['vswitch'] == "OVS":
                if self.ovs_values['type'] == "Vanilla":
                    ofile.write("VSWITCH = 'OvsVanilla'\n")
                else:
                    ofile.write("VSWITCH = 'OvsDpdkVhost'\n")
                    ofile.write("VSWITCH_PMD_CPU_MASK = '" +
                                self.ovs_values['mask'] + "'\n")
            else:
                ofile.write("VSWITCH = 'VppDpdkVhost'\n")
                ofile.write("VSWITCH_VPP_L2_CONNECT_MODE = '" +
                            self.vpp_values['mode'] + "'\n")
            nics = self.get_nics_string()
            wln = "WHITELIST_NICS = [" + nics + "]" + "\n"
            ofile.write(wln)
            ofile.write("RTE_TARGET = 'x86_64-native-linuxapp-gcc'")
            ofile.write("\n")
            ofile.write("TRAFFICGEN = " + "'" + self.main_values['tgen'] + "'")
            ofile.write("\n")
            ofile.write("VSWITCH_BRIDGE_NAME = 'vsperf-br0'")
            ofile.write("\n")
            ofile.write("TRAFFICGEN_DURATION = " +
                        self.traffic_values['duration'] + "\n")
            ofile.write("TRAFFICGEN_LOSSRATE = 0" + "\n")
            ofile.write("TRAFFICGEN_PKT_SIZES = (" +
                        self.traffic_values['pktsizes'] +
                        ")" + "\n")
            if self.main_values['tgen'] == "Trex":
                ofile.write("TRAFFICGEN_TREX_HOST_IP_ADDR = '" +
                            self.trex_values['hostip'] + "'" + "\n")
                ofile.write("TRAFFICGEN_TREX_USER = '" +
                            self.trex_values['user'] + "'" + "\n")
                ofile.write("TRAFFICGEN_TREX_BASE_DIR = '" +
                            self.trex_values['bdir'] + "'" + "\n")
                ofile.write("TRAFFICGEN_TREX_LINE_SPEED_GBPS = '" +
                            self.trex_values['rate'] + "'" + "\n")
                ofile.write("TRAFFICGEN_TREX_PORT1 = '" +
                            self.trex_values['pci1'] + "'" + "\n")
                ofile.write("TRAFFICGEN_TREX_PORT2 = '" +
                            self.trex_values['pci2'] + "'" + "\n")
                ofile.write("TRAFFICGEN_TREX_PROMISCUOUS = " +
                            self.trex_values['prom'] + "\n")
                ofile.write("TRAFFICGEN_TREX_LATENCY_PPS = " +
                            self.trex_values['lat'] + "\n")
                ofile.write("TRAFFICGEN_TREX_RFC2544_BINARY_SEARCH_LOSS_VERIFICATION = " +
                            self.trex_values['bslv'])
                ofile.write("TRAFFICGEN_TREX_MAX_REPEAT = " +
                            self.trex_values['maxrep'] + "\n")
            elif self.main_values['tgen'] == "TestCenter":
                ofile.write("TRAFFICGEN_STC_LAB_SERVER_ADDR = '" +
                            self.stc_values['lab'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_LICENSE_SERVER_ADDR = '" +
                            self.stc_values['lisc'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_EAST_CHASSIS_ADDR = '" +
                            self.stc_values['eaddr'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_EAST_SLOT_NUM = '" +
                            self.stc_values['eslot'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_EAST_PORT_NUM = '" +
                            self.stc_values['eport'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_EAST_INTF_ADDR = '" +
                            self.stc_values['eint'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_EAST_INTF_GATEWAY_ADDR = '" +
                            self.stc_values['egw'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_WEST_CHASSIS_ADDR = '" +
                            self.stc_values['waddr'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_WEST_SLOT_NUM = '" +
                            self.stc_values['wslot'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_WEST_PORT_NUM = '" +
                            self.stc_values['wport'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_WEST_INTF_ADDR = '" +
                            self.stc_values['wint'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_WEST_INTF_GATEWAY_ADDR = '" +
                            self.stc_values['wgw'] + "'" + "\n")
                ofile.write("TRAFFICGEN_STC_RFC2544_TPUT_TEST_FILE_NAME = '" +
                            self.stc_values['script'] + "'" + "\n")
            elif self.main_values['tgen'] == 'IxNet':
                print("IXIA Trafficgen")
                # Ixia/IxNet configuration
                ofile.write("TRAFFICGEN_IXIA_CARD = '" +
                            self.ixnet_values['card'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXIA_PORT1 = '" +
                            self.ixnet_values['port1'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXIA_PORT2 = '" +
                            self.ixnet_values['port2'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXIA_LIB_PATH = '" +
                            self.ixnet_values['libp1'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXNET_LIB_PATH = '" +
                            self.ixnet_values['libp2'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXIA_HOST = '" +
                            self.ixnet_values['host'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXNET_MACHINE = '" +
                            self.ixnet_values['machine'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXNET_PORT = '" +
                            self.ixnet_values['port'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXNET_USER = '" +
                            self.ixnet_values['user'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXNET_TESTER_RESULT_DIR = '" +
                            self.ixnet_values['tdir'] + "'" + "\n")
                ofile.write("TRAFFICGEN_IXNET_DUT_RESULT_DIR = '" +
                            self.ixnet_values['rdir'] + "'" + "\n")
            if self.main_values['guest'] == 'YES':
                ofile.write("GUEST_IMAGE = ['" +
                            self.guest_values['image'] + "']" + "\n")
                ofile.write("GUEST_TESTPMD_FWD_MODE = ['" +
                            self.guest_values['mode'] + "']" + "\n")
                ofile.write("GUEST_SMP = ['" +
                            self.guest_values['smp'] + "']" + "\n")
                ofile.write("GUEST_CORE_BINDING = [" +
                            self.guest_values['cores'] + ",]" + "\n")


def signal_handler(signum, frame):
    """
    Signal Handler
    """
    print("\n You interrupted, No File will be generated!")
    print(signum, frame)
    sys.exit(0)


def main():
    """
    The Main Function
    """
    try:
        vwiz = VsperfWizard()
        vwiz.run_dutwiz()
        vwiz.run_mainwiz()
        vwiz.run_vswitchwiz()
        vwiz.run_trafficwiz()
        vwiz.run_tgenwiz()
        vwiz.run_guestwiz()
        vwiz.prepare_conffile()
    except (KeyboardInterrupt, MemoryError):
        print("Some Error Occured, No file will be generated!")

    print("Thanks for using the VSPERF-WIZARD, Please look for vsperf.conf " +
          "file in the current folder")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
