====================
Metrics Dev Guide
====================
Table of Contents
=================
.. contents::
.. section-numbering::


Anible File Organization
============================

Anisble-Server
----------------

Pleae follow the following file structure:

.. code-block:: bash

    ansible-server
    |   ansible.cfg
    |   hosts
    |   
    +---group_vars
    |       all.yml
    |       
    +---playbooks
    |       clean.yaml
    |       setup.yaml
    |       
    \---roles
    +---clean-monitoring
    |   \---tasks
    |           main.yml
    |           
    +---monitoring
        +---files
        |   |   monitoring-namespace.yaml
        |   |   
        |   +---alertmanager
        |   |       alertmanager-config.yaml
        |   |       alertmanager-deployment.yaml
        |   |       alertmanager-service.yaml
        |   |       alertmanager1-deployment.yaml
        |   |       alertmanager1-service.yaml
        |   |       
        |   +---cadvisor
        |   |       cadvisor-deamonset.yaml
        |   |       cadvisor-service.yaml
        |   |       
        |   +---collectd-exporter
        |   |       collectd-exporter-deployment.yaml
        |   |       collectd-exporter-service.yaml
        |   |       
        |   +---grafana
        |   |       grafana-datasource-config.yaml
        |   |       grafana-deployment.yaml
        |   |       grafana-pv.yaml
        |   |       grafana-pvc.yaml
        |   |       grafana-service.yaml
        |   |       
        |   +---kube-state-metrics
        |   |       kube-state-metrics-deployment.yaml
        |   |       kube-state-metrics-service.yaml
        |   |       
        |   +---node-exporter
        |   |       nodeexporter-daemonset.yaml
        |   |       nodeexporter-service.yaml
        |   |       
        |   \---prometheus
        |           main-prometheus-service.yaml
        |           prometheus-config.yaml
        |           prometheus-deployment.yaml
        |           prometheus-pv.yaml
        |           prometheus-pvc.yaml
        |           prometheus-service.yaml
        |           prometheus1-deployment.yaml
        |           prometheus1-service.yaml
        |           
        \---tasks
               main.yml


Ansible - Client
------------------

Pleae follow the following file structure:

.. code-block:: bash

    ansible-server
    |   ansible.cfg
    |   hosts
    |   
    +---group_vars
    |       all.yml
    |       
    +---playbooks
    |       clean.yaml
    |       setup.yaml
    |       
    \---roles
        +---clean-collectd
        |   \---tasks   
        |           main.yml
        |       
        +---collectd
            +---files
            |       collectd.conf.j2
            |       
            \---tasks
                    main.yml


Summary of Roles
==================

A brief description of the anisble playbook roles,
which are used to deploy the  monitoring cluster

Anisble Server Roles
----------------------

Ansible Server, this part consists of the roles used to deploy 
Prometheus Alertmanager Grafana stack on the server side 

Role: Monitoring 
~~~~~~~~~~~~~~~~~~

Deployment and configuration of PAG stack along with collectd-exporter, 
cadvisor and node-exporter.

Role: Clean-Monitoring 
~~~~~~~~~~~~~~~~~~~~~~~~

Removes all the components deployed by Monitoring role.


File-Task Mapping and Configurable Parameters
================================================

Anisble Server
----------------

Role: Monitoring 
~~~~~~~~~~~~~~~~~~~

Alert Manager
^^^^^^^^^^^^^^^

File: alertmanager-config.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/alertmanager/alertmanager-config.yaml

Task: Configures Receivers for alertmanager

Summary: A configmap, currently configures webhook for alertmanager,
can be used to configure any kind of receiver

Configureable Parameters: 
    receiver.url: change to the webhook receiver's url
    route: Can be used to add receivers                           


File: alertmanager-deployment.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/alertmanager/alertmanager-deployment.yaml

Task: Deploys alertmanager instance

Summary: A Deployment, deploys 1 replica of alertmanager 


File: alertmanager-service.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/alertmanager/alertmanager-service.yaml

Task: Creates a K8s service for alertmanager

Summary: A Nodeport type of service, so that user can craete "silences",
view the status of alerts from the native alertmanager dashboard / UI.

Configurable Parameters: 
    spec.type: Options : NodePort, ClusterIP, LoadBalancer
    spec.ports: Edit / add ports to be handled by the service

**Note: alertmanager1-deployment, alertmanager1-service are same as 
alertmanager-deployment and alertmanager-service respectively.**

CAdvisor
^^^^^^^^^^^

File: cadvisor-deamonset.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/cadvisor/cadvisor-deamonset.yaml

Task: To create a cadvisor deamonset 

Summary: A deamonset, used to scrape data of the kubernetes cluster itself, 
its a deamonset so an instance is run on every node.

Configurable Parameters: 
    spec.template.spec.ports: Port of the container


File: cadvisor-service.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/cadvisor/cadvisor-service.yaml

Task: To create a cadvisor service 

Summary: A ClusterIP service for cadvisor to communicate with prometheus

Configurable Parameters: 
    spec.ports: Add / Edit ports


Collectd Exporter
^^^^^^^^^^^^^^^^^^^^

File: collectd-exporter-deployment.yaml
''''''''''''''''''''''''''''''''''''''''''
Path : monitoring/files/collectd-exporter/collectd-exporter-deployment.yaml

Task: To create a collectd replica 

Summary: A deployment, acts as receiver for collectd data sent by client machines,
prometheus pulls data from this exporter 

Configurable Parameters: 
    spec.template.spec.ports: Port of the container


File: collectd-exporter.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/collectd-exporter/collectd-exporter.yaml

Task: To create a collectd service

Summary: A NodePort service for collectd-exporter to hold data for prometheus 
to scrape

