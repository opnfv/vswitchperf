=================
Table of Contents
=================
.. contents::
.. section-numbering::

Ansible Client-side
====================

Ansible File Organisation
--------------------------
Files Structure::

    ansible-client
    ├── ansible.cfg
    ├── hosts
    ├── playbooks
    │   └── setup.yaml
    └── roles
        ├── clean-td-agent
        │   └── tasks
        │       └── main.yml
        └── td-agent
            ├── files
            │   └── td-agent.conf
            └── tasks
                └── main.yml

Summary of roles
-----------------
====================== ======================
Roles                  Description
====================== ======================
``td-agent``           Install Td-agent & change configuration file
``clean-td-agent``     Unistall Td-agent
====================== ======================

Configurable Parameters
------------------------
====================================================== ====================== ======================
File (ansible-client/roles/)                           Parameter              Description
====================================================== ====================== ======================
``td-agent/files/td-agent.conf``                       host                   Fluentd-server IP
``td-agent/files/td-agent.conf``                       port                   Fluentd-Server Port
====================================================== ====================== ======================

Ansible Server-side
====================

Ansible File Organisation
--------------------------
Files Structure::

      ansible-server
      ├── ansible.cfg
      ├── group_vars
      │   └── all.yml
      ├── hosts
      ├── playbooks
      │   └── setup.yaml
      └── roles
          ├── clean-logging
          │   └── tasks
          │       └── main.yml
          ├── k8s-master
          │   └── tasks
          │       └── main.yml
          ├── k8s-pre
          │   └── tasks
          │       └── main.yml
          ├── k8s-worker
          │   └── tasks
          │       └── main.yml
          ├── logging
          │   ├── files
          │   │   ├── elastalert
          │   │   │   ├── ealert-conf-cm.yaml
          │   │   │   ├── ealert-key-cm.yaml
          │   │   │   ├── ealert-rule-cm.yaml
          │   │   │   └── elastalert.yaml
          │   │   ├── elasticsearch
          │   │   │   ├── elasticsearch.yaml
          │   │   │   └── user-secret.yaml
          │   │   ├── fluentd
          │   │   │   ├── fluent-cm.yaml
          │   │   │   ├── fluent-service.yaml
          │   │   │   └── fluent.yaml
          │   │   ├── kibana
          │   │   │   └── kibana.yaml
          │   │   ├── namespace.yaml
          │   │   ├── nginx
          │   │   │   ├── nginx-conf-cm.yaml
          │   │   │   ├── nginx-key-cm.yaml
          │   │   │   ├── nginx-service.yaml
          │   │   │   └── nginx.yaml
          │   │   ├── persistentVolume.yaml
          │   │   └── storageClass.yaml
          │   └── tasks
          │       └── main.yml
          └── nfs
              └── tasks
                  └── main.yml

Summary of roles
-----------------
====================== ======================
Roles                  Description
====================== ======================
``k8s-pre``            Pre-requisite for installing K8s, like installing docker & K8s, disable swap etc.
``k8s-master``         Reset K8s & make a master
``k8s-worker``         Join woker nodes with token
``logging``            EFK & elastalert setup in K8s
``clean logging``      Remove EFK & elastalert setup from K8s
``nfs``                Start a NFS server to store Elasticsearch data
====================== ======================

Configurable Parameters
------------------------
========================================================================= ============================================ ======================
File (ansible-server/roles/)                                              Parameter name                               Description
========================================================================= ============================================ ======================
**Role: logging**
``logging/files/persistentVolume.yaml``                                   storage                                      Increase or Decrease Storage size of Persistent Volume size for each VM
``logging/files/kibana/kibana.yaml``                                      version                                      To Change the Kibana Version
``logging/files/kibana/kibana.yaml``                                      count                                        To increase or decrease the replica
``logging/files/elasticsearch/elasticsearch.yaml``                        version                                      To Change the Elasticsearch Version
``logging/files/elasticsearch/elasticsearch.yaml``                        nodePort                                     To Change Service Port
``logging/files/elasticsearch/elasticsearch.yaml``                        storage                                      Increase or Decrease Storage size of Elasticsearch data for each VM
``logging/files/elasticsearch/elasticsearch.yaml``                        nodeAffinity -> values (hostname)              In which VM Elasticsearch master or data pod will run (change the hostname to run the Elasticsearch master or data pod on a specific node)
``logging/files/elasticsearch/user-secret.yaml``                          stringData                                   Add Elasticsearch User & its roles (`Elastic Docs <https://www.elastic.co/guide/en/cloud-on-k8s/master/k8s-users-and-roles.html#k8s_file_realm>`_)
``logging/files/fluentd/fluent.yaml``                                     replicas                                     To increase or decrease the replica
``logging/files/fluentd/fluent-service.yaml``                             nodePort                                     To Change Service Port
``logging/files/fluentd/fluent-cm.yaml``                                  index_template.json -> number_of_replicas    To increase or decrease replica of data in Elasticsearch
``logging/files/fluentd/fluent-cm.yaml``                                  fluent.conf                                  Server port & other Fluentd Configuration
``logging/files/nginx/nginx.yaml``                                        replicas                                     To increase or decrease the replica
``logging/files/nginx/nginx-service.yaml``                                nodePort                                     To Change Service Port
``logging/files/nginx/nginx-key-cm.yaml``                                 kibana-access.key, kibana-access.pem         Key file for HTTPs Connection
``logging/files/nginx/nginx-conf-cm.yaml``                                -                                            Nginx Configuration
``logging/files/elastalert/elastalert.yaml``                              replicas                                     To increase or decrease the replica
``logging/files/elastalert/ealert-key-cm.yaml``                           elastalert.key, elastalert.pem               Key file for HTTPs Connection
``logging/files/elastalert/ealert-conf-cm.yaml``                          run_every                                    How often ElastAlert will query Elasticsearch
``logging/files/elastalert/ealert-conf-cm.yaml``                          alert_time_limit                             If an alert fails for some reason, ElastAlert will retry sending the alert until this time period has elapsed
``logging/files/elastalert/ealert-conf-cm.yaml``                          es_host, es_port                             Elasticsearch Serivce name & port in K8s
``logging/files/elastalert/ealert-rule-cm.yaml``                          http_post_url                                Alert Receiver IP (`Elastalert Rule Config <https://elastalert.readthedocs.io/en/latest/ruletypes.html>`_)
**Role: nfs**
``nfs/tasks/main.yml``                                                    line                                         Path of NFS storage
========================================================================= ============================================ ======================
