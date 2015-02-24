# Design Summary

Below is a summary of the general design of the test suite.

---

## Architecture

The test suite is structured as multiple components, each with a specific purpose. These are:

* `conf`
  Centralised configuration of the test library, designed in the fashion of [Django's] `settings.py`
* `ovs`
  Control of the `ovs-*` (and `ovsdb-*`) applications, including `ovs-dpdk`.
* `guest`
  Control of hypervisors, with basic control of VMs running on said hypervisor
* `system`
  Configuration of the system, as required by DPDK.
* `test`
  Useful functions and classes for tests
* `trafficgen`
  Control of traffic generators
* `utils`
  Additional helper libraries and modules

Each module in the testsuite has been designed to be as independent as possible. Most of them have built-in "main" methods, which can be used to test the system in isolation. Nonetheless, there are a certain amount of dependencies. These dependencies are illustrated below:

    +-----------+
    |           |
    |   ofctl   |
    |           |
    +-----------+
          |
    +-----------+
    |           |
    |   daemon  |
    |           |
    +-----------+
          |
    +-----------+  +-----------+
    |           |  |           |
    |    ovs    |  |   guest   |
    |           |  |           |
    +-----------+  +-----------+
          |              |
    +--------------------------+  +-----------+  +-----------+  +-----------+
    |                          |  |           |  |           |  |           |
    |          system          |  |trafficgen |  |   conf*   |  | sysmetric |
    |                          |  |           |  |           |  |           |
    +--------------------------+  +-----------+  +-----------+  +-----------+

**Note** `conf` is used by all modules. It's pretty useful by itself

---

## Why Python?

During development of this test suite, a number of languages were considered. Python was chosen for the reasons below and more:

* Python is readable
  Well written Python is readable to even novice programmers. Focus on testing your application, not testing your tests.

* It provides a natural way of calling other applications
  While it's not Bash, the `subprocess` modules in Python allows for easy calling of external applications. Unlike Bash, error handling in Python is easy.

* It's extendible
  Python has a "batteries included" approach such that most of the features you could want are available in the default Python distribution. However, should you require more, the "Python Package Index (PyPI) hosts thousands of third-party modules for Python" (source: [About Python]).

* It's portable​
  Python will run anywhere that Open vSwitch does.

---

[About Python]: https://www.python.org/about/
[Django's]: https://www.djangoproject.com/

