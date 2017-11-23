.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

.. _vsperf-installation:

======================
Installing vswitchperf
======================

Downloading vswitchperf
-----------------------

The vswitchperf can be downloaded from its official git repository, which is
hosted by OPNFV. It is necessary to install a ``git`` at your DUT before downloading
vswitchperf. Installation of ``git`` is specific to the packaging system used by
Linux OS installed at DUT.

Example of installation of GIT package and its dependencies:

* in case of OS based on RedHat Linux:

  .. code:: bash

     sudo yum install git


* in case of Ubuntu or Debian:

  .. code:: bash

     sudo apt-get install git

After the ``git`` is successfully installed at DUT, then vswitchperf can be downloaded
as follows:

.. code:: bash

   git clone http://git.opnfv.org/vswitchperf

The last command will create a directory ``vswitchperf`` with a local copy of vswitchperf
repository.

Supported Operating Systems
---------------------------

* CentOS 7.3
* Fedora 24 (kernel 4.8 requires DPDK 16.11 and newer)
* Fedora 25 (kernel 4.9 requires DPDK 16.11 and newer)
* openSUSE 42.2
* openSUSE 42.3
* openSUSE Tumbleweed
* RedHat 7.2 Enterprise Linux
* RedHat 7.3 Enterprise Linux
* Ubuntu 14.04
* Ubuntu 16.04
* Ubuntu 16.10 (kernel 4.8 requires DPDK 16.11 and newer)

Supported vSwitches
-------------------

The vSwitch must support Open Flow 1.3 or greater.

* Open vSwitch
* Open vSwitch with DPDK support
* TestPMD application from DPDK (supports p2p and pvp scenarios)
* Cisco VPP

Supported Hypervisors
---------------------

* Qemu version 2.3 or greater (version 2.5.0 is recommended)

Supported VNFs
--------------

In theory, it is possible to use any VNF image, which is compatible
with supported hypervisor. However such VNF must ensure, that appropriate
number of network interfaces is configured and that traffic is properly
forwarded among them. For new vswitchperf users it is recommended to start
with official vloop-vnf_ image, which is maintained by vswitchperf community.

.. _vloop-vnf:

vloop-vnf
=========

The official VM image is called vloop-vnf and it is available for free download
from OPNFV artifactory. This image is based on Linux Ubuntu distribution and it
supports following applications for traffic forwarding:

* DPDK testpmd
* Linux Bridge
* Custom l2fwd module

The vloop-vnf can be downloaded to DUT, for example by ``wget``:

  .. code:: bash

     wget http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20160823.qcow2

**NOTE:** In case that ``wget`` is not installed at your DUT, you could install it at RPM
based system by ``sudo yum install wget`` or at DEB based system by ``sudo apt-get install
wget``.

Changelog of vloop-vnf:

  * `vloop-vnf-ubuntu-14.04_20160823`_

    * ethtool installed
    * only 1 NIC is configured by default to speed up boot with 1 NIC setup
    * security updates applied

  * `vloop-vnf-ubuntu-14.04_20160804`_

    * Linux kernel 4.4.0 installed
    * libnuma-dev installed
    * security updates applied

  * `vloop-vnf-ubuntu-14.04_20160303`_

    * snmpd service is disabled by default to avoid error messages during VM boot
    * security updates applied

  * `vloop-vnf-ubuntu-14.04_20151216`_

    * version with development tools required for build of DPDK and l2fwd

.. _vsperf-installation-script:

Installation
------------

The test suite requires Python 3.3 or newer and relies on a number of other
system and python packages. These need to be installed for the test suite
to function.

Installation of required packages, preparation of Python 3 virtual
environment and compilation of OVS, DPDK and QEMU is performed by
script **systems/build_base_machine.sh**. It should be executed under
user account, which will be used for vsperf execution.

**NOTE:** Password-less sudo access must be configured for given
user account before script is executed.

.. code:: bash

    $ cd systems
    $ ./build_base_machine.sh

**NOTE:** you don't need to go into any of the systems subdirectories,
simply run the top level **build_base_machine.sh**, your OS will be detected
automatically.

