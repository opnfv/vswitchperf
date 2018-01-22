.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

******************************
VSPERF LEVEL TEST DESIGN (LTD)
******************************

.. 3.1

============
Introduction
============

The intention of this Level Test Design (LTD) document is to specify the set of
tests to carry out in order to objectively measure the current characteristics
of a virtual switch in the Network Function Virtualization Infrastructure
(NFVI) as well as the test pass criteria. The detailed test cases will be
defined in details-of-LTD_, preceded by the doc-id-of-LTD_ and the scope-of-LTD_.

This document is currently in draft form.

.. 3.1.1


.. _doc-id-of-LTD:

Document identifier
===================

The document id will be used to uniquely
identify versions of the LTD. The format for the document id will be:
OPNFV\_vswitchperf\_LTD\_REL\_STATUS, where by the
status is one of: draft, reviewed, corrected or final. The document id
for this version of the LTD is:
OPNFV\_vswitchperf\_LTD\_Brahmaputra\_REVIEWED.

.. 3.1.2

.. _scope-of-LTD:

Scope
=====

The main purpose of this project is to specify a suite of
performance tests in order to objectively measure the current packet
transfer characteristics of a virtual switch in the NFVI. The intent of
the project is to facilitate testing of any virtual switch. Thus, a
generic suite of tests shall be developed, with no hard dependencies to
a single implementation. In addition, the test case suite shall be
architecture independent.

The test cases developed in this project shall not form part of a
separate test framework, all of these tests may be inserted into the
Continuous Integration Test Framework and/or the Platform Functionality
Test Framework - if a vSwitch becomes a standard component of an OPNFV
release.

.. 3.1.3

References
==========

*  `RFC 1242 Benchmarking Terminology for Network Interconnection
   Devices <http://www.ietf.org/rfc/rfc1242.txt>`__
*  `RFC 2544 Benchmarking Methodology for Network Interconnect
   Devices <http://www.ietf.org/rfc/rfc2544.txt>`__
*  `RFC 2285 Benchmarking Terminology for LAN Switching
   Devices <http://www.ietf.org/rfc/rfc2285.txt>`__
*  `RFC 2889 Benchmarking Methodology for LAN Switching
   Devices <http://www.ietf.org/rfc/rfc2889.txt>`__
*  `RFC 3918 Methodology for IP Multicast
   Benchmarking <http://www.ietf.org/rfc/rfc3918.txt>`__
*  `RFC 4737 Packet Reordering
   Metrics <http://www.ietf.org/rfc/rfc4737.txt>`__
*  `RFC 5481 Packet Delay Variation Applicability
   Statement <http://www.ietf.org/rfc/rfc5481.txt>`__
*  `RFC 6201 Device Reset
   Characterization <http://tools.ietf.org/html/rfc6201>`__

.. 3.2

.. _details-of-LTD:

================================
Details of the Level Test Design
================================

This section describes the features to be tested (FeaturesToBeTested-of-LTD_), and
identifies the sets of test cases or scenarios (TestIdentification-of-LTD_).

.. 3.2.1

.. _FeaturesToBeTested-of-LTD:

Features to be tested
=====================

Characterizing virtual switches (i.e. Device Under Test (DUT) in this document)
includes measuring the following performance metrics:

- Throughput
- Packet delay
- Packet delay variation
- Packet loss
- Burst behaviour
- Packet re-ordering
- Packet correctness
- Availability and capacity of the DUT

.. 3.2.2

.. _TestIdentification-of-LTD:

Test identification
===================

.. 3.2.2.1

Throughput tests
----------------

The following tests aim to determine the maximum forwarding rate that
can be achieved with a virtual switch. The list is not exhaustive but
should indicate the type of tests that should be required. It is
expected that more will be added.

.. 3.2.2.1.1

.. _PacketLossRatio:

Test ID: LTD.Throughput.RFC2544.PacketLossRatio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2544 X% packet loss ratio Throughput and Latency Test

    **Prerequisite Test**: N/A

    **Priority**:

    **Description**:

    This test determines the DUT's maximum forwarding rate with X% traffic
    loss for a constant load (fixed length frames at a fixed interval time).
    The default loss percentages to be tested are: - X = 0% - X = 10^-7%

    Note: Other values can be tested if required by the user.

    The selected frame sizes are those previously defined under
    :ref:`default-test-parameters`.
    The test can also be used to determine the average latency of the traffic.

    Under the `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__
    test methodology, the test duration will
    include a number of trials; each trial should run for a minimum period
    of 60 seconds. A binary search methodology must be applied for each
    trial to obtain the final result.

    **Expected Result**: At the end of each trial, the presence or absence
    of loss determines the modification of offered load for the next trial,
    converging on a maximum rate, or
    `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__ Throughput with X%
    loss.
    The Throughput load is re-used in related
    `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__ tests and other
    tests.

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The maximum forwarding rate in Frames Per Second (FPS) and Mbps of
       the DUT for each frame size with X% packet loss.
    -  The average latency of the traffic flow when passing through the DUT
       (if testing for latency, note that this average is different from the
       test specified in Section 26.3 of
       `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__).
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

.. 3.2.2.1.2

.. _PacketLossRatioFrameModification:

