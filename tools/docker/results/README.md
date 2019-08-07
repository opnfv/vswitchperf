## Please set the limit on mmap counts equal to 262144 or more.

There are two options. Run this command:
```sh

sysctl -w vm.max_map_count = 262144

```
or, to set it permanently, update the
```sh

vm.max_map_count

```
setting in

```sh

/etc/sysctl.conf

```

### Update the IP address.
You may want to modify the IP address from 0.0.0.0 to appropriate host-ip in
```sh
docker-compose.yml

```

### Changes made to sebp/elk
The vsperf/elk image is same as sebp/elk with a minor change - the inclusion of collectd codec to logstash.
In the Dockerfile of sebp/elk, under logstash configuration, following lines are added:
```sh
 WORKDIR ${LOGSTASH_HOME}
 RUN gosu logstash bin/logstash-plugin install logstash-codec-collectd
 WORKDIR /

```

The resultsdb directory contains the source from Dovetail/Dovetail-webportal project.
Once the results container is deployed, please run the python script as follows, to ensure that results can be pushed and queried correctly.
```sh
python init_db.py host_ip_address testapi_port
```
For example, if the host on which the container is running is 10.10.120.22, and container is exposing 8000 as the port, the command should be:
```sh
python init_db.py 10.10.120.22 8000
```