Script **build_base_machine.sh** will install all the vsperf dependencies
in terms of system packages, Python 3.x and required Python modules.
In case of CentOS 7 or RHEL it will install Python 3.3 from an additional
repository provided by Software Collections (`a link`_). Installation script
will also use `virtualenv`_ to create a vsperf virtual environment, which is
isolated from the default Python environment. This environment will reside in a
directory called **vsperfenv** in $HOME. It will ensure, that system wide Python
installation is not modified or broken by VSPERF installation. The complete list
of Python packages installed inside virtualenv can be found at file
``requirements.txt``, which is located at vswitchperf repository.

**NOTE:** For RHEL 7.3 Enterprise and CentOS 7.3 OVS Vanilla is not
built from upstream source due to kernel incompatibilities. Please see the
instructions in the vswitchperf_design document for details on configuring
OVS Vanilla for binary package usage.

.. _vpp-installation:

VPP installation
================

VPP installation is now included as part of the VSPerf installation scripts.

In case of an error message about a missing file such as
"Couldn't open file /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7" you can resolve this
issue by simply downloading the file.

  .. code:: bash

    $ wget https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-7


Using vswitchperf
-----------------

You will need to activate the virtual environment every time you start a
new shell session. Its activation is specific to your OS:

* CentOS 7 and RHEL

  .. code:: bash

     $ scl enable python33 bash
     $ source $HOME/vsperfenv/bin/activate

* Fedora and Ubuntu

  .. code:: bash

     $ source $HOME/vsperfenv/bin/activate

After the virtual environment is configued, then VSPERF can be used.
For example:

  .. code:: bash

     (vsperfenv) $ cd vswitchperf
     (vsperfenv) $ ./vsperf --help

Gotcha
======

In case you will see following error during environment activation:

.. code:: bash

   $ source $HOME/vsperfenv/bin/activate
   Badly placed ()'s.

then check what type of shell you are using:

.. code:: bash

   $ echo $SHELL
   /bin/tcsh

See what scripts are available in $HOME/vsperfenv/bin

.. code:: bash

   $ ls $HOME/vsperfenv/bin/
   activate          activate.csh      activate.fish     activate_this.py

source the appropriate script

.. code:: bash

   $ source bin/activate.csh

Working Behind a Proxy
======================

If you're behind a proxy, you'll likely want to configure this before
running any of the above. For example:

  .. code:: bash

    export http_proxy=proxy.mycompany.com:123
    export https_proxy=proxy.mycompany.com:123

.. _a link: http://www.softwarecollections.org/en/scls/rhscl/python33/
.. _virtualenv: https://virtualenv.readthedocs.org/en/latest/
.. _vloop-vnf-ubuntu-14.04_20160823: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20160823.qcow2
.. _vloop-vnf-ubuntu-14.04_20160804: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20160804.qcow2
.. _vloop-vnf-ubuntu-14.04_20160303: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20160303.qcow2
.. _vloop-vnf-ubuntu-14.04_20151216: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20151216.qcow2

Bind Tools DPDK
===============

VSPerf supports the default DPDK bind tool, but also supports driverctl. The
driverctl tool is a new tool being used that allows driver binding to be
persistent across reboots. The driverctl tool is not provided by VSPerf, but can
be downloaded from upstream sources. Once installed set the bind tool to
driverctl to allow VSPERF to correctly bind cards for DPDK tests.

.. code:: python

    PATHS['dpdk']['src']['bind-tool'] = 'driverctl'

Hugepage Configuration
----------------------

Systems running vsperf with either dpdk and/or tests with guests must configure
hugepage amounts to support running these configurations. It is recommended
to configure 1GB hugepages as the pagesize.

The amount of hugepages needed depends on your configuration files in vsperf.
Each guest image requires 2048 MB by default according to the default settings
in the ``04_vnf.conf`` file.

.. code:: bash

    GUEST_MEMORY = ['2048']

