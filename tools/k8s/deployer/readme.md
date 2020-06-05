# Deployer

#### Automating K8s object provisioning 

This tool helps in automating deployment of various K8s objects through Ansible roles packaged as Docker container.

<br>

##### Prerequisite on target hosts:

* Python 3.6
* Should be K8s master (cluster api) running an active cluster

<br>

### Current features:

* Flannel
* Multus
* Kubevirt-Ovs CNI
* Intel-SRIOV CNI
* Intel-Userspace CNI

<br>

### Using:

Default run:

​	```$ docker container run parthyadav/deployer```

##### Custom Run:

* Overriding any config parameter 

  ```$ docker container run parthyadav/deployer -e action=deprovision```

  or simply mount new ```config.yml```

  ```$ docker container run -v $(pwd)/config.yml:/playbooks/config.yml parthyadav/deployer```



<br>

User can override following files by mounting to ```/playbooks```:

* ```hosts```
* ```ansible.cfg```
* ```config.yml```

```$ docker container run -v $(pwd):/playbooks parthyadav/deployer```

<br>











