# Copyright 2018-19 Spirent Communications.
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

# pylint: disable=R0902
# Sixteen is reasonable instance attributes
# pylint: disable=W0221
"""
VSPER docker-controller.
"""

import io
import time
from concurrent import futures
import grpc

from proto import vsperf_pb2
from proto import vsperf_pb2_grpc
from utils import ssh

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


# pylint: disable=too-few-public-methods,no-self-use
class PseudoFile(io.RawIOBase):
    """
    Handle ssh command output.
    """

    def write(self, chunk):
        """
        Write to file
        """
        if "error" in chunk:
            return
        with open("./output.txt", "a") as fref:
            fref.write(chunk)


class VsperfController(vsperf_pb2_grpc.ControllerServicer):
    """
    Main Controller Class
    """

    def __init__(self):
        """
        Initialization
        """
        self.client = None
        self.dut = None
        self.dut_check = None
        self.tgen_check = None
        self.user = None
        self.pwd = None
        self.tgen_client = None
        self.tgen = None
        self.tgen_user = None
        self.tgenpwd = None
        self.tgen_conf = None
        self.scenario = None
        self.hpmax = None
        self.hprequested = None
        self.tgen_ip_address = None
        self.trex_conf = None
        # Default TGen is T-Rex
        self.trex_conffile = "trex_cfg.yml"
        self.collectd_conffile = "collectd.conf"

    def setup(self):
        """
        Performs Setup of the client.
        """
        # Just connect to VM.
        self.client = ssh.SSH(host=self.dut, user=self.user,
                              password=self.pwd)
        self.client.wait()

    def install_vsperf(self):
        """
        Perform actual installation
        """
        download_cmd = "git clone https://gerrit.opnfv.org/gerrit/vswitchperf"
        self.client.run(download_cmd)
        install_cmd = "cd vswitchperf/systems ; "
        install_cmd += "echo '{}' | sudo -S ./build_base_machine.sh ".format(
            self.pwd)
        #install_cmd += "./build_base_machine.sh"
        self.client.run(install_cmd)

    def VsperfInstall(self, request, context):
        """
        Handle VSPERF install command from client
        """
        # print("Installing VSPERF")
        if self.dut_check != 0:
            return vsperf_pb2.StatusReply(message="DUT-Host is not Connected [!]" \
                                                   "\nMake sure to establish connection with" \
                                                   " DUT-Host.")
        vsperf_check_cmd = "source ~/vsperfenv/bin/activate ; cd vswitchperf* && ./vsperf --help"
        vsperf_check_cmd_result = str(self.client.execute(vsperf_check_cmd)[1])
        vsperf_verify_list = [
            'usage',
            'positional arguments',
            'optional arguments',
            'test selection options',
            'test behavior options']
        for idx, i in enumerate(vsperf_verify_list, start=1):
            if str(i) in vsperf_check_cmd_result:
                if idx < 5:
                    continue
                elif idx == 5:
                    return vsperf_pb2.StatusReply(
                        message="VSPERF is Already Installed on DUT-Host")
        self.install_vsperf()
        return vsperf_pb2.StatusReply(message="VSPERF Successfully Installed DUT-Host")

    def HostConnect(self, request, context):
        """
        Handle host connectivity command from client
        """
        self.dut = request.ip
        self.user = request.uname
        self.pwd = request.pwd
        self.setup()
        check_cmd = "ls -l"
        self.dut_check = int(self.client.execute(check_cmd)[0])
        return vsperf_pb2.StatusReply(message="Successfully Connected")

    def save_chunks_to_file(self, chunks, filename):
        """
        Write the output to file
        """
        with open(filename, 'wb') as fref:
            for chunk in chunks:
                fref.write(chunk.Content)