Test ID: LTD.Throughput.RFC2544.PacketLossRatioFrameModification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2544 X% packet loss Throughput and Latency Test with
    packet modification

    **Prerequisite Test**: N/A

    **Priority**:

    **Description**:

    This test determines the DUT's maximum forwarding rate with X% traffic
    loss for a constant load (fixed length frames at a fixed interval time).
    The default loss percentages to be tested are: - X = 0% - X = 10^-7%

    Note: Other values can be tested if required by the user.

    The selected frame sizes are those previously defined under
    :ref:`default-test-parameters`.
    The test can also be used to determine the average latency of the traffic.

    Under the `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__
    test methodology, the test duration will
    include a number of trials; each trial should run for a minimum period
    of 60 seconds. A binary search methodology must be applied for each
    trial to obtain the final result.

    During this test, the DUT must perform the following operations on the
    traffic flow:

    -  Perform packet parsing on the DUT's ingress port.
    -  Perform any relevant address look-ups on the DUT's ingress ports.
    -  Modify the packet header before forwarding the packet to the DUT's
       egress port. Packet modifications include:

       -  Modifying the Ethernet source or destination MAC address.
       -  Modifying/adding a VLAN tag. (**Recommended**).
       -  Modifying/adding a MPLS tag.
       -  Modifying the source or destination ip address.
       -  Modifying the TOS/DSCP field.
       -  Modifying the source or destination ports for UDP/TCP/SCTP.
       -  Modifying the TTL.

    **Expected Result**: The Packet parsing/modifications require some
    additional degree of processing resource, therefore the
    `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__
    Throughput is expected to be somewhat lower than the Throughput level
    measured without additional steps. The reduction is expected to be
    greatest on tests with the smallest packet sizes (greatest header
    processing rates).

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The maximum forwarding rate in Frames Per Second (FPS) and Mbps of
       the DUT for each frame size with X% packet loss and packet
       modification operations being performed by the DUT.
    -  The average latency of the traffic flow when passing through the DUT
       (if testing for latency, note that this average is different from the
       test specified in Section 26.3 of
       `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__).
    -  The `RFC5481 <https://www.rfc-editor.org/rfc/rfc5481.txt>`__
       PDV form of delay variation on the traffic flow,
       using the 99th percentile.
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

.. 3.2.2.1.3

Test ID: LTD.Throughput.RFC2544.Profile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2544 Throughput and Latency Profile

    **Prerequisite Test**: N/A

    **Priority**:

    **Description**:

    This test reveals how throughput and latency degrades as the offered
    rate varies in the region of the DUT's maximum forwarding rate as
    determined by LTD.Throughput.RFC2544.PacketLossRatio (0% Packet Loss).
    For example it can be used to determine if the degradation of throughput
    and latency as the offered rate increases is slow and graceful or sudden
    and severe.

    The selected frame sizes are those previously defined under
    :ref:`default-test-parameters`.

    The offered traffic rate is described as a percentage delta with respect
    to the DUT's RFC 2544 Throughput as determined by
    LTD.Throughput.RFC2544.PacketLoss Ratio (0% Packet Loss case). A delta
    of 0% is equivalent to an offered traffic rate equal to the RFC 2544
    Maximum Throughput; A delta of +50% indicates an offered rate half-way
    between the Maximum RFC2544 Throughput and line-rate, whereas a delta of
    -50% indicates an offered rate of half the RFC 2544 Maximum Throughput.
    Therefore the range of the delta figure is natuarlly bounded at -100%
    (zero offered traffic) and +100% (traffic offered at line rate).

    The following deltas to the maximum forwarding rate should be applied:

    -  -50%, -10%, 0%, +10% & +50%

    **Expected Result**: For each packet size a profile should be produced
    of how throughput and latency vary with offered rate.

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The forwarding rate in Frames Per Second (FPS) and Mbps of the DUT
       for each delta to the maximum forwarding rate and for each frame
       size.
    -  The average latency for each delta to the maximum forwarding rate and
       for each frame size.
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.
    -  Any failures experienced (for example if the vSwitch crashes, stops
       processing packets, restarts or becomes unresponsive to commands)
       when the offered load is above Maximum Throughput MUST be recorded
       and reported with the results.

.. 3.2.2.1.4

Test ID: LTD.Throughput.RFC2544.SystemRecoveryTime
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2544 System Recovery Time Test

    **Prerequisite Test** LTD.Throughput.RFC2544.PacketLossRatio

    **Priority**:

    **Description**:

    The aim of this test is to determine the length of time it takes the DUT
    to recover from an overload condition for a constant load (fixed length
    frames at a fixed interval time). The selected frame sizes are those
    previously defined under :ref:`default-test-parameters`,
    traffic should be sent to the DUT under normal conditions. During the
    duration of the test and while the traffic flows are passing though the
    DUT, at least one situation leading to an overload condition for the DUT
    should occur. The time from the end of the overload condition to when
    the DUT returns to normal operations should be measured to determine
    recovery time. Prior to overloading the DUT, one should record the
    average latency for 10,000 packets forwarded through the DUT.

    The overload condition SHOULD be to transmit traffic at a very high
    frame rate to the DUT (150% of the maximum 0% packet loss rate as
    determined by LTD.Throughput.RFC2544.PacketLossRatio or line-rate
    whichever is lower), for at least 60 seconds, then reduce the frame rate
    to 75% of the maximum 0% packet loss rate. A number of time-stamps
    should be recorded: - Record the time-stamp at which the frame rate was
    reduced and record a second time-stamp at the time of the last frame
    lost. The recovery time is the difference between the two timestamps. -
    Record the average latency for 10,000 frames after the last frame loss
    and continue to record average latency measurements for every 10,000
    frames, when latency returns to within 10% of pre-overload levels record
    the time-stamp.

    **Expected Result**:

    **Metrics collected**

    The following are the metrics collected for this test:

    -  The length of time it takes the DUT to recover from an overload
       condition.
    -  The length of time it takes the DUT to recover the average latency to
       pre-overload conditions.

    **Deployment scenario**:

    -  Physical → virtual switch → physical.

.. 3.2.2.1.5

.. _BackToBackFrames:

Test ID: LTD.Throughput.RFC2544.BackToBackFrames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC2544 Back To Back Frames Test

    **Prerequisite Test**: N

    **Priority**:

    **Description**:

    The aim of this test is to characterize the ability of the DUT to
    process back-to-back frames. For each frame size previously defined
    under :ref:`default-test-parameters`, a burst of traffic
    is sent to the DUT with the minimum inter-frame gap between each frame.
    If the number of received frames equals the number of frames that were
    transmitted, the burst size should be increased and traffic is sent to
    the DUT again. The value measured is the back-to-back value, that is the
    maximum burst size the DUT can handle without any frame loss. Please note
    a trial must run for a minimum of 2 seconds and should be repeated 50
    times (at a minimum).

    **Expected Result**:

    Tests of back-to-back frames with physical devices have produced
    unstable results in some cases. All tests should be repeated in multiple
    test sessions and results stability should be examined.

    **Metrics collected**

    The following are the metrics collected for this test:

    -  The average back-to-back value across the trials, which is
       the number of frames in the longest burst that the DUT will
       handle without the loss of any frames.
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

    **Deployment scenario**:

    -  Physical → virtual switch → physical.

.. 3.2.2.1.6

Test ID: LTD.Throughput.RFC2889.MaxForwardingRateSoak
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2889 X% packet loss Max Forwarding Rate Soak Test

    **Prerequisite Tests**:

    LTD.Throughput.RFC2544.PacketLossRatio will determine the offered load and
    frame size for which the maximum theoretical throughput of the interface
    has not been achieved. As described in RFC 2544 section 24, the final
    determination of the benchmark SHOULD be conducted using a full length
    trial, and for this purpose the duration is 5 minutes with zero loss ratio.

    It is also essential to verify that the Traffic Generator has sufficient
    stability to conduct Soak tests. Therefore, a prerequisite is to perform
    this test with the DUT removed and replaced with a cross-over cable (or
    other equivalent very low overhead method such as a loopback in a HW switch),
    so that the traffic generator (and any other network involved) can be tested
    over the Soak period. Note that this test may be challenging for software-
    based traffic generators.

    **Priority**:

    **Description**:

    The aim of this test is to understand the Max Forwarding Rate stability
    over an extended test duration in order to uncover any outliers. To allow
    for an extended test duration, the test should ideally run for 24 hours
    or if this is not possible, for at least 6 hours.

    For this test, one frame size must be sent at the highest frame rate with
    X% packet loss ratio, as determined in the prerequisite test (a short trial).
    The loss ratio shall be measured and recorded every 5 minutes during the test
    (it may be sufficient to collect lost frame counts and divide by the number 
    of frames sent in 5 minutes to see if a threshold has been crossed, 
    and accept some small inaccuracy in the threshold evaluation, not the result).
    The default loss ratio is X = 0% and loss ratio > 10^-7% is the default
    threshold to terminate the test early (or inform the test operator of
    the failure status).

    Note: Other values of X and loss threshold can be tested if required by the user.

    **Expected Result**:

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  Max Forwarding Rate stability of the DUT.

       -  This means reporting the number of packets lost per time interval
          and reporting any time intervals with packet loss. The
          `RFC2889 <https://www.rfc-editor.org/rfc/rfc2289.txt>`__
          Forwarding Rate shall be measured in each interval.
          An interval of 300s is suggested.

    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.
    -  The `RFC5481 <https://www.rfc-editor.org/rfc/rfc5481.txt>`__
       PDV form of delay variation on the traffic flow,
       using the 99th percentile, may also be collected.

.. 3.2.2.1.7

Test ID: LTD.Throughput.RFC2889.MaxForwardingRateSoakFrameModification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2889 Max Forwarding Rate Soak Test with Frame Modification

    **Prerequisite Test**:

    LTD.Throughput.RFC2544.PacketLossRatioFrameModification (0% Packet Loss)
    will determine the offered load and
    frame size for which the maximum theoretical throughput of the interface
    has not been achieved. As described in RFC 2544 section 24, the final
    determination of the benchmark SHOULD be conducted using a full length
    trial, and for this purpose the duration is 5 minutes with zero loss ratio.

    It is also essential to verify that the Traffic Generator has sufficient
    stability to conduct Soak tests. Therefore, a prerequisite is to perform
    this test with the DUT removed and replaced with a cross-over cable (or
    other equivalent very low overhead method such as a loopback in a HW switch),
    so that the traffic generator (and any other network involved) can be tested
    over the Soak period. Note that this test may be challenging for software-
    based traffic generators.


    **Priority**:

    **Description**:

    The aim of this test is to understand the Max Forwarding Rate stability over an
    extended test duration in order to uncover any outliers. To allow for an
    extended test duration, the test should ideally run for 24 hours or, if
    this is not possible, for at least 6 hours.

    For this test, one frame size must be sent at the highest frame rate with
    X% packet loss ratio, as determined in the prerequisite test (a short trial).
    The loss ratio shall be measured and recorded every 5 minutes during the test
    (it may be sufficient to collect lost frame counts and divide by the number 
    of frames sent in 5 minutes to see if a threshold has been crossed, 
    and accept some small inaccuracy in the threshold evaluation, not the result).
    The default loss ratio is X = 0% and loss ratio > 10^-7% is the default
    threshold to terminate the test early (or inform the test operator of
    the failure status).

    Note: Other values of X and loss threshold can be tested if required by the user.

    During this test, the DUT must perform the following operations on the
    traffic flow:

    -  Perform packet parsing on the DUT's ingress port.
    -  Perform any relevant address look-ups on the DUT's ingress ports.
    -  Modify the packet header before forwarding the packet to the DUT's
       egress port. Packet modifications include:

       -  Modifying the Ethernet source or destination MAC address.
       -  Modifying/adding a VLAN tag (**Recommended**).
       -  Modifying/adding a MPLS tag.
       -  Modifying the source or destination ip address.
       -  Modifying the TOS/DSCP field.
       -  Modifying the source or destination ports for UDP/TCP/SCTP.
       -  Modifying the TTL.

    **Expected Result**:

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  Max Forwarding Rate stability of the DUT.

       -  This means reporting the number of packets lost per time interval
          and reporting any time intervals with packet loss. The
          `RFC2889 <https://www.rfc-editor.org/rfc/rfc2289.txt>`__
          Forwarding Rate shall be measured in each interval.
          An interval of 300s is suggested.

    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.
    -  The `RFC5481 <https://www.rfc-editor.org/rfc/rfc5481.txt>`__
       PDV form of delay variation on the traffic flow, using the 99th
       percentile, may also be collected.

.. 3.2.2.1.8

Test ID: LTD.Throughput.RFC6201.ResetTime
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 6201 Reset Time Test

    **Prerequisite Test**: N/A

    **Priority**:

    **Description**:

    The aim of this test is to determine the length of time it takes the DUT
    to recover from a reset.

    Two reset methods are defined - planned and unplanned. A planned reset
    requires stopping and restarting the virtual switch by the usual
    'graceful' method defined by it's documentation. An unplanned reset
    requires simulating a fatal internal fault in the virtual switch - for
    example by using kill -SIGKILL on a Linux environment.

    Both reset methods SHOULD be exercised.

    For each frame size previously defined under :ref:`default-test-parameters`,
    traffic should be sent to the DUT under
    normal conditions. During the duration of the test and while the traffic
    flows are passing through the DUT, the DUT should be reset and the Reset
    time measured. The Reset time is the total time that a device is
    determined to be out of operation and includes the time to perform the
    reset and the time to recover from it (cf. `RFC6201
    <https://www.rfc-editor.org/rfc/rfc6201.txt>`__).

    `RFC6201 <https://www.rfc-editor.org/rfc/rfc6201.txt>`__ defines two methods
    to measure the Reset time:

      - Frame-Loss Method: which requires the monitoring of the number of
        lost frames and calculates the Reset time based on the number of
        frames lost and the offered rate according to the following
        formula:

        .. code-block:: console

                                    Frames_lost (packets)
                 Reset_time = -------------------------------------
                                Offered_rate (packets per second)

      - Timestamp Method: which measures the time from which the last frame
        is forwarded from the DUT to the time the first frame is forwarded
        after the reset. This involves time-stamping all transmitted frames
        and recording the timestamp of the last frame that was received prior
        to the reset and also measuring the timestamp of the first frame that
        is received after the reset. The Reset time is the difference between
        these two timestamps.

    According to `RFC6201 <https://www.rfc-editor.org/rfc/rfc6201.txt>`__ the
    choice of method depends on the test tool's capability; the Frame-Loss
    method SHOULD be used if the test tool supports:

     * Counting the number of lost frames per stream.
     * Transmitting test frame despite the physical link status.

    whereas the Timestamp method SHOULD be used if the test tool supports:

     * Timestamping each frame.
     * Monitoring received frame's timestamp.
     * Transmitting frames only if the physical link status is up.

    **Expected Result**:

    **Metrics collected**

    The following are the metrics collected for this test:

     * Average Reset Time over the number of trials performed.

    Results of this test should include the following information:

     * The reset method used.
     * Throughput in Fps and Mbps.
     * Average Frame Loss over the number of trials performed.
     * Average Reset Time in milliseconds over the number of trials performed.
     * Number of trials performed.
     * Protocol: IPv4, IPv6, MPLS, etc.
     * Frame Size in Octets
     * Port Media: Ethernet, Gigabit Ethernet (GbE), etc.
     * Port Speed: 10 Gbps, 40 Gbps etc.
     * Interface Encapsulation: Ethernet, Ethernet VLAN, etc.

    **Deployment scenario**:

    * Physical → virtual switch → physical.

.. 3.2.2.1.9

Test ID: LTD.Throughput.RFC2889.MaxForwardingRate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC2889 Forwarding Rate Test

    **Prerequisite Test**: LTD.Throughput.RFC2544.PacketLossRatio

    **Priority**:

    **Description**:

    This test measures the DUT's Max Forwarding Rate when the Offered Load
    is varied between the throughput and the Maximum Offered Load for fixed
    length frames at a fixed time interval. The selected frame sizes are
    those previously defined under :ref:`default-test-parameters`.
    The throughput is the maximum offered
    load with 0% frame loss (measured by the prerequisite test), and the
    Maximum Offered Load (as defined by
    `RFC2285 <https://www.rfc-editor.org/rfc/rfc2285.txt>`__) is *"the highest
    number of frames per second that an external source can transmit to a
    DUT/SUT for forwarding to a specified output interface or interfaces"*.

    Traffic should be sent to the DUT at a particular rate (TX rate)
    starting with TX rate equal to the throughput rate. The rate of
    successfully received frames at the destination counted (in FPS). If the
    RX rate is equal to the TX rate, the TX rate should be increased by a
    fixed step size and the RX rate measured again until the Max Forwarding
    Rate is found.

    The trial duration for each iteration should last for the period of time
    needed for the system to reach steady state for the frame size being
    tested. Under `RFC2889 <https://www.rfc-editor.org/rfc/rfc2289.txt>`__
    (Sec. 5.6.3.1) test methodology, the test
    duration should run for a minimum period of 30 seconds, regardless
    whether the system reaches steady state before the minimum duration
    ends.

    **Expected Result**: According to
    `RFC2889 <https://www.rfc-editor.org/rfc/rfc2289.txt>`__ The Max Forwarding
    Rate is the highest forwarding rate of a DUT taken from an iterative set of
    forwarding rate measurements. The iterative set of forwarding rate measurements
    are made by setting the intended load transmitted from an external source and
    measuring the offered load (i.e what the DUT is capable of forwarding). If the
    Throughput == the Maximum Offered Load, it follows that Max Forwarding Rate is
    equal to the Maximum Offered Load.

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The Max Forwarding Rate for the DUT for each packet size.
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

    **Deployment scenario**:

    -  Physical → virtual switch → physical. Note: Full mesh tests with
       multiple ingress and egress ports are a key aspect of RFC 2889
       benchmarks, and scenarios with both 2 and 4 ports should be tested.
       In any case, the number of ports used must be reported.

.. 3.2.2.1.10

Test ID: LTD.Throughput.RFC2889.ForwardPressure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC2889 Forward Pressure Test

    **Prerequisite Test**: LTD.Throughput.RFC2889.MaxForwardingRate

    **Priority**:

    **Description**:

    The aim of this test is to determine if the DUT transmits frames with an
    inter-frame gap that is less than 12 bytes. This test overloads the DUT
    and measures the output for forward pressure. Traffic should be
    transmitted to the DUT with an inter-frame gap of 11 bytes, this will
    overload the DUT by 1 byte per frame. The forwarding rate of the DUT
    should be measured.

    **Expected Result**: The forwarding rate should not exceed the maximum
    forwarding rate of the DUT collected by
    LTD.Throughput.RFC2889.MaxForwardingRate.

    **Metrics collected**

    The following are the metrics collected for this test:

    -  Forwarding rate of the DUT in FPS or Mbps.
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

    **Deployment scenario**:

    -  Physical → virtual switch → physical.

.. 3.2.2.1.11

Test ID: LTD.Throughput.RFC2889.ErrorFramesFiltering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC2889 Error Frames Filtering Test

    **Prerequisite Test**: N/A

    **Priority**:

    **Description**:

    The aim of this test is to determine whether the DUT will propagate any
    erroneous frames it receives or whether it is capable of filtering out
    the erroneous frames. Traffic should be sent with erroneous frames
    included within the flow at random intervals. Illegal frames that must
    be tested include: - Oversize Frames. - Undersize Frames. - CRC Errored
    Frames. - Dribble Bit Errored Frames - Alignment Errored Frames

    The traffic flow exiting the DUT should be recorded and checked to
    determine if the erroneous frames where passed through the DUT.

    **Expected Result**: Broken frames are not passed!

    **Metrics collected**

    No Metrics are collected in this test, instead it determines:

    -  Whether the DUT will propagate erroneous frames.
    -  Or whether the DUT will correctly filter out any erroneous frames
       from traffic flow with out removing correct frames.

    **Deployment scenario**:

    -  Physical → virtual switch → physical.

.. 3.2.2.1.12

Test ID: LTD.Throughput.RFC2889.BroadcastFrameForwarding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC2889 Broadcast Frame Forwarding Test

    **Prerequisite Test**: N

    **Priority**:

    **Description**:

    The aim of this test is to determine the maximum forwarding rate of the
    DUT when forwarding broadcast traffic. For each frame previously defined
    under :ref:`default-test-parameters`, the traffic should
    be set up as broadcast traffic. The traffic throughput of the DUT should
    be measured.

    The test should be conducted with at least 4 physical ports on the DUT.
    The number of ports used MUST be recorded.

    As broadcast involves forwarding a single incoming packet to several
    destinations, the latency of a single packet is defined as the average
    of the latencies for each of the broadcast destinations.

    The incoming packet is transmitted on each of the other physical ports,
    it is not transmitted on the port on which it was received. The test MAY
    be conducted using different broadcasting ports to uncover any
    performance differences.

    **Expected Result**:

    **Metrics collected**:

    The following are the metrics collected for this test:

    -  The forwarding rate of the DUT when forwarding broadcast traffic.
    -  The minimum, average & maximum packets latencies observed.

    **Deployment scenario**:

    -  Physical → virtual switch 3x physical. In the Broadcast rate testing,
       four test ports are required. One of the ports is connected to the test
       device, so it can send broadcast frames and listen for miss-routed frames.

.. 3.2.2.1.13

Test ID: LTD.Throughput.RFC2544.WorstN-BestN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: Modified RFC 2544 X% packet loss ratio Throughput and Latency Test

    **Prerequisite Test**: N/A

    **Priority**:

    **Description**:

    This test determines the DUT's maximum forwarding rate with X% traffic
    loss for a constant load (fixed length frames at a fixed interval time).
    The default loss percentages to be tested are: X = 0%, X = 10^-7%

    Modified RFC 2544 throughput benchmarking methodology aims to quantify
    the throughput measurement variations observed during standard RFC 2544
    benchmarking measurements of virtual switches and VNFs. The RFC2544
    binary search algorithm is modified to use more samples per test trial
    to drive the binary search and yield statistically more meaningful
    results. This keeps the heart of the RFC2544 methodology, still relying
    on the binary search of throughput at specified loss tolerance, while
    providing more useful information about the range of results seen in
    testing. Instead of using a single traffic trial per iteration step,
    each traffic trial is repeated N times and the success/failure of the
    iteration step is based on these N traffic trials. Two types of revised
    tests are defined - *Worst-of-N* and *Best-of-N*.

    **Worst-of-N**

    *Worst-of-N* indicates the lowest expected maximum throughput for (
    packet size, loss tolerance) when repeating the test.

    1.  Repeat the same test run N times at a set packet rate, record each
        result.
    2.  Take the WORST result (highest packet loss) out of N result samples,
        called the Worst-of-N sample.
    3.  If Worst-of-N sample has loss less than the set loss tolerance, then
        the step is successful - increase the test traffic rate.
    4.  If Worst-of-N sample has loss greater than the set loss tolerance
        then the step failed - decrease the test traffic rate.
    5.  Go to step 1.

    **Best-of-N**

    *Best-of-N* indicates the highest expected maximum throughput for (
    packet size, loss tolerance) when repeating the test.

    1.  Repeat the same traffic run N times at a set packet rate, record
        each result.
    2.  Take the BEST result (least packet loss) out of N result samples,
        called the Best-of-N sample.
    3.  If Best-of-N sample has loss less than the set loss tolerance, then
        the step is successful - increase the test traffic rate.
    4.  If Best-of-N sample has loss greater than the set loss tolerance,
        then the step failed - decrease the test traffic rate.
    5.  Go to step 1.

    Performing both Worst-of-N and Best-of-N benchmark tests yields lower
    and upper bounds of expected maximum throughput under the operating
    conditions, giving a very good indication to the user of the
    deterministic performance range for the tested setup.

    **Expected Result**: At the end of each trial series, the presence or
    absence of loss determines the modification of offered load for the
    next trial series, converging on a maximum rate, or
    `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__ Throughput
    with X% loss.
    The Throughput load is re-used in related
    `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__ tests and other
    tests.

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The maximum forwarding rate in Frames Per Second (FPS) and Mbps of
       the DUT for each frame size with X% packet loss.
    -  The average latency of the traffic flow when passing through the DUT
       (if testing for latency, note that this average is different from the
       test specified in Section 26.3 of
       `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__).
    -  Following may also be collected as part of this test, to determine
       the vSwitch's performance footprint on the system:

      -  CPU core utilization.
      -  CPU cache utilization.
      -  Memory footprint.
      -  System bus (QPI, PCI, ...) utilization.
      -  CPU cycles consumed per packet.

.. 3.2.2.1.14

Test ID: LTD.Throughput.Overlay.Network.<tech>.RFC2544.PacketLossRatio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

       **Title**: <tech> Overlay Network RFC 2544 X% packet loss ratio Throughput and Latency Test


       NOTE: Throughout this test, four interchangeable overlay technologies are covered by the
       same test description.  They are: VXLAN, GRE, NVGRE and GENEVE.

      **Prerequisite Test**: N/A

      **Priority**:

      **Description**:
      This test evaluates standard switch performance benchmarks for the scenario where an
      Overlay Network is deployed for all paths through the vSwitch. Overlay Technologies covered
      (replacing <tech> in the test name) include:

      - VXLAN
      - GRE
      - NVGRE
      - GENEVE

      Performance will be assessed for each of the following overlay network functions:

      - Encapsulation only
      - De-encapsulation only
      - Both Encapsulation and De-encapsulation

      For each native packet, the DUT must perform the following operations:

      - Examine the packet and classify its correct overlay net (tunnel) assignment
      - Encapsulate the packet
      - Switch the packet to the correct port

      For each encapsulated packet, the DUT must perform the following operations:

      - Examine the packet and classify its correct native network assignment
      - De-encapsulate the packet, if required
      - Switch the packet to the correct port

    The selected frame sizes are those previously defined under
    :ref:`default-test-parameters`.

    Thus, each test comprises an overlay technology, a network function,
    and a packet size *with* overlay network overhead included
    (but see also the discussion at
    https://etherpad.opnfv.org/p/vSwitchTestsDrafts ).

    The test can also be used to determine the average latency of the traffic.

    Under the `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__
    test methodology, the test duration will
    include a number of trials; each trial should run for a minimum period
    of 60 seconds. A binary search methodology must be applied for each
    trial to obtain the final result for Throughput.

    **Expected Result**: At the end of each trial, the presence or absence
    of loss determines the modification of offered load for the next trial,
    converging on a maximum rate, or
    `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__ Throughput with X%
    loss (where the value of X is typically equal to zero).
    The Throughput load is re-used in related
    `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__ tests and other
    tests.

    **Metrics Collected**:
    The following are the metrics collected for this test:

    -  The maximum Throughput in Frames Per Second (FPS) and Mbps of
       the DUT for each frame size with X% packet loss.
    -  The average latency of the traffic flow when passing through the DUT
       and VNFs (if testing for latency, note that this average is different from the
       test specified in Section 26.3 of
       `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__).
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

.. 3.2.3.1.15

Test ID: LTD.Throughput.RFC2544.MatchAction.PacketLossRatio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2544 X% packet loss ratio match action Throughput and Latency Test

    **Prerequisite Test**: LTD.Throughput.RFC2544.PacketLossRatio

    **Priority**:

    **Description**:

    The aim of this test is to determine the cost of carrying out match
    action(s) on the DUT’s RFC2544 Throughput with X% traffic loss for
    a constant load (fixed length frames at a fixed interval time).

    Each test case requires:

         * selection of a specific match action(s),
         * specifying a percentage of total traffic that is elligible
           for the match action,
         * determination of the specific test configuration (number
           of flows, number of test ports, presence of an external
           controller, etc.), and
         * measurement of the RFC 2544 Throughput level with X% packet
           loss: Traffic shall be bi-directional and symmetric.

    Note: It would be ideal to verify that all match action-elligible
    traffic was forwarded to the correct port, and if forwarded to
    an unintended port it should be considered lost.

    A match action is an action that is typically carried on a frame
    or packet that matches a set of flow classification parameters
    (typically frame/packet header fields). A match action may or may
    not modify a packet/frame. Match actions include [1]:

         * output : outputs a packet to a particular port.
         * normal: Subjects the packet to traditional L2/L3 processing
           (MAC learning).
         * flood: Outputs the packet on all switch physical ports
           other than the port on which it was received and any ports
           on which flooding is disabled.
         * all: Outputs the packet on all switch physical ports other
           than the port on which it was received.
         * local: Outputs  the packet on the ``local port``, which
           corresponds to the network device that has the same name as
           the bridge.
         * in_port: Outputs the packet on the port from which it was
           received.
         * Controller: Sends the packet and its metadata to the
           OpenFlow controller as a ``packet in`` message.
         * enqueue: Enqueues  the  packet  on the specified queue
           within port.
         * drop: discard the packet.

   Modifications include [1]:

         * mod vlan: covered by LTD.Throughput.RFC2544.PacketLossRatioFrameModification
         * mod_dl_src: Sets the source Ethernet address.
         * mod_dl_dst: Sets the destination Ethernet address.
         * mod_nw_src: Sets the IPv4 source address.
         * mod_nw_dst: Sets the IPv4 destination address.
         * mod_tp_src: Sets the TCP or UDP or SCTP source port.
         * mod_tp_dst: Sets the TCP or UDP or SCTP destination port.
         * mod_nw_tos: Sets the  DSCP bits in the IPv4 ToS/DSCP or
           IPv6 traffic class field.
         * mod_nw_ecn: Sets the ECN bits in the appropriate IPv4 or
           IPv6 field.
         * mod_nw_ttl: Sets the IPv4 TTL or IPv6 hop limit field.

    Note: This comprehensive list requires extensive traffic generator
    capabilities.

    The match action(s) that were applied as part of the test should be
    reported in the final test report.

    During this test, the DUT must perform the following operations on
    the traffic flow:

        * Perform packet parsing on the DUT’s ingress port.
        * Perform any relevant address look-ups on the DUT’s ingress
          ports.
        * Carry out one or more of the match actions specified above.

    The default loss percentages to be tested are: - X = 0% - X = 10^-7%
    Other values can be tested if required by the user. The selected
    frame sizes are those previously defined under
    :ref:`default-test-parameters`.

    The test can also be used to determine the average latency of the
    traffic when a match action is applied to packets in a flow. Under
    the RFC2544 test methodology, the test duration will include a
    number of trials; each trial should run for a minimum period of 60
    seconds. A binary search methodology must be applied for each
    trial to obtain the final result.

    **Expected Result:**

    At the end of each trial, the presence or absence of loss
    determines the modification of offered load for the next trial,
    converging on a maximum rate, or RFC2544Throughput with X% loss.
    The Throughput load is re-used in related RFC2544 tests and other
    tests.

    **Metrics Collected:**

    The following are the metrics collected for this test:

        * The RFC 2544 Throughput in Frames Per Second (FPS) and Mbps
          of the DUT for each frame size with X% packet loss.
        * The average latency of the traffic flow when passing through
          the DUT (if testing for latency, note that this average is
          different from the test specified in Section 26.3 ofRFC2544).
        * CPU and memory utilization may also be collected as part of
          this test, to determine the vSwitch’s performance footprint
          on the system.

    The metrics collected can be compared to that of the prerequisite
    test to determine the cost of the match action(s) in the pipeline.

    **Deployment scenario**:

    -  Physical → virtual switch → physical (and others are possible)

    [1] ovs-ofctl - administer OpenFlow switches
        [http://openvswitch.org/support/dist-docs/ovs-ofctl.8.txt ]


.. 3.2.2.2

Packet Latency tests
--------------------

These tests will measure the store and forward latency as well as the packet
delay variation for various packet types through the virtual switch. The
following list is not exhaustive but should indicate the type of tests
that should be required. It is expected that more will be added.

.. 3.2.2.2.1

Test ID: LTD.PacketLatency.InitialPacketProcessingLatency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: Initial Packet Processing Latency

    **Prerequisite Test**: N/A

    **Priority**:

    **Description**:

    In some virtual switch architectures, the first packets of a flow will
    take the system longer to process than subsequent packets in the flow.
    This test determines the latency for these packets. The test will
    measure the latency of the packets as they are processed by the
    flow-setup-path of the DUT. There are two methods for this test, a
    recommended method and a nalternative method that can be used if it is
    possible to disable the fastpath of the virtual switch.

    Recommended method: This test will send 64,000 packets to the DUT, each
    belonging to a different flow. Average packet latency will be determined
    over the 64,000 packets.

    Alternative method: This test will send a single packet to the DUT after
    a fixed interval of time. The time interval will be equivalent to the
    amount of time it takes for a flow to time out in the virtual switch
    plus 10%. Average packet latency will be determined over 1,000,000
    packets.

    This test is intended only for non-learning virtual switches; For learning
    virtual switches use RFC2889.

    For this test, only unidirectional traffic is required.

    **Expected Result**: The average latency for the initial packet of all
    flows should be greater than the latency of subsequent traffic.

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  Average latency of the initial packets of all flows that are
       processed by the DUT.

    **Deployment scenario**:

    -  Physical → Virtual Switch → Physical.

.. 3.2.2.2.2

Test ID: LTD.PacketDelayVariation.RFC3393.Soak
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: Packet Delay Variation Soak Test

    **Prerequisite Tests**:

    LTD.Throughput.RFC2544.PacketLossRatio will determine the offered load and
    frame size for which the maximum theoretical throughput of the interface
    has not been achieved. As described in RFC 2544 section 24, the final
    determination of the benchmark SHOULD be conducted using a full length
    trial, and for this purpose the duration is 5 minutes with zero loss ratio.

    It is also essential to verify that the Traffic Generator has sufficient
    stability to conduct Soak tests. Therefore, a prerequisite is to perform
    this test with the DUT removed and replaced with a cross-over cable (or
    other equivalent very low overhead method such as a loopback in a HW switch),
    so that the traffic generator (and any other network involved) can be tested
    over the Soak period. Note that this test may be challenging for software-
    based traffic generators.


    **Priority**:

    **Description**:

    The aim of this test is to understand the distribution of packet delay
    variation for different frame sizes over an extended test duration and
    to determine if there are any outliers. To allow for an extended test
    duration, the test should ideally run for 24 hours or, if this is not
    possible, for at least 6 hours.

    For this test, one frame size must be sent at the highest frame rate with
    X% packet loss ratio, as determined in the prerequisite test (a short trial).
    The loss ratio shall be measured and recorded every 5 minutes during the test
    (it may be sufficient to collect lost frame counts and divide by the number 
    of frames sent in 5 minutes to see if a threshold has been crossed, 
    and accept some small inaccuracy in the threshold evaluation, not the result).
    The default loss ratio is X = 0% and loss ratio > 10^-7% is the default
    threshold to terminate the test early (or inform the test operator of
    the failure status).

    Note: Other values of X and loss threshold can be tested if required by the user.


    **Expected Result**:

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The packet delay variation value for traffic passing through the DUT.
    -  The `RFC5481 <https://www.rfc-editor.org/rfc/rfc5481.txt>`__
       PDV form of delay variation on the traffic flow,
       using the 99th percentile, for each 300s interval during the test.
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

.. 3.2.2.3

Scalability tests
-----------------

The general aim of these tests is to understand the impact of large flow
table size and flow lookups on throughput. The following list is not
exhaustive but should indicate the type of tests that should be required.
It is expected that more will be added.

.. 3.2.2.3.1

.. _Scalability0PacketLoss:

Test ID: LTD.Scalability.Flows.RFC2544.0PacketLoss
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2544 0% loss Flow Scalability throughput test

    **Prerequisite Test**: LTD.Throughput.RFC2544.PacketLossRatio, IF the
    delta Throughput between the single-flow RFC2544 test and this test with
    a variable number of flows is desired.

    **Priority**:

    **Description**:

    The aim of this test is to measure how throughput changes as the number
    of flows in the DUT increases. The test will measure the throughput
    through the fastpath, as such the flows need to be installed on the DUT
    before passing traffic.

    For each frame size previously defined under :ref:`default-test-parameters`
    and for each of the following number of flows:

    -  1,000
    -  2,000
    -  4,000
    -  8,000
    -  16,000
    -  32,000
    -  64,000
    -  Max supported number of flows.

    This test will be conducted under two conditions following the
    establishment of all flows as required by RFC 2544, regarding the flow
    expiration time-out:

    1) The time-out never expires during each trial.

    2) The time-out expires for all flows periodically. This would require a
    short time-out compared with flow re-appearance for a small number of
    flows, and may not be possible for all flow conditions.

    The maximum 0% packet loss Throughput should be determined in a manner
    identical to LTD.Throughput.RFC2544.PacketLossRatio.

    **Expected Result**:

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The maximum number of frames per second that can be forwarded at the
       specified number of flows and the specified frame size, with zero
       packet loss.

.. 3.2.2.3.2

Test ID: LTD.MemoryBandwidth.RFC2544.0PacketLoss.Scalability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2544 0% loss Memory Bandwidth Scalability test

    **Prerequisite Tests**: LTD.Throughput.RFC2544.PacketLossRatio, IF the
    delta Throughput between an undisturbed RFC2544 test and this test with
    the Throughput affected by cache and memory bandwidth contention is desired.

    **Priority**:

    **Description**:

    The aim of this test is to understand how the DUT's performance is
    affected by cache sharing and memory bandwidth between processes.

    During the test all cores not used by the vSwitch should be running a
    memory intensive application. This application should read and write
    random data to random addresses in unused physical memory. The random
    nature of the data and addresses is intended to consume cache, exercise
    main memory access (as opposed to cache) and exercise all memory buses
    equally. Furthermore:

    - the ratio of reads to writes should be recorded. A ratio of 1:1
      SHOULD be used.
    - the reads and writes MUST be of cache-line size and be cache-line aligned.
    - in NUMA architectures memory access SHOULD be local to the core's node.
      Whether only local memory or a mix of local and remote memory is used
      MUST be recorded.
    - the memory bandwidth (reads plus writes) used per-core MUST be recorded;
      the test MUST be run with a per-core memory bandwidth equal to half the
      maximum system memory bandwidth divided by the number of cores. The test
      MAY be run with other values for the per-core memory bandwidth.
    - the test MAY also be run with the memory intensive application running
      on all cores.

    Under these conditions the DUT's 0% packet loss throughput is determined
    as per LTD.Throughput.RFC2544.PacketLossRatio.

    **Expected Result**:

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The DUT's 0% packet loss throughput in the presence of cache sharing and
       memory bandwidth between processes.

.. 3.2.2.3.3

Test ID: LTD.Scalability.VNF.RFC2544.PacketLossRatio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: VNF Scalability RFC 2544 X% packet loss ratio Throughput and
               Latency Test

    **Prerequisite Test**: N/A

    **Priority**:

    **Description**:

    This test determines the DUT's throughput rate with X% traffic loss for
    a constant load (fixed length frames at a fixed interval time) when the
    number of VNFs on the DUT increases. The default loss percentages
    to be tested are: - X = 0% - X = 10^-7% . The minimum number of
    VNFs to be tested are 3.

    Flow classification should be conducted with L2, L3 and L4 matching
    to understand the matching and scaling capability of the vSwitch. The
    matching fields which were used as part of the test should be reported
    as part of the benchmark report.

    The vSwitch is responsible for forwarding frames between the VNFs

    The SUT (vSwitch and VNF daisy chain) operation should be validated
    before running the test. This may be completed by running a burst or
    continuous stream of traffic through the SUT to ensure proper operation
    before a test.

    **Note**: The traffic rate used to validate SUT operation should be low
    enough not to stress the SUT.

    **Note**: Other values can be tested if required by the user.

    **Note**: The same VNF should be used in the "daisy chain" formation.
    Each addition of a VNF should be conducted in a new test setup (The DUT
    is brought down, then the DUT is brought up again). An atlernative approach
    would be to continue to add VNFs without bringing down the DUT. The
    approach used needs to be documented as part of the test report.

    The selected frame sizes are those previously defined under
    :ref:`default-test-parameters`.
    The test can also be used to determine the average latency of the traffic.

    Under the `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__
    test methodology, the test duration will
    include a number of trials; each trial should run for a minimum period
    of 60 seconds. A binary search methodology must be applied for each
    trial to obtain the final result for Throughput.

    **Expected Result**: At the end of each trial, the presence or absence
    of loss determines the modification of offered load for the next trial,
    converging on a maximum rate, or
    `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__ Throughput with X%
    loss.
    The Throughput load is re-used in related
    `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__ tests and other
    tests.

    If the test VNFs are rather light-weight in terms of processing, the test
    provides a view of multiple passes through the vswitch on logical
    interfaces. In other words, the test produces an optimistic count of
    daisy-chained VNFs, but the cumulative effect of traffic on the vSwitch is
    "real" (assuming that the vSwitch has some dedicated resources, and the
    effects on shared resources is understood).


    **Metrics Collected**:
    The following are the metrics collected for this test:

    -  The maximum Throughput in Frames Per Second (FPS) and Mbps of
       the DUT for each frame size with X% packet loss.
    -  The average latency of the traffic flow when passing through the DUT
       and VNFs (if testing for latency, note that this average is different from the
       test specified in Section 26.3 of
       `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__).
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

