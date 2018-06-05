Traffic Capture
---------------

Tha ability to capture traffic at multiple points of the system is crucial to
many of the functional tests. It allows the verification of functionality for
both the vSwitch and the NICs using hardware acceleration for packet
manipulation and modification.

There are three different methods of traffic capture supported by VSPERF.
Detailed descriptions of these methods as well as their pros and cons can be
found in the following chapters.

Traffic Capture inside of a VM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method uses the standard PVP scenario, in which vSwitch first processes
and modifies the packet before forwarding it to the VM. Inside of the VM we
capture the traffic using **tcpdump** or a similiar technique. The capture
information is the used to verify the expected modifications to the packet done
by vSwitch.

.. code-block:: console

                                                            _
       +--------------------------------------------------+  |
       |                                                  |  |
       |   +------------------------------------------+   |  |
       |   |  Traffic capture and Packet Forwarding   |   |  |
       |   +------------------------------------------+   |  |
       |          ^                            :          |  |
       |          |                            |          |  |  Guest
       |          :                            v          |  |
       |   +---------------+          +---------------+   |  |
       |   | logical port 0|          | logical port 1|   |  |
       +---+---------------+----------+---------------+---+ _|
                   ^                          :
                   |                          |
                   :                          v            _
       +---+---------------+----------+---------------+---+  |
       |   | logical port 0|          | logical port 1|   |  |
       |   +---------------+          +---------------+   |  |
       |           ^                          :           |  |
       |           |                          |           |  |  Host
       |           :                          v           |  |
       |   +--------------+            +--------------+   |  |
       |   |   phy port   |  vSwitch   |   phy port   |   |  |
       +---+--------------+------------+--------------+---+ _|
                   ^                          :
                   |                          |
                   :                          v
       +--------------------------------------------------+
       |                                                  |
       |                traffic generator                 |
       |                                                  |
       +--------------------------------------------------+

PROS:

- supports testing with all traffic generators
- easy to use and implement into test
- allows testing hardware offloading on the ingress side

CONS:

- does not allow testing hardware offloading on the egress side

An example of Traffic Capture in VM test:

.. code-block:: python

    # Capture Example 1 - Traffic capture inside VM (PVP scenario)
    # This TestCase will modify VLAN ID set by the traffic generator to the new value.
    # Correct VLAN ID settings is verified by inspection of captured frames.
    {
        Name: capture_pvp_modify_vid,
        Deployment: pvp,
        Description: Test and verify VLAN ID modification by Open vSwitch,
        Parameters : {
            VSWITCH : OvsDpdkVhost, # works also for Vanilla OVS
            TRAFFICGEN_DURATION : 5,
            TRAFFIC : {
                traffic_type : rfc2544_continuous,
                frame_rate : 100,
                'vlan': {
                    'enabled': True,
                    'id': 8,
                    'priority': 1,
                    'cfi': 0,
                },
            },
            GUEST_LOOPBACK : ['linux_bridge'],
        },
        TestSteps: [
            # replace original flows with vlan ID modification
            ['!vswitch', 'add_flow', '$VSWITCH_BRIDGE_NAME', {'in_port': '1', 'actions': ['mod_vlan_vid:4','output:3']}],
            ['!vswitch', 'add_flow', '$VSWITCH_BRIDGE_NAME', {'in_port': '2', 'actions': ['mod_vlan_vid:4','output:4']}],
            ['vswitch', 'dump_flows', '$VSWITCH_BRIDGE_NAME'],
            # verify that received frames have modified vlan ID
            ['VNF0', 'execute_and_wait', 'tcpdump -i eth0 -c 5 -w dump.pcap vlan 4 &'],
            ['trafficgen', 'send_traffic',{}],
            ['!VNF0', 'execute_and_wait', 'tcpdump -qer dump.pcap vlan 4 2>/dev/null | wc -l','|^(\d+)$'],
            ['tools', 'assert', '#STEP[-1][0] == 5'],
        ],
    },

Traffic Capture for testing NICs with HW offloading/acceleration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The NIC with hardware acceleration/offloading is inserted as an additional card
into the server. Two ports on this card are then connected together using
a patch cable as shown in the diagram. Only a single port of the tested NIC is
setup with DPDK acceleration, while the other is handled by the Linux Ip stack
allowing for traffic capture. The two NICs are then connected by vSwitch so the
original card can forward the processed packets to the traffic generator. The
ports handled by Linux IP stack allow for capturing packets, which are then
analyzed for changes done by both the vSwitch and the NIC with hardware
acceleration.

.. code-block:: console

                                                       _
    +------------------------------------------------+  |
    |                                                |  |
    |   +----------------------------------------+   |  |
    |   |                 vSwitch                |   |  |
    |   |  +----------------------------------+  |   |  |
    |   |  |                                  |  |   |  |
    |   |  |       +------------------+       |  |   |  |
    |   |  |       |                  |       v  |   |  |
    |   +----------------------------------------+   |  |  Device under Test
    |      ^       |                  ^       |      |  |
    |      |       |                  |       |      |  |
    |      |       v                  |       v      |  |
    |   +--------------+          +--------------+   |  |
    |   |              |          | NIC w HW acc |   |  |
    |   |   phy ports  |          |   phy ports  |   |  |
    +---+--------------+----------+--------------+---+ _|
           ^       :                  ^       :
           |       |                  |       |
           |       |                  +-------+
           :       v                 Patch Cable
    +------------------------------------------------+
    |                                                |
    |                traffic generator               |
    |                                                |
    +------------------------------------------------+

PROS:

- allows testing hardware offloading on both the ingress and egress side
- supports testing with all traffic generators
- relatively easy to use and implement into tests

CONS:

