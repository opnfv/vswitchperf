Integration tests
=================

Executing Tunnel encapsulation tests
------------------------------------

VSPERF supports VXLAN, GRE and GENEVE tunneling protocols.
Testing of these protocols is limited to unidirectional traffic and
P2P (Physical to Physical scenarios).

To run VXLAN encapsulation tests:

  .. code-block:: console

     ./vsperf --conf-file user_settings.py --run-integration --test-param 'tunnel_type=vxlan' overlay_p2p_tput

To run GRE encapsulation tests:

  .. code-block:: console

     ./vsperf --conf-file user_settings.py --run-integration --test-param 'tunnel_type=gre' overlay_p2p_tput

To run GENEVE encapsulation tests:

  .. code-block:: console

     ./vsperf --conf-file user_settings.py --run-integration --test-param 'tunnel_type=geneve' overlay_p2p_tput

To run OVS NATIVE tunnel tests (VXLAN/GRE/GENEVE):

1. Install the OVS kernel modules

  .. code:: console

     cd src/ovs/ovs
     sudo -E make modules_install

2. Set the following variables:

  .. code-block:: console

   VSWITCH = 'OvsVanilla'
   VSWITCH_VANILLA_PHY_PORT_NAMES = ['nic1name', 'nic2name']
   # Specify vport_* kernel module to test.
   VSWITCH_VANILLA_KERNEL_MODULES = ['vport_vxlan',
                                     'vport_gre',
                                     'vport_geneve',
                                     os.path.join(OVS_DIR_VANILLA, 'datapath/linux/openvswitch.ko')]

3. Run tests:

  .. code-block:: console

     ./vsperf --conf-file user_settings.py --run-integration --test-param 'tunnel_type=vxlan' overlay_p2p_tput


Executing VXLAN decapsulation tests
------------------------------------

To run VXLAN decapsulation tests:

1. Set IXNET_TCL_SCRIPT, VXLAN_FRAME_L2 and VLXAN_FRAME_L3 of your settings file to:

  .. code-block:: console

   IXNET_TCL_SCRIPT='ixnetrfc2544v2.tcl'

   VXLAN_FRAME_L2 = {'srcmac':
                     '01:02:03:04:05:06',
                     'dstmac':
                     '<DUT's NIC1 MAC>',
                     'srcport': 4789,
                     'dstport': 4789}

   VXLAN_FRAME_L3 = {'proto': 'udp',
                     'packetsize': 64,
                     'srcip': '1.1.1.1',
                     'dstip': '192.168.240.1',
                     'vni': VXLAN_VNI,
                     'inner_srcmac': '01:02:03:04:05:06',
                     'inner_dstmac': '06:05:04:03:02:01',
                     'inner_srcip': '192.168.0.10',
                     'inner_dstip': '192.168.240.9',
                     'inner_proto': 'udp',
                     'inner_srcport': 3000,
                     'inner_dstport': 3001,
                    }

2. Run test:

  .. code-block:: console

     ./vsperf --conf-file user_settings.py --run-integration overlay_p2p_decap_cont


Executing GRE decapsulation tests
---------------------------------

To run GRE decapsulation tests:

1. Set IXNET_TCL_SCRIPT, VXLAN_FRAME_L2 and VLXAN_FRAME_L3 of your settings file to:

  .. code-block:: console

   IXNET_TCL_SCRIPT='ixnetrfc2544v2.tcl'

   VXLAN_FRAME_L2 = {'srcmac':
                     '01:02:03:04:05:06',
                     'dstmac':
                     '<DUT's NIC1 MAC>',
                     'srcport': 4789,
                     'dstport': 4789}

   VXLAN_FRAME_L3 = {'proto': 'gre',
                     'packetsize': 64,
                     'srcip': '1.1.1.1',
                     'dstip': '192.168.240.1',
                     'inner_srcmac': '01:02:03:04:05:06',
                     'inner_dstmac': '06:05:04:03:02:01',
                     'inner_srcip': '192.168.0.10',
                     'inner_dstip': '192.168.240.9',
                     'inner_proto': 'udp',
                     'inner_srcport': 3000,
                     'inner_dstport': 3001,
                    }

2. Run test:

  .. code-block:: console

     ./vsperf --conf-file user_settings.py --test-param 'tunnel_type=gre' --run-integration overlay_p2p_decap_cont