.. 3.2.2.3.4

Test ID: LTD.Scalability.VNF.RFC2544.PacketLossProfile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

     **Title**: VNF Scalability RFC 2544 Throughput and Latency Profile

     **Prerequisite Test**: N/A

     **Priority**:

     **Description**:

     This test reveals how throughput and latency degrades as the number
     of VNFs increases and offered rate varies in the region of the DUT's
     maximum forwarding rate as determined by
     LTD.Throughput.RFC2544.PacketLossRatio (0% Packet Loss).
     For example it can be used to determine if the degradation of throughput
     and latency as the number of VNFs and offered rate increases is slow
     and graceful, or sudden and severe. The minimum number of VNFs to
     be tested is 3.

     The selected frame sizes are those previously defined under
     :ref:`default-test-parameters`.

     The offered traffic rate is described as a percentage delta with respect
     to the DUT's RFC 2544 Throughput as determined by
     LTD.Throughput.RFC2544.PacketLoss Ratio (0% Packet Loss case). A delta
     of 0% is equivalent to an offered traffic rate equal to the RFC 2544
     Throughput; A delta of +50% indicates an offered rate half-way
     between the Throughput and line-rate, whereas a delta of
     -50% indicates an offered rate of half the maximum rate. Therefore the
     range of the delta figure is natuarlly bounded at -100% (zero offered
     traffic) and +100% (traffic offered at line rate).

     The following deltas to the maximum forwarding rate should be applied:

     -  -50%, -10%, 0%, +10% & +50%

    **Note**: Other values can be tested if required by the user.

    **Note**: The same VNF should be used in the "daisy chain" formation.
    Each addition of a VNF should be conducted in a new test setup (The DUT
    is brought down, then the DUT is brought up again). An atlernative approach
    would be to continue to add VNFs without bringing down the DUT. The
    approach used needs to be documented as part of the test report.

    Flow classification should be conducted with L2, L3 and L4 matching
    to understand the matching and scaling capability of the vSwitch. The
    matching fields which were used as part of the test should be reported
    as part of the benchmark report.

    The SUT (vSwitch and VNF daisy chain) operation should be validated
    before running the test. This may be completed by running a burst or
    continuous stream of traffic through the SUT to ensure proper operation
    before a test.

    **Note**: the traffic rate used to validate SUT operation should be low
    enough not to stress the SUT

    **Expected Result**: For each packet size a profile should be produced
    of how throughput and latency vary with offered rate.

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The forwarding rate in Frames Per Second (FPS) and Mbps of the DUT
       for each delta to the maximum forwarding rate and for each frame
       size.
    -  The average latency for each delta to the maximum forwarding rate and
       for each frame size.
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.
    -  Any failures experienced (for example if the vSwitch crashes, stops
       processing packets, restarts or becomes unresponsive to commands)
       when the offered load is above Maximum Throughput MUST be recorded
       and reported with the results.

