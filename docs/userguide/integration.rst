.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

Integration tests
=================

VSPERF includes a set of integration tests defined in conf/integration.
These tests can be run by specifying --integration as a parameter to vsperf.
Current tests in conf/integration are Overlay tests.

VSPERF supports VXLAN, GRE and GENEVE tunneling protocols.
Testing of these protocols is limited to unidirectional traffic and
P2P (Physical to Physical scenarios).

NOTE: The configuration for overlay tests provided in this guide is for unidirectional traffic only.

Executing Tunnel encapsulation tests
------------------------------------

The VXLAN OVS DPDK encapsulation tests requires IPs, MAC addresses,
bridge names and WHITELIST_NICS for DPDK.

Default values are already provided. To customize for your environment, override
the following variables in you user_settings.py file:

  .. code-block:: python

    # Variables defined in conf/integration/02_vswitch.conf
    # Tunnel endpoint for Overlay P2P deployment scenario
    # used for br0
    VTEP_IP1 = '192.168.0.1/24'

    # Used as remote_ip in adding OVS tunnel port and
    # to set ARP entry in OVS (e.g. tnl/arp/set br-ext 192.168.240.10 02:00:00:00:00:02
    VTEP_IP2 = '192.168.240.10'

    # Network to use when adding a route for inner frame data
    VTEP_IP2_SUBNET = '192.168.240.0/24'

    # Bridge names
    TUNNEL_INTEGRATION_BRIDGE = 'br0'
    TUNNEL_EXTERNAL_BRIDGE = 'br-ext'

    # IP of br-ext
    TUNNEL_EXTERNAL_BRIDGE_IP = '192.168.240.1/24'

    # vxlan|gre|geneve
    TUNNEL_TYPE = 'vxlan'

    # Variables defined conf/integration/03_traffic.conf
    # For OP2P deployment scenario
    TRAFFICGEN_PORT1_MAC = '02:00:00:00:00:01'
    TRAFFICGEN_PORT2_MAC = '02:00:00:00:00:02'
    TRAFFICGEN_PORT1_IP = '1.1.1.1'
    TRAFFICGEN_PORT2_IP = '192.168.240.10'

To run VXLAN encapsulation tests:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=vxlan' overlay_p2p_tput

To run GRE encapsulation tests:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=gre' overlay_p2p_tput

To run GENEVE encapsulation tests:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=geneve' overlay_p2p_tput

To run OVS NATIVE tunnel tests (VXLAN/GRE/GENEVE):

1. Install the OVS kernel modules

  .. code:: console

    cd src/ovs/ovs
    sudo -E make modules_install

2. Set the following variables:

  .. code-block:: python

    VSWITCH = 'OvsVanilla'
    VSWITCH_VANILLA_PHY_PORT_NAMES = ['nic1name', 'nic2name']
    # Specify vport_* kernel module to test.
    VSWITCH_VANILLA_KERNEL_MODULES = ['vport_vxlan',
                                      'vport_gre',
                                      'vport_geneve',
                                      os.path.join(OVS_DIR_VANILLA,
                                      'datapath/linux/openvswitch.ko')]

3. Run tests:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=vxlan' overlay_p2p_tput


Executing VXLAN decapsulation tests
------------------------------------

To run VXLAN decapsulation tests:

1. Set the variables used in "Executing Tunnel encapsulation tests"

2. Set dstmac of DUT_NIC2_MAC to the MAC adddress of the 2nd NIC of your DUT

  .. code-block:: python

    DUT_NIC2_MAC = '<DUT NIC2 MAC>'

3. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration overlay_p2p_decap_cont

If you want to use different values for your VXLAN frame, you may set:

  .. code-block:: python

    VXLAN_FRAME_L3 = {'proto': 'udp',
                      'packetsize': 64,
                      'srcip': TRAFFICGEN_PORT1_IP,
                      'dstip': '192.168.240.1',
                     }
    VXLAN_FRAME_L4 = {'srcport': 4789,
                      'dstport': 4789,
                      'vni': VXLAN_VNI,
                      'inner_srcmac': '01:02:03:04:05:06',
                      'inner_dstmac': '06:05:04:03:02:01',
                      'inner_srcip': '192.168.0.10',
                      'inner_dstip': '192.168.240.9',
                      'inner_proto': 'udp',
                      'inner_srcport': 3000,
                      'inner_dstport': 3001,
                     }


Executing GRE decapsulation tests
---------------------------------