- a more complex setup with two cards
- if the tested card only has one port, an additional card is needed

An example of Traffic Capture for testing NICs with HW offloading test:

.. code-block:: python

    # Capture Example 2 - Setup with 2 NICs, where traffic is captured after it is
    # processed by NIC under the test (2nd NIC). See documentation for further details.
    # This TestCase will strip VLAN headers from traffic sent by the traffic generator.
    # The removal of VLAN headers is verified by inspection of captured frames.
    #
    # NOTE: This setup expects a DUT with two NICs with two ports each. First NIC is
    # connected to the traffic generator (standard VSPERF setup). Ports of a second NIC
    # are interconnected by a patch cable. PCI addresses of all four ports have to be
    # properly configured in the WHITELIST_NICS parameter.
    {
        Name: capture_p2p2p_strip_vlan_ovs,
        Deployment: clean,
        Description: P2P Continuous Stream,
        Parameters : {
            _CAPTURE_P2P2P_OVS_ACTION : 'strip_vlan',
            TRAFFIC : {
                bidir : False,
                traffic_type : rfc2544_continuous,
                frame_rate : 100,
                'l2': {
                    'srcmac': ca:fe:00:00:00:00,
                    'dstmac': 00:00:00:00:00:01
                },
                'vlan': {
                    'enabled': True,
                    'id': 8,
                    'priority': 1,
                    'cfi': 0,
                },
            },
            # suppress DPDK configuration, so physical interfaces are not bound to DPDK driver
            'WHITELIST_NICS' : [],
            'NICS' : [],
        },
        TestSteps: _CAPTURE_P2P2P_SETUP + [
            # capture traffic after processing by NIC under the test (after possible egress HW offloading)
            ['tools', 'exec_shell_background', 'tcpdump -i [2][device] -c 5 -w capture.pcap '
                                               'ether src [l2][srcmac]'],
            ['trafficgen', 'send_traffic', {}],
            ['vswitch', 'dump_flows', '$VSWITCH_BRIDGE_NAME'],
            ['vswitch', 'dump_flows', 'br1'],
            # there must be 5 captured frames...
            ['tools', 'exec_shell', 'tcpdump -r capture.pcap | wc -l', '|^(\d+)$'],
            ['tools', 'assert', '#STEP[-1][0] == 5'],
            # ...but no vlan headers
            ['tools', 'exec_shell', 'tcpdump -r capture.pcap vlan | wc -l', '|^(\d+)$'],
            ['tools', 'assert', '#STEP[-1][0] == 0'],
        ],
    },


Traffic Capture on the Traffic Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the functionality of the Traffic generator makes it possible to configure
Traffic Capture on both it's ports. With Traffic Capture enabled, VSPERF
instructs the Traffic Generator to automatically export captured data into
a pcap file. The captured packets are then sent to VSPERF for analysis and
verification, monitoring any changes done by both vSwitch and the NICs.

Vsperf currently only supports this functionality with the **T-Rex** generator.

.. code-block:: console

                                                            _
       +--------------------------------------------------+  |
       |                                                  |  |
       |           +--------------------------+           |  |
       |           |                          |           |  |
       |           |                          v           |  |  Host
       |   +--------------+            +--------------+   |  |
       |   |   phy port   |  vSwitch   |   phy port   |   |  |
       +---+--------------+------------+--------------+---+ _|
                   ^                          :
                   |                          |
                   :                          v
       +--------------------------------------------------+
       |                                                  |
       |                traffic generator                 |
       |                                                  |
       +--------------------------------------------------+

PROS:

- allows testing hardware offloading on both the ingress and egress side
- does not require an additional NIC

CONS:

- currently only supported by **T-Rex** traffic generator

An example Traffic Capture on the Traffic Generator test:

.. code-block:: python


    # Capture Example 3 - Traffic capture by traffic generator.
    # This TestCase uses OVS flow to add VLAN tag with given ID into every
    # frame send by traffic generator. Correct frame modificaiton is verified by
    # inspection of packet capture received by T-Rex.
    {
        Name: capture_p2p_add_vlan_ovs_trex,
        Deployment: clean,
        Description: OVS: Test VLAN tag modification and verify it by traffic capture,
        vSwitch : OvsDpdkVhost, # works also for Vanilla OVS
        Parameters : {
            TRAFFICGEN : Trex,
            TRAFFICGEN_DURATION : 5,
            TRAFFIC : {
                traffic_type : rfc2544_continuous,
                frame_rate : 100,
                # enable capture of five RX frames
                'capture': {
                    'enabled': True,
                    'tx_ports' : [],
                    'rx_ports' : [1],
                    'count' : 5,
                },
            },
        },
        TestSteps : STEP_VSWITCH_P2P_INIT + [
            # replace standard L2 flows by flows, which will add VLAN tag with ID 3
            ['!vswitch', 'add_flow', 'int_br0', {'in_port': '1', 'actions': ['mod_vlan_vid:3','output:2']}],
            ['!vswitch', 'add_flow', 'int_br0', {'in_port': '2', 'actions': ['mod_vlan_vid:3','output:1']}],
            ['vswitch', 'dump_flows', 'int_br0'],
            ['trafficgen', 'send_traffic', {}],
            ['trafficgen', 'get_results'],
            # verify that captured frames have vlan tag with ID 3
            ['tools', 'exec_shell', 'tcpdump -qer /#STEP[-1][0][capture_rx] vlan 3 '
                                    '2>/dev/null | wc -l', '|^(\d+)$'],
            # number of received frames with expected VLAN id must match the number of captured frames
            ['tools', 'assert', '#STEP[-1][0] == 5'],
        ] + STEP_VSWITCH_P2P_FINIT,
    },

