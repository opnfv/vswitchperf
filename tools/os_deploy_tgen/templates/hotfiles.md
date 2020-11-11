# How to use these HOT Files.

These hot files are referenced in the yaml files.
Please ensure you are using correct HOT file.

## L2 - No Routers are setup - Same Subnet.

l2fip.hot - Floating IP is configured. Use this if the Openstack environment supports floating IP.
l2up - Use this if you want username and password configured for the TestVNFs.
l2.hot - Use this if the 2 interfaces has fixed IPs from 2 different networks. This applies when TestVNF has connectivity to provider network.

## L3 - Routers are setup - Different Subnets
l3.hot - Setup TestVNFs on two different subnet and connect them with a router.