###### Traffic Generator Related functions ####
    def TGenHostConnect(self, request, context):
        """
        Connect to TGen-Node
        """
        self.tgen = request.ip
        self.tgen_user = request.uname
        self.tgenpwd = request.pwd
        self.tgen_setup()
        check_tgen_cmd = "ls"
        self.tgen_check = int(self.tgen_client.execute(check_tgen_cmd)[0])
        return vsperf_pb2.StatusReply(message="Successfully Connected")

    def tgen_setup(self):
        """
        Setup the T-Gen Client
        """
        # Just connect to VM.
        self.tgen_client = ssh.SSH(host=self.tgen, user=self.tgen_user,
                                   password=self.tgenpwd)
        self.tgen_client.wait()

    def TGenInstall(self, request, context):
        """
        Install Traffic generator on the node.
        """
        if self.tgen_check != 0:
            return vsperf_pb2.StatusReply(message="TGen-Host is not Connected [!]" \
                                                   "\nMake sure to establish connection with" \
                                                   " TGen-Host.")
        kill_cmd = "pkill -f t-rex"
        self.tgen_client.send_command(kill_cmd)
        tgen_start_cmd = "cd trex_2.37/scripts && ./t-rex-64 -f cap2/dns.yaml -d 100 -m 1 --nc"
        tgen_start_cmd_result = int(self.tgen_client.execute(tgen_start_cmd)[0])
        kill_cmd = "pkill -f t-rex"
        self.tgen_client.send_command(kill_cmd)
        if tgen_start_cmd_result == 0:
            return vsperf_pb2.StatusReply(
                message="Traffic Generetor has T-rex Installed")
        download_cmd = "git clone https://github.com/cisco-system-traffic-generator/trex-core"
        self.tgen_client.run(download_cmd)
        install_cmd = "cd trex-core/linux_dpdk ; ./b configure ; ./b build"
        self.tgen_client.run(install_cmd)
        # before you setup your trex_cfg.yml make sure to do sanity check
        # NIC PICs and establish route between your DUT and Test Device.
        return vsperf_pb2.StatusReply(message="Traffic Generetor has now T-rex Installed")

    def TGenUploadConfigFile(self, request, context):
        """
        Handle upload config-file command from client
        """
        if self.tgen_check != 0:
            return vsperf_pb2.StatusReply(message="TGen-Host is not Connected [!]" \
                                                   "\nMake sure to establish connection with" \
                                                   " TGen-Host.")
        filename = self.trex_conffile
        self.save_chunks_to_file(request, filename)
        check_trex_config_cmd = "echo {} | sudo -S find /etc -maxdepth 1 -name trex_cfg.yaml".\
                                 format(self.tgenpwd)
        check_test_result = str(
            self.tgen_client.execute(check_trex_config_cmd)[1])
        if "trex_cfg.yaml" in check_test_result:
            self.tgen_client.run("rm -f /etc/trex_cfg.yaml")
        self.upload_tgen_config()
        self.tgen_client.run(
            "echo {} | sudo -S mv ~/trex_cfg.yaml /etc/".format(self.tgenpwd), pty=True)
        return vsperf_pb2.UploadStatus(Message="Successfully Uploaded",
                                       Code=1)

    def upload_tgen_config(self):
        """
        Perform file upload.
        """
        self.tgen_client.put_file(self.trex_conffile, '/root/trex_cfg.yaml')

# Tool-Chain related Functions####3

    def install_collectd(self):
        """
        installation of the collectd
        """
        check_collectd_config_cmd = "find /opt -maxdepth 1 -name 'collectd'"
        check_test_result = str(
            self.client.execute(check_collectd_config_cmd)[1])
        if "collectd" in check_test_result:
            pass
        else:
            download_cmd = "git clone https://github.com/collectd/collectd.git"
            self.client.run(download_cmd)
            build_cmd = "cd collectd ; "
            build_cmd += "./build.sh"
            self.client.run(build_cmd)
            config_cmd = "cd collectd ; ./configure --enable-syslog "
            config_cmd += "--enable-logfile --enable-hugepages --enable-debug ; "
            self.client.run(config_cmd)
            install_cmd = "cd collectd ; make ; "
            install_cmd += "echo '{}' | sudo -S make install".format(self.pwd)
            self.client.run(install_cmd, pty=True)

    def CollectdInstall(self, request, context):
        """
        Install Collectd on DUT
        """
        if self.dut_check != 0:
            return vsperf_pb2.StatusReply(message="DUT-Host is not Connected [!]" \
                                                   "\nMake sure to establish connection with" \
                                                   " DUT-Host.")
        self.install_collectd()
        return vsperf_pb2.StatusReply(
            message="Collectd Successfully Installed on DUT-Host")

    def upload_collectd_config(self):
        """
        Perform file upload.
        """
        self.client.put_file(self.collectd_conffile, '~/collectd.conf')
        move_cmd = "echo '{}' | sudo -S mv ~/collectd.conf /opt/collectd/etc".format(
            self.pwd)
        self.client.run(move_cmd, pty=True)

    def CollectdUploadConfig(self, request, context):
        """
        Upload collectd config-file on DUT
        """
        if self.dut_check != 0:
            return vsperf_pb2.StatusReply(message="DUT-Host is not Connected [!]" \
                                                   "\nMake sure to establish connection with" \
                                                   " DUT-Host.")
        filename = self.collectd_conffile
        self.save_chunks_to_file(request, filename)
        self.upload_collectd_config()
        return vsperf_pb2.UploadStatus(
            Message="Successfully Collectd Configuration Uploaded", Code=1)

