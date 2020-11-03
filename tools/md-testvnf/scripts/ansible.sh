#!/bin/bash -eux
yum -y update
# Install EPEL repository.
yum -y install epel-release

# Install Ansible.
yum -y install ansible