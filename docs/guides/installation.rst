Installing vswitchperf
======================

The test suite requires Python 3.3 and relies on a number of other
packages. These need to be installed for the test suite to function. To
install Python 3.3 in CentOS 7, an additional repository, Software
Collections (see
https://www.softwarecollections.org/en/scls/rhscl/python33) should be
enabled.

Installation of required packages and preparation of Python 3 virtual
environment is performed by systems/build_base_machine.sh. It should be
executed under user account, which will be used for vsperf execution.
Password less sudo access must be configured for given user account
before script is executed.

Execution of installation script:

.. code:: bash

    cd systems
    ./build_base_machine.sh

You need to activate the virtual environment every time you start a new
shell session. To activate, simple run:

.. code:: bash

    scl enable python33 bash
    cd vsperfenv
    source bin/activate

--------------

Working Behind a Proxy
======================

If you're behind a proxy, you'll likely want to configure this before
running any of the above. For example:

  .. code:: bash

    export http_proxy=proxy.mycompany.com:123
    export https_proxy=proxy.mycompany.com:123