The dpdk startup parameters also require an amount of hugepages depending on
your configuration in the ``02_vswitch.conf`` file.

.. code:: bash

    DPDK_SOCKET_MEM = ['1024', '0']

**NOTE:** Option ``DPDK_SOCKET_MEM`` is used by all vSwitches with DPDK support.
It means Open vSwitch, VPP and TestPMD.

VSPerf will verify hugepage amounts are free before executing test
environments. In case of hugepage amounts not being free, test initialization
will fail and testing will stop.

**NOTE:** In some instances on a test failure dpdk resources may not
release hugepages used in dpdk configuration. It is recommended to configure a
few extra hugepages to prevent a false detection by VSPerf that not enough free
hugepages are available to execute the test environment. Normally dpdk would use
previously allocated hugepages upon initialization.

Depending on your OS selection configuration of hugepages may vary. Please refer
to your OS documentation to set hugepages correctly. It is recommended to set
the required amount of hugepages to be allocated by default on reboots.

Information on hugepage requirements for dpdk can be found at
http://dpdk.org/doc/guides/linux_gsg/sys_reqs.html

You can review your hugepage amounts by executing the following command

.. code:: bash

    cat /proc/meminfo | grep Huge

If no hugepages are available vsperf will try to automatically allocate some.
Allocation is controlled by ``HUGEPAGE_RAM_ALLOCATION`` configuration parameter in
``02_vswitch.conf`` file. Default is 2GB, resulting in either 2 1GB hugepages
or 1024 2MB hugepages.

Tuning Considerations
---------------------

With the large amount of tuning guides available online on how to properly
tune a DUT, it becomes difficult to achieve consistent numbers for DPDK testing.
VSPerf recommends a simple approach that has been tested by different companies
to achieve proper CPU isolation.

The idea behind CPU isolation when running DPDK based tests is to achieve as few
interruptions to a PMD process as possible. There is now a utility available on
most Linux Systems to achieve proper CPU isolation with very little effort and
customization. The tool is called tuned-adm and is most likely installed by
default on the Linux DUT

VSPerf recommends the latest tuned-adm package, which can be downloaded from the
following location:

http://www.tuned-project.org/2017/04/27/tuned-2-8-0-released/

Follow the instructions to install the latest tuned-adm onto your system. For
current RHEL customers you should already have the most current version. You
just need to install the cpu-partitioning profile.

.. code:: bash

    yum install -y tuned-profiles-cpu-partitioning.noarch

Proper CPU isolation starts with knowing what NUMA your NIC is installed onto.
You can identify this by checking the output of the following command

.. code:: bash

    cat /sys/class/net/<NIC NAME>/device/numa_node

You can then use utilities such as lscpu or cpu_layout.py which is located in
the src dpdk area of VSPerf. These tools will show the CPU layout of which
cores/hyperthreads are located on the same NUMA.

Determine which CPUS/Hyperthreads will be used for PMD threads and VCPUs for
VNFs. Then modify the /etc/tuned/cpu-partitioning-variables.conf and add the
CPUs into the isolated_cores variable in some form of x-y or x,y,z or x-y,z,
etc. Then apply the profile.

.. code:: bash

    tuned-adm profile cpu-partitioning

After applying the profile, reboot your system.

After rebooting the DUT, you can verify the profile is active by running

.. code:: bash

    tuned-adm active

Now you should have proper CPU isolation active and can achieve consistent
results with DPDK based tests.

The last consideration is when running TestPMD inside of a VNF, it may make
sense to enable enough cores to run a PMD thread on separate core/HT. To achieve
this, set the number of VCPUs to 3 and enable enough nb-cores in the TestPMD
config. You can modify options in the conf files.

.. code:: python

    GUEST_SMP = ['3']
    GUEST_TESTPMD_PARAMS = ['-l 0,1,2 -n 4 --socket-mem 512 -- '
                            '--burst=64 -i --txqflags=0xf00 '
                            '--disable-hw-vlan --nb-cores=2']

Verify you set the VCPU core locations appropriately on the same NUMA as with
your PMD mask for OVS-DPDK.