.. 3.2.2.4

Activation tests
----------------

The general aim of these tests is to understand the capacity of the
and speed with which the vswitch can accommodate new flows.

.. 3.2.2.4.1

Test ID: LTD.Activation.RFC2889.AddressCachingCapacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC2889 Address Caching Capacity Test

    **Prerequisite Test**: N/A

    **Priority**:

    **Description**:

    Please note this test is only applicable to virtual switches that are capable of
    MAC learning. The aim of this test is to determine the address caching
    capacity of the DUT for a constant load (fixed length frames at a fixed
    interval time). The selected frame sizes are those previously defined
    under :ref:`default-test-parameters`.

    In order to run this test the aging time, that is the maximum time the
    DUT will keep a learned address in its flow table, and a set of initial
    addresses, whose value should be >= 1 and <= the max number supported by
    the implementation must be known. Please note that if the aging time is
    configurable it must be longer than the time necessary to produce frames
    from the external source at the specified rate. If the aging time is
    fixed the frame rate must be brought down to a value that the external
    source can produce in a time that is less than the aging time.

    Learning Frames should be sent from an external source to the DUT to
    install a number of flows. The Learning Frames must have a fixed
    destination address and must vary the source address of the frames. The
    DUT should install flows in its flow table based on the varying source
    addresses. Frames should then be transmitted from an external source at
    a suitable frame rate to see if the DUT has properly learned all of the
    addresses. If there is no frame loss and no flooding, the number of
    addresses sent to the DUT should be increased and the test is repeated
    until the max number of cached addresses supported by the DUT
    determined.

    **Expected Result**:

    **Metrics collected**:

    The following are the metrics collected for this test:

    -  Number of cached addresses supported by the DUT.
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

    **Deployment scenario**:

    -  Physical → virtual switch → 2 x physical (one receiving, one listening).

