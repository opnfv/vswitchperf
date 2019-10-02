VSPERF Client
--------------
VSPERF client is a simple python application, which can be used to work with interactive deploy and testcontrol containers.

============
Description
============

VSPERF client is used for both set-up of DUT-Host and TGen-Host as well as to run multiple tests. User can perform different operations by selecting the available options and their sub-options.

VSPERF client provides following options to User.

* Establish Connections
This option allows user to initialize the connections.

[0]Connect to DUT Host: It will establish connection with DUT-HOST. DUT-HOST refers to system where the DUT - vswitch and vnfs - run. The vsperf application also runs on DUT-HOST.
[1]Connect to Tgen Host: This option will establish connection with TGEN-HOST. TGEN-HOST refers to system where the traffic generator runs. As of now, only T-Rex is support for installation and configuration.

* Installation
After establishing the connections, user can perform installations to set up the test environment. Under this, we have 3 options:

[0]Install VSPERF : This option will first check either vsperf is installed on DUT-Host or not. If VSPERF is not installed, it will perform VSPERF installation process on DUT-Host

[1]Install TGen: This option will check whether t-rex is installed on Tgen-host or not. If t-rex is already installed then it will also check either is working fine or not. If t-rex is not installed, then configured version of t-rex will be installed.

[2]Install Collectd: This is option will install collectd on DUT-Host.

* Upload Configuration Files
Once the installation process is completed, User can upload configuration files. Two uploads are supported:

[0]Upload TGen Configuration File: It will upload trex_cfg.yaml configuration file to Tgen-Host.[User can either specify path in vsperfclient.conf or provide path during runtime for the trex_cfg.yaml]. This file will be used to run T-rex traffic generator.

[1]Upload Collectd Configuration File: This is option is use to uplaod collectd configuration file.

* Manage DUT-System Configuration
Following upload of configuration files, user can perform some basic configuration of the DUT-Host. The available options are:

[0]DUT-Host hugepages configuration: This option allows User to manage hugepages of DUT-Host. [User need to provide values for HpMax and HpRequested in vsperfclient.conf]

[1]Check VSPERF dependencies: Using this option user can check library dependencies on DUT-Host.

* Run Test
Once the above steps are completed, user can perform sanity checks and run the tests. The available options are:

[0]Upload Test Configuration File : This option will upload the vsperf test configuration file.

[1]Perform Sanity Checks before running tests : This option has certain sub-options, user must perform all sanity checks before running test. User may not able to start the Vsperf test until all sanity checks are passed. The sanity check option contains following sub-options: (a) check VSPERF is installed correctly, (b) check if VNF path is available on DUT-Host, (c) check if configured NIC-PCIs is available on TGen and DUT hosts (d) check if Collectd is installed correctly (e) check if connection between DUT-Host and TGen-Host is OK, (f) check CPU-allocation on DUT-host is done correctly.

[2]Check if DUT-HOST is available : User can check if DUT-Host is available for Test or not. If DUT-Host is available for performing Vsperf user can go ahead and start performing test.

[3]Start TGen : This option will start t-rex traffic generator for test.

[4]Start Beats : This option will start beats on DUT-Host

[5]Start Test : If all the sanity checks are passed, and traffic generator is running, then this option will start the vsperf test. Whatever test is defined in vsperfclient.conf will be performed. Note: User can also perform multiple tests.

* Test Status
Once user has started a test, he can check on the status. The following sub-options are available.

[0]Test status : Check whether the test has completed successfully or failed. If user is running multiple tests, they can identify the failed test-name using this option.

[1]Get Test Configuration file from DUT-host: User can also able to read the test configuration file content they uploaded.

* Clean-Up
When all tests are done, user can perform cleanup of the systems, using the following sub-options:

[0]Remove VSPERF: This option will completely remove the vsperfenv on DUT-Host

[1]Terminate VSPERF: This option will keep vsperfenv on DUT-Host. If there is any process still running related with the vsperf then this option will terminate all those processes like ovs-vswitchd,ovsdb-server,vppctl,stress,qemu-system-x86_64.

[2]Remove Results from DUT-Host : This is option will remove all the test results located in /tmp folder.

[3]Remove Uploaded Configuration Files: This option will remove all uploaded test configuration file

[4]Remove Collectd: This option will uninstall collectd from the DUT-Host

[5]Remove Everything: This option will execute all the options listed above.

=============================
How To Use
=============================

Prerequisites before running vsperf client
^^^^^^^^^^^^^^^^^^^^^

1. User must install grpcio, grpcio-tools and configparser for python3 environment.

2. User has to prepare the client-configuration file by providing appropriate values.

3. User has to prepare the configuration files that will be uploaded to either DUT-host or TGen-Host systems.

4. T-rex and collectd configuration files should be named as trex_cfg.yaml and collectd.conf, respectively.

5. Start the deployment-interactive container and testcontrol-interactive container, which will run the servers on ports 50051 and 50052, respectively.

Run vsperf client
^^^^^^^^^^^^^^^^^^^^^
Locate and run the vsperf_client.py with python3.

