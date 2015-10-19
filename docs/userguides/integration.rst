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