Configurable Parameters: 
    spec.ports: Add / Edit ports


Grafana
^^^^^^^^^

File: grafana-datasource-config.yaml
''''''''''''''''''''''''''''''''''''''''''
Path : monitoring/files/grafana/grafana-datasource-config.yaml

Task: To create config file for grafana 

Summary: A configmap, adds prometheus datasource in grafana 


File: grafana-deployment.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/grafana/grafana-deployment.yaml

Task: To create a grafana deployment

Summary: The grafana deployment creates a single replica of grafana, 
with preconfigured prometheus datasource.

Configurable Parameters: 
    spec.template.spec.ports: Edit ports
    spec.template.spec.env: Add / Edit environment variables


File: grafana-pv.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/grafana/grafana-pv.yaml

Task: To create a presistent volume for grafana

Summary: A presistent volume for grafana. 

Configurable Parameters: 
    spec.capacity.storage: Increase / decrease size
    spec.accessModes: To change the way PV is accessed.
    spec.nfs.server: To change the ip address of NFS server
    spec.nfs.path: To change the path of the server


File: grafana-pvc.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/grafana/grafana-pvc.yaml

Task: To create a presistent volume claim for grafana

Summary: A presistent volume claim for grafana. 

Configurable Parameters: 
    spec.resources.requests.storage: Increase / decrease size


File: grafana-service.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/grafana/grafana-service.yaml

Task: To create a service for grafana

Summary: A Nodeport type of service, so that users actually connect to,
view the dashboard / UI.

Configurable Parameters: 
    spec.type: Options : NodePort, ClusterIP, LoadBalancer
    spec.ports: Edit / add ports to be handled by the service
    

Kube State Metrics
^^^^^^^^^^^^^^^^^^^^

File: kube-state-metrics-deployment.yaml
''''''''''''''''''''''''''''''''''''''''''
Path : monitoring/files/kube-state-metrics/kube-state-metrics-deployment.yaml

Task: To create a kube-state-metrics instance

Summary: A deployment, used to collect metrics of the kubernetes cluster iteself 

Configurable Parameters: 
    spec.template.spec.containers.ports: Port of the container


File: kube-state-metrics-service.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/kube-state-metrics/kube-state-metrics-service.yaml

Task: To create a collectd service

Summary: A NodePort service for collectd-exporter to hold data for prometheus 
to scrape

Configurable Parameters: 
    spec.ports: Add / Edit ports


Node Exporter
^^^^^^^^^^^^^^^

File: node-exporter-deamonset.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/node-exporter/node-exporter-deamonset.yaml

Task: To create a node exporter deamonset 

Summary: A deamonset, used to scrape data of the host machines / node, 
its a deamonset so an instance is run on every node.

Configurable Parameters:
    spec.template.spec.ports: Port of the container


File: node-exporter-service.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/node-exporter/node-exporter-service.yaml

Task: To create a node exporter service 

Summary: A ClusterIP service for node exporter to communicate with prometheus

Configurable Parameters:
    spec.ports: Add / Edit ports


Prometheus
^^^^^^^^^^^^^

File: prometheus-config.yaml
''''''''''''''''''''''''''''''''''''''''''
Path : monitoring/files/prometheus/prometheus-config.yaml

Task: To create config file for prometheus 

Summary: A configmap, adds alert rules.

Configurable Parameters:
    data.alert.rules: Add / Edit alert rules


File: prometheus-deployment.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/prometheus/prometheus-deployment.yaml

Task: To create a prometheus deployment

Summary: The prometheus deployment creates a single replica of prometheus, 
with preconfigured prometheus datasource.

Configurable Parameters: 
    spec.template.spec.affinity: To change the node affinity, 
                                 make sure only 1 instance of prometheus is 
                                 running on 1 node.

    spec.template.spec.ports: Add / Edit container port


File: prometheus-pv.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/prometheus/prometheus-pv.yaml

Task: To create a presistent volume for prometheus

Summary: A presistent volume for prometheus. 

Configurable Parameters: 
    spec.capacity.storage: Increase / decrease size
    spec.accessModes: To change the way PV is accessed.
    spec.hostpath.path: To change the path of the volume


File: prometheus-pvc.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/prometheus/prometheus-pvc.yaml

Task: To create a presistent volume claim for prometheus

Summary: A presistent volume claim for prometheus. 

Configurable Parameters: 
    spec.resources.requests.storage: Increase / decrease size


File: prometheus-service.yaml
'''''''''''''''''''''''''''''''''
Path : monitoring/files/prometheus/prometheus-service.yaml

Task: To create a service for prometheus

Summary: A Nodeport type of service, prometheus native dashboard 
available here.

Configurable Parameters: 
    spec.type: Options : NodePort, ClusterIP, LoadBalancer
    spec.ports: Edit / add ports to be handled by the service
    

File: main-prometheus-server.yaml
'''''''''''''''''''''''''''''''''''
Path: monitoring/files/prometheus/main-prometheus-service.yaml

Task: A service which connects both prometheus instances.

Summary: A Nodeport service for other services to connect to prometheus cluster.
As HA prometheus needs to independent instances of prometheus scapring the same inputs
having the same configuration

**Note: prometheus-deployment, prometheus1-service are same as 
prometheus-deployment and prometheus-service respectively.**


Anisble Client Roles
----------------------

Role: Collectd 
~~~~~~~~~~~~~~~~~~

File: main.yml
^^^^^^^^^^^^^^^^
Path: collectd/tasks/main.yaml

Task: Install collectd along with prerequisites

Associated template file:

- collectd.conf.j2 
Path: collectd/files/collectd.conf.j2

Summary: Edit this file to change the default configuration to 
be installed on client's machine