To run GRE decapsulation tests:

1. Set the variables used in "Executing Tunnel encapsulation tests"

2. Set dstmac of DUT_NIC2_MAC to the MAC adddress of the 2nd NIC of your DUT

  .. code-block:: python

    DUT_NIC2_MAC = '<DUT NIC2 MAC>'

3. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --test-params 'tunnel_type=gre'
             --integration overlay_p2p_decap_cont


If you want to use different values for your GRE frame, you may set:

  .. code-block:: python

    GRE_FRAME_L3 = {'proto': 'gre',
                    'packetsize': 64,
                    'srcip': TRAFFICGEN_PORT1_IP,
                    'dstip': '192.168.240.1',
                   }

    GRE_FRAME_L4 = {'srcport': 0,
                    'dstport': 0
                    'inner_srcmac': '01:02:03:04:05:06',
                    'inner_dstmac': '06:05:04:03:02:01',
                    'inner_srcip': '192.168.0.10',
                    'inner_dstip': '192.168.240.9',
                    'inner_proto': 'udp',
                    'inner_srcport': 3000,
                    'inner_dstport': 3001,
                   }


Executing GENEVE decapsulation tests
------------------------------------

IxNet 7.3X does not have native support of GENEVE protocol. The
template, GeneveIxNetTemplate.xml_ClearText.xml, should be imported
into IxNET for this testcase to work.

To import the template do:

1. Run the IxNetwork TCL Server
2. Click on the Traffic menu
3. Click on the Traffic actions and click Edit Packet Templates
4. On the Template editor window, click Import. Select the template
   tools/pkt_gen/ixnet/GeneveIxNetTemplate.xml_ClearText.xml
   and click import.
5. Restart the TCL Server.

To run GENEVE decapsulation tests:

1. Set the variables used in "Executing Tunnel encapsulation tests"

2. Set dstmac of DUT_NIC2_MAC to the MAC adddress of the 2nd NIC of your DUT

  .. code-block:: python

    DUT_NIC2_MAC = '<DUT NIC2 MAC>'

3. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --test-params 'tunnel_type=geneve'
             --integration overlay_p2p_decap_cont


If you want to use different values for your GENEVE frame, you may set:

  .. code-block:: python

    GENEVE_FRAME_L3 = {'proto': 'udp',
                       'packetsize': 64,
                       'srcip': TRAFFICGEN_PORT1_IP,
                       'dstip': '192.168.240.1',
                      }

    GENEVE_FRAME_L4 = {'srcport': 6081,
                       'dstport': 6081,
                       'geneve_vni': 0,
                       'inner_srcmac': '01:02:03:04:05:06',
                       'inner_dstmac': '06:05:04:03:02:01',
                       'inner_srcip': '192.168.0.10',
                       'inner_dstip': '192.168.240.9',
                       'inner_proto': 'udp',
                       'inner_srcport': 3000,
                       'inner_dstport': 3001,
                      }


Executing Native/Vanilla OVS VXLAN decapsulation tests
------------------------------------------------------

To run VXLAN decapsulation tests:

1. Set the following variables in your user_settings.py file:

  .. code-block:: python

    VSWITCH_VANILLA_KERNEL_MODULES = ['vport_vxlan',
                                      os.path.join(OVS_DIR_VANILLA,
                                      'datapath/linux/openvswitch.ko')]

    DUT_NIC1_MAC = '<DUT NIC1 MAC ADDRESS>'

    TRAFFICGEN_PORT1_IP = '172.16.1.2'
    TRAFFICGEN_PORT2_IP = '192.168.1.11'

    VTEP_IP1 = '172.16.1.2/24'
    VTEP_IP2 = '192.168.1.1'
    VTEP_IP2_SUBNET = '192.168.1.0/24'
    TUNNEL_EXTERNAL_BRIDGE_IP = '172.16.1.1/24'
    TUNNEL_INT_BRIDGE_IP = '192.168.1.1'

    VXLAN_FRAME_L2 = {'srcmac':
                      '01:02:03:04:05:06',
                      'dstmac': DUT_NIC1_MAC
                     }

    VXLAN_FRAME_L3 = {'proto': 'udp',
                      'packetsize': 64,
                      'srcip': TRAFFICGEN_PORT1_IP,
                      'dstip': '172.16.1.1',
                     }

    VXLAN_FRAME_L4 = {
                      'srcport': 4789,
                      'dstport': 4789,
                      'protocolpad': 'true',
                      'vni': 99,
                      'inner_srcmac': '01:02:03:04:05:06',
                      'inner_dstmac': '06:05:04:03:02:01',
                      'inner_srcip': '192.168.1.2',
                      'inner_dstip': TRAFFICGEN_PORT2_IP,
                      'inner_proto': 'udp',
                      'inner_srcport': 3000,
                      'inner_dstport': 3001,
                     }

2. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=vxlan' overlay_p2p_decap_cont

Executing Native/Vanilla OVS GRE decapsulation tests
----------------------------------------------------

To run GRE decapsulation tests:

1. Set the following variables in your user_settings.py file:

  .. code-block:: python

    VSWITCH_VANILLA_KERNEL_MODULES = ['vport_gre',
                                      os.path.join(OVS_DIR_VANILLA,
                                      'datapath/linux/openvswitch.ko')]

    DUT_NIC1_MAC = '<DUT NIC1 MAC ADDRESS>'

    TRAFFICGEN_PORT1_IP = '172.16.1.2'
    TRAFFICGEN_PORT2_IP = '192.168.1.11'

    VTEP_IP1 = '172.16.1.2/24'
    VTEP_IP2 = '192.168.1.1'
    VTEP_IP2_SUBNET = '192.168.1.0/24'
    TUNNEL_EXTERNAL_BRIDGE_IP = '172.16.1.1/24'
    TUNNEL_INT_BRIDGE_IP = '192.168.1.1'

    GRE_FRAME_L2 = {'srcmac':
                    '01:02:03:04:05:06',
                    'dstmac': DUT_NIC1_MAC
                   }

    GRE_FRAME_L3 = {'proto': 'udp',
                    'packetsize': 64,
                    'srcip': TRAFFICGEN_PORT1_IP,
                    'dstip': '172.16.1.1',
                   }

    GRE_FRAME_L4 = {
                    'srcport': 4789,
                    'dstport': 4789,
                    'protocolpad': 'true',
                    'inner_srcmac': '01:02:03:04:05:06',
                    'inner_dstmac': '06:05:04:03:02:01',
                    'inner_srcip': '192.168.1.2',
                    'inner_dstip': TRAFFICGEN_PORT2_IP,
                    'inner_proto': 'udp',
                    'inner_srcport': 3000,
                    'inner_dstport': 3001,
                   }

2. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=gre' overlay_p2p_decap_cont

Executing Native/Vanilla OVS GENEVE decapsulation tests
-------------------------------------------------------

To run GENEVE decapsulation tests:

1. Set the following variables in your user_settings.py file:

  .. code-block:: python

    VSWITCH_VANILLA_KERNEL_MODULES = ['vport_geneve',
                                      os.path.join(OVS_DIR_VANILLA,
                                      'datapath/linux/openvswitch.ko')]

    DUT_NIC1_MAC = '<DUT NIC1 MAC ADDRESS>'

    TRAFFICGEN_PORT1_IP = '172.16.1.2'
    TRAFFICGEN_PORT2_IP = '192.168.1.11'

    VTEP_IP1 = '172.16.1.2/24'
    VTEP_IP2 = '192.168.1.1'
    VTEP_IP2_SUBNET = '192.168.1.0/24'
    TUNNEL_EXTERNAL_BRIDGE_IP = '172.16.1.1/24'
    TUNNEL_INT_BRIDGE_IP = '192.168.1.1'

    GENEVE_FRAME_L2 = {'srcmac':
                       '01:02:03:04:05:06',
                       'dstmac': DUT_NIC1_MAC
                      }

    GENEVE_FRAME_L3 = {'proto': 'udp',
                       'packetsize': 64,
                       'srcip': TRAFFICGEN_PORT1_IP,
                       'dstip': '172.16.1.1',
                      }

    GENEVE_FRAME_L4 = {'srcport': 6081,
                       'dstport': 6081,
                       'protocolpad': 'true',
                       'geneve_vni': 0,
                       'inner_srcmac': '01:02:03:04:05:06',
                       'inner_dstmac': '06:05:04:03:02:01',
                       'inner_srcip': '192.168.1.2',
                       'inner_dstip': TRAFFICGEN_PORT2_IP,
                       'inner_proto': 'udp',
                       'inner_srcport': 3000,
                       'inner_dstport': 3001,
                      }

2. Run test:

  .. code-block:: console

    ./vsperf --conf-file user_settings.py --integration
             --test-params 'tunnel_type=geneve' overlay_p2p_decap_cont

