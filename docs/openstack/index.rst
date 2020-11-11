.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Spirent Communications, AT&T, Ixia  and others.

.. OPNFV VSPERF With Openstack master file.

***************************
OPNFV VSPERF with OPENSTACK
***************************

Introduction
------------
VSPERF performs the following, when run with openstack:

1. Connect to Openstack (using the credentials)
2. Deploy Traffic-Generators in a required way (defined by scenarios)
3. Update the VSPERF configuration based on the deployment.
4. Use the updated configuration to run test in "Trafficgen" Mode. 
5. Publish and store results.


What to Configure?
^^^^^^^^^^^^^^^^^^
The configurable parameters are provided in *conf/11_openstackstack.conf*. The configurable parameters are:

1. Access to Openstack Environment: Auth-URL, Username, Password, Project and Domain IDs/Name.
2. VM Details - Name, Flavor, External-Network.
3. Scenario - How many compute nodes to use, and how many instances of trafficgenerator to deploy.
 
User can customize these parameters. Assume the customized values are placed in openstack.conf file. This file will be used to run the test.

How to run?
^^^^^^^^^^^
Add --openstack flag as show below

.. code-block:: console
    
    vsperf --openstack --conf-file openstack.conf phy2phy_tput

