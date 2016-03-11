.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation, AT&T and others.

======================
Installing vswitchperf
======================

Supported Operating Systems
---------------------------

* CentOS 7
* Fedora 20
* Fedora 21
* Fedora 22
* RedHat 7.2
* Ubuntu 14.04

Supported vSwitches
-------------------
The vSwitch must support Open Flow 1.3 or greater.

* OVS (built from source).
* OVS with DPDK (built from source).

Supported Hypervisors
---------------------

* Qemu version 2.3.

Available VNFs
--------------
A simple VNF that forwards traffic through a VM, using:

* DPDK testpmd
* Linux Brigde
* custom l2fwd module

The official VM image is called vloop-vnf and it is available for free
download at OPNFV website.

vloop-vnf changelog:
====================

* `vloop-vnf-ubuntu-14.04_20160303`_

  * snmpd service is disabled by default to avoid error messages during VM boot
  * security updates applied

* `vloop-vnf-ubuntu-14.04_20151216`_

  * version with development tools required for build of DPDK and l2fwd

Other Requirements
------------------
The test suite requires Python 3.3 and relies on a number of other
packages. These need to be installed for the test suite to function.

Installation of required packages, preparation of Python 3 virtual
environment and compilation of OVS, DPDK and QEMU is performed by
script **systems/build_base_machine.sh**. It should be executed under
user account, which will be used for vsperf execution.

**Please Note**: Password-less sudo access must be configured for given
user account before script is executed.

Execution of installation script:

.. code:: bash

    $ cd systems
    $ ./build_base_machine.sh

**Please Note**: you don't need to go into any of the systems subdirectories,
simply run the top level **build_base_machine.sh**, your OS will be detected
automatically.

Script **build_base_machine.sh** will install all the vsperf dependencies
in terms of system packages, Python 3.x and required Python modules.
In case of CentOS 7 it will install Python 3.3 from an additional repository
provided by Software Collections (`a link`_). In case of RedHat 7 it will
install Python 3.4 as an alternate installation in /usr/local/bin. Installation
script will also use `virtualenv`_ to create a vsperf virtual environment,
which is isolated from the default Python environment. This environment will
reside in a directory called **vsperfenv** in $HOME.

You will need to activate the virtual environment every time you start a
new shell session. Its activation is specific to your OS:

CentOS 7
========

.. code:: bash

    $ scl enable python33 bash
    $ cd $HOME/vsperfenv
    $ source bin/activate

Fedora, RedHat and Ubuntu
=========================

.. code:: bash

    $ cd $HOME/vsperfenv
    $ source bin/activate

Working Behind a Proxy
======================

If you're behind a proxy, you'll likely want to configure this before
running any of the above. For example:

  .. code:: bash

    export http_proxy=proxy.mycompany.com:123
    export https_proxy=proxy.mycompany.com:123

.. _a link: http://www.softwarecollections.org/en/scls/rhscl/python33/
.. _virtualenv: https://virtualenv.readthedocs.org/en/latest/
.. _vloop-vnf-ubuntu-14.04_20160303: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20160303.qcow2
.. _vloop-vnf-ubuntu-14.04_20151216: http://artifacts.opnfv.org/vswitchperf/vnf/vloop-vnf-ubuntu-14.04_20151216.qcow2