###System Configuration related functions###

    def DutHugepageConfig(self, request, context):
        """
        Configure the DUT system hugepage parameter from client
        """
        if self.dut_check != 0:
            return vsperf_pb2.StatusReply(message="DUT-Host is not Connected [!]" \
                                                   "\nMake sure to establish connection with" \
                                                   " DUT-Host.")
        self.hpmax = int(request.hpmax)
        self.hprequested = int(request.hprequested)
        hugepage_cmd = "echo '{}' | sudo -S mkdir -p /mnt/huge ; ".format(
            self.pwd)
        hugepage_cmd += "echo '{}' | sudo -S mount -t hugetlbfs nodev /mnt/huge".format(
            self.pwd)
        self.client.run(hugepage_cmd, pty=True)
        hp_nr_cmd = "cat /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages"
        hp_free_cmd = "cat /sys/devices/system/node/node0/hugepages/hugepages-2048kB/free_hugepages"
        hp_nr = int(self.client.execute(hp_nr_cmd)[1])
        hp_free = int(self.client.execute(hp_free_cmd)[1])
        if hp_free <= self.hprequested:
            hp_nr_new = hp_nr + (self.hprequested - hp_free)
            if hp_nr_new > self.hpmax:
                hp_nr_new = self.hpmax

        nr_hugepage_cmd = "echo '{}' | sudo -S bash -c \"echo 'vm.nr_hugepages={}' >>".\
                           format(self.pwd, hp_nr_new)
        nr_hugepage_cmd += " /etc/sysctl.conf\""
        self.client.run(nr_hugepage_cmd, pty=True)

        dict_cmd = "cat /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages"
        dict_check = int(self.client.execute(dict_cmd)[0])
        if dict_check == 0:
            node1_hugepage_cmd = "echo '{}' | sudo -s bash -c \"echo 0 >".format(self.pwd)
            node1_hugepage_cmd += " /sys/devices/system/node/node1/"
            node1_hugepage_cmd += "hugepages/hugepages-2048kB/nr_hugepages\""
        return vsperf_pb2.StatusReply(
            message="DUT-Host system configured with {} No of Hugepages".format(hp_nr_new))

    def CheckDependecies(self, request, context):
        """
        Check and Install required packages on DUT
        """
        if self.dut_check != 0:
            return vsperf_pb2.StatusReply(message="DUT-Host is not Connected [!]" \
                                                   "\nMake sure to establish connection with" \
                                                   " DUT-Host.")
        packages = ['python34-tkinter', 'sysstat', 'bc']
        for pkg in packages:
            # pkg_check_cmd = "dpkg -s {}".format(pkg) for ubuntu
            pkg_check_cmd = "rpm -q {}".format(pkg)
            pkg_cmd_response = self.client.execute(pkg_check_cmd)[0]
            if pkg_cmd_response == 1:
                install_pkg_cmd = "echo '{}' | sudo -S yum install -y {}".format(
                    self.pwd, pkg)
                #install_pkg_cmd = "echo '{}' | sudo -S apt-get install -y {}".format(self.pwd,pkg)
                self.client.run(install_pkg_cmd, pty=True)

        return vsperf_pb2.StatusReply(message="Python34-tkinter, sysstat and bc Packages"\
                                    "are now Installed")

def serve():
    """
    Start servicing the client
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vsperf_pb2_grpc.add_ControllerServicer_to_server(
        VsperfController(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except (SystemExit, KeyboardInterrupt, MemoryError, RuntimeError):
        server.stop(0)


if __name__ == "__main__":
    serve()
