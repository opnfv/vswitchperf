# OPNFV - k8s cluster setup

This project aims to set up and programmatically deploy a Kubernetes cluster on CentOS 7 machines with the help of Kubeadm. It uses ansible and requires very little intervention.

## Getting Started
The following steps aim to describe the minimum required to successfully run this script.


### Prerequisites

Kubernetes and Ansible should be installed on the master node and docker and kubelet services should be running.

Hardware prerequisites as suggested by Kubernetes documentation:

-   Master node's minimal  **required**  memory is 2GB and the worker node needs minimum 1GB.
-   The master node needs at least 1.5 cores and the worker node needs at least 0.7 cores.

### Setup
In order the configure the cluster, we'll need to modify the `hosts` and `env_variable` file. The `hosts` file has the following structure:

```
[master]
master ansible_host=10.10.120.22 ansible_connection=local ansible_user=opnfv ansible_password=opnfv
#master ansible_host=10.10.120.22 ansible_connection=ssh ansible_ssh_user=opnfv ansible_ssh_pass=opnfv ansible_ssh_common_args='-o StrictHostKeyChecking=no'

[worker]
worker ansible_host=10.10.120.21 ansible_connection=ssh ansible_ssh_user=opnfv ansible_ssh_pass=opnfv ansible_ssh_common_args='-o StrictHostKeyChecking=no'

```
In this configuration file, connection details should be filled in. In case more nodes within the cluster are needed, add lines as necessary to the worker group within the `hosts` file.

In the `env_variables` file the following parameters should be entered as per your environment

ad_addr: 10.10.120.22
cidr_v: 10.244.0.0/16

In ad_addr enter your master node advertise ip address and in cidr_v your cidr range for the pods.

### Usage
In order to use the script, download or clone the repository to the root of what will be the master node.

Navigate to its contents and execute the following command as regular user (this will prevent errors throughout configuration and deployment) on whichever machine you wish to use as the master node (this host will be the one running kubectl):

```
ansible-playbook settingup_k8s_cluster.yml
```
You can verify the installation by running:
```
kubectl get nodes
```
And verifying the readiness of the nodes. More information may be obtained with `kubectl describe nodes` if needed.

To clear the cluster, execute the following command
ansible-playbook clear_k8s_cluster.yml

### Debugging
In case a step goes wrong within the installation, ansible should display a message, however, there's also files to debug if the installation had something to do within k8s. In the case of the master node, we should be able to find a `log_init.txt` with necessary logs. On worker nodes, the relevant file is `node_joined.txt`.