.. 3.2.2.4.2

Test ID: LTD.Activation.RFC2889.AddressLearningRate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC2889 Address Learning Rate Test

    **Prerequisite Test**: LTD.Memory.RFC2889.AddressCachingCapacity

    **Priority**:

    **Description**:

    Please note this test is only applicable to virtual switches that are capable of
    MAC learning. The aim of this test is to determine the rate of address
    learning of the DUT for a constant load (fixed length frames at a fixed
    interval time). The selected frame sizes are those previously defined
    under :ref:`default-test-parameters`, traffic should be
    sent with each IPv4/IPv6 address incremented by one. The rate at which
    the DUT learns a new address should be measured. The maximum caching
    capacity from LTD.Memory.RFC2889.AddressCachingCapacity should be taken
    into consideration as the maximum number of addresses for which the
    learning rate can be obtained.

    **Expected Result**: It may be worthwhile to report the behaviour when
    operating beyond address capacity - some DUTs may be more friendly to
    new addresses than others.

    **Metrics collected**:

    The following are the metrics collected for this test:

    -  The address learning rate of the DUT.

    **Deployment scenario**:

    -  Physical → virtual switch → 2 x physical (one receiving, one listening).

.. 3.2.2.5

Coupling between control path and datapath Tests
------------------------------------------------

