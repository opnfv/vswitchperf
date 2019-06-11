# Copyright 2019-2020 Spirent Communications.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Retrieve information from remote host.
In this file, we retrive only NIC PICs
"""
from __future__ import print_function
import sys
import subprocess
import os
from os.path import exists
from stat import S_ISDIR
import paramiko

# The PCI device class for ETHERNET devices
ETHERNET_CLASS = "0200"
LSPCI_PATH = '/usr/bin/lspci'
RECV_BYTES = 4096
ADVANCED = True


#pylint: disable=too-many-instance-attributes
class RemoteInfo(object):
    """
    Class to extract information from a remote system
    """

    def __init__(self, host, username, password):
        """
        Perform Initialization
        """
        # Dict of ethernet devices present. Dictionary indexed by PCI address.
        # Each device within this is itself a dictionary of device properties
        self.nic_devices = {}
        print(host)
        if host == 'local':
            self.local = True
            print("setting local to true")
        else:
            self.local = False
            # Assuming port as 22.
            self.port = 22
            self.hostname = host
            self.password = password
            self.username = username
            self.client = paramiko.Transport((self.hostname, self.port))
            self.client.connect(username=self.username,
                                password=self.password)
            self.session = self.client.open_channel(kind='session')
            self.session.get_pty()
            self.sftp = paramiko.SFTPClient.from_transport(self.client)

    def sftp_exists(self, path):
        """
        Check if remote file exist
        """
        try:
            self.sftp.stat(path)
            return True
        except IOError:
            return False
        #except FileNotFoundError:
        #    return False

    def sft_listdir(self, path):
        """
        List directories on remote nost
        """
        files = []
        for fil in self.sftp.listdir_attr(path):
            if not S_ISDIR(fil.st_mode):
                files.append(fil.filename)
        return files

    def is_connected(self):
        """
        Check if session is connected.
        """
        return self.client.is_active()

    def new_channel(self):
        """
        FOr every command a new session is setup
        """
        if not self.is_connected():
            self.client = paramiko.Transport((self.hostname, self.port))
            self.client.connect(username=self.username,
                                password=self.password)
        self.session = self.client.open_channel(kind='session')

    # This is roughly compatible with check_output function in subprocess module
    # which is only available in python 2.7.
    def check_output(self, args, stderr=None):
        '''
        Run a command and capture its output
        '''
        stdout_data = []
        stderr_data = []
        if self.local:
            return subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=stderr,
                                    universal_newlines=True).communicate()[0]
        else:
            self.new_channel()
            separator = ' '
            command = separator.join(args)
            # self.session.get_pty()
            self.session.exec_command(command)
            while True:
                if self.session.recv_ready():
                    stdout_data.append(self.session.recv(RECV_BYTES))
                if self.session.recv_stderr_ready():
                    stderr_data.append(self.session.recv_stderr(RECV_BYTES))
                if self.session.exit_status_ready():
                    break
            if stdout_data:
                return b"".join(stdout_data)
            else:
                return b"".join(stderr_data)

    def get_pci_details(self, dev_id):
        '''
        This function gets additional details for a PCI device
        '''
        device = {}

        extra_info = self.check_output([LSPCI_PATH,
                                        "-vmmks", dev_id]).splitlines()

        # parse lspci details
        for line in extra_info:
            if len(line) == 0:
                continue
            if self.local:
                name, value = line.split("\t", 1)
            else:
                name, value = line.decode().split("\t", 1)
            name = name.strip(":") + "_str"
            device[name] = value
        # check for a unix interface name
        sys_path = "/sys/bus/pci/devices/%s/net/" % dev_id
        device["Interface"] = ""
        if self.local:
            if exists(sys_path):
                device["Interface"] = ",".join(os.listdir(sys_path))
        else:
            if self.sftp_exists(sys_path):
                device["Interface"] = ",".join(self.sft_listdir(sys_path))

        # check if a port is used for ssh connection
        device["Ssh_if"] = False
        device["Active"] = ""

        return device

    def get_nic_details(self):
        '''
        This function populates the "devices" dictionary. The keys used are
        the pci addresses (domain:bus:slot.func). The values are themselves
        dictionaries - one for each NIC.
        '''
        devinfos = []
        # first loop through and read details for all devices
        # request machine readable format, with numeric IDs
        dev = {}
        dev_lines = self.check_output([LSPCI_PATH, "-Dvmmn"]).splitlines()
        print(dev_lines)
        for dev_line in dev_lines:
            if len(dev_line) == 0:
                if dev["Class"] == ETHERNET_CLASS:
                    print("ADDING DEVICE")
                    # convert device and vendor ids to numbers, then add to
                    # global
                    dev["Vendor"] = int(dev["Vendor"], 16)
                    dev["Device"] = int(dev["Device"], 16)
                    self.nic_devices[dev["Slot"]] = dict(
                        dev)  # use dict to make copy of dev
            else:
                # values = re.split(r'\t+', str(dev_line))
                if self.local:
                    name, value = dev_line.split('\t', 1)
                else:
                    name, value = dev_line.decode().split("\t", 1)
                dev[name.rstrip(":")] = value

        # based on the basic info, get extended text details
        for dev in self.nic_devices.keys():
            # get additional info and add it to existing data
            if ADVANCED:
                self.nic_devices[dev].update(self.get_pci_details(dev).items())
            devinfos.append(self.nic_devices[dev])
        return devinfos

    def dev_id_from_dev_name(self, dev_name):
        '''
        Take a device "name" - a string passed in by user to identify a NIC
        device, and determine the device id - i.e. the domain:bus:slot.func-for
        it, which can then be used to index into the devices array
        '''
        # dev = None
        # check if it's already a suitable index
        if dev_name in self.nic_devices:
            return dev_name
        # check if it's an index just missing the domain part
        elif "0000:" + dev_name in self.nic_devices:
            return "0000:" + dev_name
        else:
            # check if it's an interface name, e.g. eth1
            for dev in self.nic_devices.keys():
                if dev_name in self.nic_devices[dev]["Interface"].split(","):
                    return self.nic_devices[dev]["Slot"]
        # if nothing else matches - error
        print ("Unknown device: %s. "
               "Please specify device in \"bus:slot.func\" format" % dev_name)
        sys.exit(1)


def main():
    '''program main function'''
    host = raw_input("Enter Host IP: ")
    username = raw_input("Enter User Name: ")
    pwd = raw_input("Enter Password: ")
    rhi = RemoteInfo(host, username, pwd)
    dev_list = rhi.get_nic_details()
    for dev in dev_list:
        print(dev["Slot"])


if __name__ == "__main__":
    main()
