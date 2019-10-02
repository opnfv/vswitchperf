Before using VSPERF client and VSPERF containers, user must run the prepare.sh script which will prepare their local environment.

locate vsperf-docker/prepare.sh and run:
bash prepare.sh

VSPERF Containers
------------------

============
deployment
============
User have two choices for deployment, auto and interactive.

1. auto
^^^^^^^^^^^^^^^^^^^^^
This auto deployment container will do everything related with VSPERF set-up automatically. It includes, installation of VSPERF, T-rex and collectd, uploading collectd configuration file on DUT-Host, uploading t-rex configuration files and starting the t-rex traffic generator. Before installing vsperf and t-rex, the container will perform verification process, which includes basic sanity checks such as checking for old installations, huge-page checks, necessary folders and software, etc. User should modify the t-rex(trex_cfg.yaml)and collectd(collectd.conf) configuration files depending on their needs before running the containers.


Pre-Deployment Configuration
******************
User has to provide the following in list.env file:
1.DUT-Host and TGen-Host related credentials and IP address
2.Values for HUGEPAGE_MAX and HUGEPAGE_REQUESTED
3.Option for sanity check - YES or NO.

Build
******************
Use **docker-compose build** command to build the container.

Run
******************
Run the container's service with **docker-compose run deploy** command.


2. interactive
^^^^^^^^^^^^^^^^^^^^^
The interactive container must run before using the vsperf client. It will start the server on port 50051 for the vsperf client to send commands. Deployment interactive container handles all vsperf set-up related commands from vsperf client and performs the corresponding operation.


Build
******************
Run **docker-compose build** command to build the container.

Run
******************
Run the container with **docker-compose up deploy** command.
Once the server is running user have to run testcontrol interactive container and then user can run the vsperf client.


===============
testcontrol
===============
For testcontrol too, user has two choices- auto and interactive.

1. auto
^^^^^^^^^^^^^^^^^^^^^
This auto testcontrol container will perform test automatically on DUT-Host. This container also performing sanity checks automatically. User will also able to get test-status for all tests. If all sanity check doesn't satisfy then test will not run and container gracefully stopped. User can modify the vsperf.conf file which will be upload on DUT-Host automatically by container and used for performing the vsperf test.

Pre-Deployment Configuration
******************
1.User have to provide all the DUT-Host credentials and IP address of TGen-host in list.env.
2.Provide name for VSPERF_TESTS and VSPERF_CONFFILE in list.env.
3.Provide option for VSPERF_TRAFFICGEN_MODE and CLEAN_UP [YES or NO] in list.env file.

Build
******************
Run **docker-compose build** command to build the container.

Run
******************
Run the container's service with **docker-compose run testcontrol** command.
User can observe the results and perform the another test by just changing the VSPERF_TEST environment variable in list.env file.


2. interactive
^^^^^^^^^^^^^^^^^^^^^
This interactive testcontrol container must run before using the vsperf client. It will start the server on port 50052 for the vsperf client. This testcontrol interactive container handle all the test related commands from vsperf client and do the operations. Testcontrol interactive container running server on localhost port 50052.

Build
******************
Run **docker-compose build** command to build the container.

Run
******************
Run the container with **docker-compose up testcontrol** command.
After running this container user can use the vsperf client.