The following tests aim to determine how tightly coupled the datapath
and the control path are within a virtual switch. The following list
is not exhaustive but should indicate the type of tests that should be
required. It is expected that more will be added.

.. 3.2.2.5.1

Test ID: LTD.CPDPCouplingFlowAddition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: Control Path and Datapath Coupling

    **Prerequisite Test**:

    **Priority**:

    **Description**:

    The aim of this test is to understand how exercising the DUT's control
    path affects datapath performance.

    Initially a certain number of flow table entries are installed in the
    vSwitch. Then over the duration of an RFC2544 throughput test
    flow-entries are added and removed at the rates specified below. No
    traffic is 'hitting' these flow-entries, they are simply added and
    removed.

    The test MUST be repeated with the following initial number of
    flow-entries installed: - < 10 - 1000 - 100,000 - 10,000,000 (or the
    maximum supported number of flow-entries)

    The test MUST be repeated with the following rates of flow-entry
    addition and deletion per second: - 0 - 1 (i.e. 1 addition plus 1
    deletion) - 100 - 10,000

    **Expected Result**:

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  The maximum forwarding rate in Frames Per Second (FPS) and Mbps of
       the DUT.
    -  The average latency of the traffic flow when passing through the DUT
       (if testing for latency, note that this average is different from the
       test specified in Section 26.3 of
       `RFC2544 <https://www.rfc-editor.org/rfc/rfc2544.txt>`__).
    -  CPU and memory utilization may also be collected as part of this
       test, to determine the vSwitch's performance footprint on the system.

    **Deployment scenario**:

    -  Physical → virtual switch → physical.

