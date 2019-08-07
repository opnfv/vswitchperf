##############################################################################
# Copyright (c) 2016 HUAWEI TECHNOLOGIES CO.,LTD and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
"""
Preload the results database with testcases.
"""

from __future__ import print_function
import json
import sys
import requests

DB_HOST_IP = sys.argv[1]
TESTAPI_PORT = sys.argv[2]

TARGET_URL = 'http://{}:{}/api/v1'.format(DB_HOST_IP, TESTAPI_PORT)


def get(url):
    """
    Get the http response.
    """
    return requests.get(url).json()


def post(url, data):
    """
    Post HTTP request.
    """
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url, data=json.dumps(data), headers=headers)
    print(res.text)


def pod():
    """
    Get the PODs.
    """
    target = '{}/pods'.format(TARGET_URL)

    with open('pods.json', 'r') as podref:
        pods = json.load(podref)
    for apod in pods:
        post(target, apod)

    add_pod('master', 'metal')
    add_pod('virtual_136_2', 'virtual')


def project():
    """
    Get the Projects
    """
    target = '{}/projects'.format(TARGET_URL)
    with open('projects.json', 'r') as projref:
        projects = json.load(projref)
    for proj in projects:
        post(target, proj)


def cases():
    """
    Get the Cases
    """
    with open('cases.json', 'r') as caseref:
        for line in caseref:
            subcases = json.loads(line)
            for cas in subcases["testcases"]:
                target = '{}/projects/{}/cases'.format(TARGET_URL,
                                                       cas['project_name'])
                post(target, cas)
    add_case("functest", "tempest_custom")


def add_pod(name, mode):
    """
    Add the Pods.
    """
    data = {
        "role": "",
        "name": name,
        "details": '',
        "mode": mode,
        "creation_date": "2017-2-23 11:23:03.765581"
    }
    pod_url = '{}/pods'.format(TARGET_URL)
    post(pod_url, data)


def add_case(projectname, casename):
    """
    Add a testcase
    """
    data = {
        "project_name": projectname,
        "name": casename,
    }
    case_url = '{}/projects/{}/cases'.format(TARGET_URL, projectname)
    post(case_url, data)


if __name__ == '__main__':
    pod()
    project()
    cases()
