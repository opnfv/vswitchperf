FROM python:3.6.10-slim-buster
MAINTAINER Parth Yadav <parthyadav3105@gmail.com>

ENV ANSIBLE_VERSION 2.9.6

RUN apt update -y && apt install sshpass -y
RUN pip install ansible==${ANSIBLE_VERSION}
RUN pip install openshift

# Envirnoment variable path is the first location ansible searches ansible.cfg
# Override ansible.cfg from /deployer with /playbooks
ENV ANSIBLE_CONFIG /playbooks

WORKDIR /deployer
ADD ./roles /deployer/roles
ADD ansible.cfg .
ADD config.yml .
ADD main.yml .
                  
ENTRYPOINT ["ansible-playbook", "-i", "/playbooks/", "main.yml" ]