.. 3.2.2.6

CPU and memory consumption
--------------------------

The following tests will profile a virtual switch's CPU and memory
utilization under various loads and circumstances. The following
list is not exhaustive but should indicate the type of tests that
should be required. It is expected that more will be added.

.. 3.2.2.6.1

.. _CPU0PacketLoss:

Test ID: LTD.Stress.RFC2544.0PacketLoss
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Title**: RFC 2544 0% Loss CPU OR Memory Stress Test

    **Prerequisite Test**:

    **Priority**:

    **Description**:

    The aim of this test is to understand the overall performance of the
    system when a CPU or Memory intensive application is run on the same DUT as
    the Virtual Switch. For each frame size, an
    LTD.Throughput.RFC2544.PacketLossRatio (0% Packet Loss) test should be
    performed. Throughout the entire test a CPU or Memory intensive application
    should be run on all cores on the system not in use by the Virtual Switch.
    For NUMA system only cores on the same NUMA node are loaded.

    It is recommended that stress-ng be used for loading the non-Virtual
    Switch cores but any stress tool MAY be used.

    **Expected Result**:

    **Metrics Collected**:

    The following are the metrics collected for this test:

    -  Memory and CPU utilization of the cores running the Virtual Switch.
    -  The number of identity of the cores allocated to the Virtual Switch.
    -  The configuration of the stress tool (for example the command line
       parameters used to start it.)

    **Note:** Stress in the test ID can be replaced with the name of the
              component being stressed, when reporting the results:
              LTD.CPU.RFC2544.0PacketLoss or LTD.Memory.RFC2544.0PacketLoss

