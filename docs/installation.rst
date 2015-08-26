Installing vswitchperf
======================

The test suite requires Python 3.3 and relies on a number of other
packages. These need to be installed for the test suite to function. To
install Python 3.3 in CentOS 7, an additional repository, Software
Collections (see
https://www.softwarecollections.org/en/scls/rhscl/python33) should be
enabled.

Install the requirements as specified below.

Enable Software Collections (SCL)
---------------------------------

  .. code-block:: console

   yum -y install scl-utils
   yum -y install https://www.softwarecollections.org/en/scls/rhscl/python33/epel-7-x86_64/download/rhscl-python33-epel-7-x86_64.noarch.rpm

(Optional) Enable Repoforge (for stress)
----------------------------------------
Allows optional installation of stress tool, which is required by load tests.

  .. code-block:: console

   yum -y install http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.3-1.el7.rf.x86_64.rpm

System packages
-----------------
There are a number of packages that must be installed using `yum`. These can be installed like so:

  .. code-block:: console

   yum -y --exclude=python33-mod_wsgi* install python33-* pciutils

Optional installation of stress tool

  .. code-block:: console

   yum -y install stress

Python 3 Packages
-----------------

To avoid file permission errors and Python version issues, use
virtualenv to create an isolated environment with Python3. The required
Python 3 packages can be found in the ``requirements.txt`` file in the
root of the test suite. They can be installed in your virtual
environment like so:

  .. code-block:: bash

    scl enable python33 bash
    # Create virtual environment
    virtualenv vsperfenv
    cd vsperfenv
    source bin/activate
    pip install -r requirements.txt

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