.. 3.2.2.7

Summary List of Tests
---------------------

1. Throughput tests

  - Test ID: LTD.Throughput.RFC2544.PacketLossRatio
  - Test ID: LTD.Throughput.RFC2544.PacketLossRatioFrameModification
  - Test ID: LTD.Throughput.RFC2544.Profile
  - Test ID: LTD.Throughput.RFC2544.SystemRecoveryTime
  - Test ID: LTD.Throughput.RFC2544.BackToBackFrames
  - Test ID: LTD.Throughput.RFC2889.Soak
  - Test ID: LTD.Throughput.RFC2889.SoakFrameModification
  - Test ID: LTD.Throughput.RFC6201.ResetTime
  - Test ID: LTD.Throughput.RFC2889.MaxForwardingRate
  - Test ID: LTD.Throughput.RFC2889.ForwardPressure
  - Test ID: LTD.Throughput.RFC2889.ErrorFramesFiltering
  - Test ID: LTD.Throughput.RFC2889.BroadcastFrameForwarding
  - Test ID: LTD.Throughput.RFC2544.WorstN-BestN
  - Test ID: LTD.Throughput.Overlay.Network.<tech>.RFC2544.PacketLossRatio

2. Packet Latency tests

  - Test ID: LTD.PacketLatency.InitialPacketProcessingLatency
  - Test ID: LTD.PacketDelayVariation.RFC3393.Soak

3. Scalability tests

  - Test ID: LTD.Scalability.Flows.RFC2544.0PacketLoss
  - Test ID: LTD.MemoryBandwidth.RFC2544.0PacketLoss.Scalability
  - LTD.Scalability.VNF.RFC2544.PacketLossProfile
  - LTD.Scalability.VNF.RFC2544.PacketLossRatio

4. Activation tests

  - Test ID: LTD.Activation.RFC2889.AddressCachingCapacity
  - Test ID: LTD.Activation.RFC2889.AddressLearningRate

5. Coupling between control path and datapath Tests

  - Test ID: LTD.CPDPCouplingFlowAddition

6. CPU and memory consumption

  - Test ID: LTD.Stress.RFC2544.0PacketLoss
