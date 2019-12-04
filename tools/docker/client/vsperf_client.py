"""Deploy : vsperf_deploy_client"""
#pylint: disable=import-error

import configparser
import sys
from pathlib import Path


import grpc
from proto import vsperf_pb2
from proto import vsperf_pb2_grpc

CHUNK_SIZE = 1024 * 1024  # 1MB


HEADER = r"""
 _  _  ___  ____  ____  ____  ____     ___  __    ____  ____  _  _  ____
( \/ )/ __)(  _ \( ___)(  _ \( ___)   / __)(  )  (_  _)( ___)( \( )(_  _)
 \  / \__ \ )___/ )__)  )   / )__)   ( (__  )(__  _)(_  )__)  )  (   )(
  \/  (___/(__)  (____)(_)\_)(__)     \___)(____)(____)(____)(_)\_) (__)
"""

COLORS = {
    'blue': '\033[94m',
    'pink': '\033[95m',
    'green': '\033[92m',
}

DUT_CHECK = 0
TGEN_CHECK = 0

def colorize(string, color):
    """Colorized HEADER"""
    if color not in COLORS:
        return string
    return COLORS[color] + string + '\033[0m'


class VsperfClient():
    """
    This class reprsents the VSPERF-client.
    It talks to vsperf-docker to perform installation, configuration and
    test-execution
    """
    # pylint: disable=R0904,no-else-break
    # pylint: disable=W0603,invalid-name
    # pylint: disable=R1710
    def __init__(self):
        """read vsperfclient.conf"""
        self.cfp = 'vsperfclient.conf'
        self.config = configparser.RawConfigParser()
        self.config.read(self.cfp)
        self.stub = None
        self.dut_check = 0
        self.tgen_check = 0
    
    def get_mode(self):
    	"""read the mode for the client"""
    	return self.config.get('Mode', 'mode')

    def get_deploy_channel_info(self):
        """get the channel data"""
        return (self.config.get('DeployServer', 'ip'),
                self.config.get('DeployServer', 'port'))

    def get_test_channel_info(self):
        """get the channel for tgen"""
        return (self.config.get('TestServer', 'ip'),
                self.config.get('TestServer', 'port'))

    def create_stub(self, channel):
        """create stub to talk to controller"""
        self.stub = vsperf_pb2_grpc.ControllerStub(channel)
    
    def host_connect(self):
        """provice dut-host credential to controller"""
        global DUT_CHECK
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        connect_reply = self.stub.HostConnect(hostinfo)
        DUT_CHECK = 1
        print(connect_reply.message)

    def tgen_connect(self):
        """provide tgen-host credential to controller"""
        global TGEN_CHECK
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        connect_reply = self.stub.TGenHostConnect(tgeninfo)
        TGEN_CHECK = 1
        print(connect_reply.message)

    def host_connect_both(self):
        """provice dut-host credential to controller"""
        global DUT_CHECK
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        connect_reply = self.stub.HostConnect(hostinfo)
        client = VsperfClient()
        client.automatically_test_dut_connect()
        DUT_CHECK = 1
        print(connect_reply.message)

    def tgen_connect_both(self):
        """provide tgen-host credential to controller"""
        global TGEN_CHECK
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        connect_reply = self.stub.TGenHostConnect(tgeninfo)
        TGEN_CHECK = 1
        client = VsperfClient()
        client.automatically_test_tgen_connect()
        print(connect_reply.message)

    @classmethod
    def automatically_test_dut_connect(cls):
        """handle automatic connection with tgen"""
        client = VsperfClient()
        ip_add, port = client.get_test_channel_info()
        channel = grpc.insecure_channel(ip_add + ':' + port)
        client.create_stub(channel)
        client.host_testcontrol_connect()

    @classmethod
    def automatically_test_tgen_connect(cls):
        """handle automatic connection with tgen"""
        client = VsperfClient()
        ip_add, port = client.get_test_channel_info()
        channel = grpc.insecure_channel(ip_add + ':' + port)
        client.create_stub(channel)
        client.tgen_testcontrol_connect()

    def exit_section(self):
        """exit"""
    @classmethod
    def section_execute(cls, menuitems, client, ip_add, port):
        """it will use to enter into sub-option"""
        channel = grpc.insecure_channel(ip_add + ':' + port)

        while True:
            client.create_stub(channel)
            while True:
                # os.system('clear')
                print(colorize(HEADER, 'blue'))
                print(colorize('version 0.1\n', 'pink'))
                for item in menuitems:
                    print(colorize("[" +
                                   str(menuitems.index(item)) + "]", 'green') +
                          list(item.keys())[0])
                choice = input(">> ")
                try:
                    if int(choice) < 0:
                        raise ValueError
                    if (int(choice) >= 0) and (int(choice) < (len(menuitems) - 1)):
                        list(menuitems[int(choice)].values())[0]()
                    else:
                        break
                except (ValueError, IndexError):
                    pass
            break
    @classmethod
    def get_user_trex_conf_location(cls):
        """Ask user for t-rex configuration location"""
        while True:
            filename_1 = str(input("Provide correct location for your t-rex configuration " \
                                     "file where trex_cfg.yaml exist\n" \
                                     "***************** Make Sure You Choose Correct" \
                                     " File for Upload*******************\n" \
                                     "Provide location: \n"))
            user_file = Path("{}".format(filename_1.strip()))
            if user_file.is_file():
                break
            else:
                print("**************File Does Not Exist*****************\n")
                continue
        return filename_1

    def upload_tgen_config(self):
        """t-rex config file as a chunk to controller"""
        if TGEN_CHECK == 0:
            return print("TGen-Host is not Connected [!]" \
                         "\nMake sure to establish connection with TGen-Host.")
        default_location = self.config.get('ConfFile', 'tgenpath')
        if not default_location:
            filename = self.get_user_trex_conf_location()
        else:
            user_preference = str(input("Use location specified in vsperfclient.conf?[Y/N] :"))
            while True:
                if 'y' in user_preference.lower().strip():
                    filename = self.config.get('ConfFile', 'tgenpath')
                    user_file = Path("{}".format(filename.strip()))
                    if user_file.is_file():
                        break
                    else:
                        print("**************File Does Not Exist*****************\n")
                        user_preference = 'n'
                        continue
                elif 'n' in user_preference.lower().strip():
                    filename = self.get_user_trex_conf_location()
                    break
                else:
                    print("Invalid Input")
                    user_preference = str(input("Use location specified in vsperfclient.conf?" \
                                                "[Y/N] : "))
                    continue
        filename = filename.strip()
        chunks = self.get_file_chunks_1(filename)
        upload_status = self.stub.TGenUploadConfigFile(chunks)
        print(upload_status.Message)

    def vsperf_install(self):
        """vsperf install on dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        install_reply = self.stub.VsperfInstall(hostinfo)
        print(install_reply.message)

    def collectd_install(self):
        """collectd install on dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        install_reply = self.stub.CollectdInstall(hostinfo)
        print(install_reply.message)

    def tgen_install(self):
        """install t-rex on Tgen host"""
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        install_reply = self.stub.TGenInstall(tgeninfo)
        print(install_reply.message)

    @classmethod
    def get_user_conf_location(cls):
        """get user input for test configuration file"""
        while True:
            filename_1 = str(input("Provide correct location for your test configuration " \
                                     "file where it exist\n" \
                                     "***************** Make Sure You Choose Correct" \
                                     " Test File for Upload*******************\n" \
                                     "Provide location: \n"))
            user_file = Path("{}".format(filename_1.strip()))
            if user_file.is_file():
                break
            else:
                print("**************File Does Not Exist*****************\n")
                continue
        return filename_1

    def upload_config(self):
        """transfer config file as a chunk to controller"""
        if DUT_CHECK == 0:
            return print("DUT-Host is not Connected [!]" \
                         "\nMake sure to establish connection with DUT-Host.")
        default_location = self.config.get('ConfFile', 'path')
        if not default_location:
            filename = self.get_user_conf_location()
        else:
            user_preference = str(input("Use location specified in vsperfclient.conf?[Y/N] :"))
            while True:
                if 'y' in user_preference.lower().strip():
                    filename = self.config.get('ConfFile', 'path')
                    user_file = Path("{}".format(filename.strip()))
                    if user_file.is_file():
                        break
                    else:
                        print("**************File Does Not Exist*****************\n")
                        user_preference = 'n'
                        continue
                elif 'n' in user_preference.lower().strip():
                    filename = self.get_user_conf_location()
                    break
                else:
                    print("Invalid Input")
                    user_preference = str(input("Use location specified in vsperfclient.conf?" \
                                                "[Y/N] : "))
                    continue
        filename = filename.strip()
        upload_param = self.get_file_chunks(filename)
        upload_status = self.stub.UploadConfigFile(upload_param)
        print(upload_status.Message)

    def start_test(self):
        """start test parameter, test config file and test name"""
        test_control = vsperf_pb2.ControlVsperf(testtype=self.config.get('Testcase', 'test'), \
                                                conffile=self.config.get('Testcase', 'conffile'))
        control_reply = self.stub.StartTest(test_control)
        print(control_reply.message)

    def start_tgen(self):
        """start t-rex traffic generetor on tgen-host"""
        tgen_control = vsperf_pb2.ControlTGen(params=self.config.get('TGen', 'params'))
        control_reply = self.stub.StartTGen(tgen_control)
        print(control_reply.message)

    @classmethod
    def get_file_chunks(cls, filename):
        """convert file into chunk to stream between client and controller with filename"""
        with open(filename, 'rb') as f_1:
            while True:
                file_path = filename
                file_path_list = file_path.split("/")
                test_filename = file_path_list[(len(file_path_list)-1)]
                piece = f_1.read(CHUNK_SIZE)
                if not piece:
                    return None
                return vsperf_pb2.ConfFileTest(Content=piece, Filename=test_filename)
    @classmethod
    def get_file_chunks_1(cls, filename):
        """Convert file into chunks"""
        with open(filename, 'rb') as f:
            while True:
                piece = f.read(CHUNK_SIZE)
                if len(piece) == 0:
                    return
                yield vsperf_pb2.ConfFile(Content=piece)


    def test_status(self):
        """check the test_status"""
        test_check = vsperf_pb2.StatusQuery(
            testtype=self.config.get('Testcase', 'test'))
        check_result_reply = self.stub.TestStatus(test_check)
        print(check_result_reply.message)

    def vsperf_terminate(self):
        """after running test terminate vsperf on dut host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        termination_reply = self.stub.TerminateVsperf(hostinfo)
        print(termination_reply.message)

    def start_beats(self):
        """start beats on dut-host before running test"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.StartBeats(hostinfo)
        print(status_reply.message)

    def remove_vsperf(self):
        """remove vsperf from dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveVsperf(hostinfo)
        print(status_reply.message)

    def remove_result_folder(self):
        """remove resutl folder from dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveResultFolder(hostinfo)
        print(status_reply.message)

    def remove_config_files(self):
        """remove all config files"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveUploadedConfig(hostinfo)
        print(status_reply.message)

    def remove_collectd(self):
        """remove collectd from dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveCollectd(hostinfo)
        print(status_reply.message)

    def remove_everything(self):
        """remove everything from dut host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveEverything(hostinfo)
        print(status_reply.message)

    def sanity_nic_check(self):
        """nic is available on tgen host check"""
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        status_reply = self.stub.SanityNICCheck(tgeninfo)
        print(status_reply.message)

    def sanity_collectd_check(self):
        """check collecd properly running"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityCollectdCheck(hostinfo)
        print(status_reply.message)

    def cpu_allocation_check(self):
        """check cpu allocation"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityCPUAllocationCheck(hostinfo)
        print(status_reply.message)

    def sanity_vnf_path(self):
        """vnf path available on dut host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityVNFpath(hostinfo)
        print(status_reply.message)

    def sanity_vsperf_check(self):
        """check vsperf correctly installed"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityVSPERFCheck(hostinfo)
        print(status_reply.message)

    def sanity_dut_tgen_conn_check(self):
        """check the connection between dut-host and tgen-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityTgenConnDUTCheck(hostinfo)
        print(status_reply.message)

    def dut_test_availability(self):
        """dut-host is free for test check"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.DUTvsperfTestAvailability(hostinfo)
        print(status_reply.message)

    def get_test_conf_from_dut(self):
        """get the vsperf test config file from dut host for user to check"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.GetVSPERFConffromDUT(hostinfo)
        print(status_reply.message)

    def dut_hugepage_config(self):
        """setup hugepages on dut-host"""
        configparam = vsperf_pb2.HugepConf(hpmax=self.config.get('HugepageConfig', 'HpMax'), \
                                           hprequested=self.config.get('HugepageConfig',\
                                            'HpRequested'))
        config_status_reply = self.stub.DutHugepageConfig(configparam)
        print(config_status_reply.message)
    @classmethod
    def get_user_collectd_conf_location(cls):
        """get collectd configuration file location from user"""
        while True:
            filename_1 = str(input("Provide correct location for your collectd configuration " \
                                     "file where collectd.conf exist\n" \
                                     "***************** Make Sure You Choose Correct" \
                                     " File for Upload*******************\n" \
                                     "Provide location: \n"))
            user_file = Path("{}".format(filename_1.strip()))
            if user_file.is_file():
                break
            else:
                print("**************File Does Not Exist*****************\n")
                continue
        return filename_1
    def host_testcontrol_connect(self):
        """provice dut-host credential to test controller"""
        global DUT_CHECK
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        self.stub.HostConnect(hostinfo)

    def tgen_testcontrol_connect(self):
        """provide tgen-host credential to test controller"""
        global TGEN_CHECK
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        self.stub.TGenHostConnect(tgeninfo)

    def upload_collectd_config(self):
        """collectd config file chunks forwarded to controller"""
        if DUT_CHECK == 0:
            return print("DUT-Host is not Connected [!]" \
                         "\nMake sure to establish connection with DUT-Host.")
        default_location = self.config.get('ConfFile', 'collectdpath')
        if not default_location:
            filename = self.get_user_collectd_conf_location()
        else:
            user_preference = str(input("Use location specified in vsperfclient.conf?[Y/N] :"))
            while True:
                if 'y' in user_preference.lower().strip():
                    filename = self.config.get('ConfFile', 'collectdpath')
                    user_file = Path("{}".format(filename.strip()))
                    if user_file.is_file():
                        break
                    else:
                        print("**************File Does Not Exist*****************\n")
                        user_preference = 'n'
                        continue
                elif 'n' in user_preference.lower().strip():
                    filename = self.get_user_collectd_conf_location()
                    break
                else:
                    print("Invalid Input")
                    user_preference = str(input("Use location specified in vsperfclient.conf?" \
                                                "[Y/N] : "))
                    continue
        filename = filename.strip()
        chunks = self.get_file_chunks_1(filename)
        upload_status = self.stub.CollectdUploadConfig(chunks)
        print(upload_status.Message)

    def dut_check_dependecies(self):
        """check_dependecies on dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        check_reply = self.stub.CheckDependecies(hostinfo)
        print(check_reply.message)
    
    @classmethod
    def establish_connection_both(cls):
        """
        This Function use to establish connection for vsperf to both the deploy server \
        and testcontrol server
        """
        client = VsperfClient()
        ip_add, port = client.get_deploy_channel_info()
        print("Establish connection for vsperf")
        menuitems_connection = [
            {"Connect to DUT Host": client.host_connect_both},
            {"Connect to TGen Host": client.tgen_connect_both},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_connection, client, ip_add, port)
    @classmethod
    def establish_connection_deploy(cls):
        """
        This Function use to establish connection for vsperf to either using the dploy 
        or using the testcontrol server
        """
        client = VsperfClient()
        ip_add, port = client.get_deploy_channel_info()
        print("Establish connection for vsperf")
        menuitems_connection = [
            {"Connect to DUT Host": client.host_connect},
            {"Connect to TGen Host": client.tgen_connect},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_connection, client, ip_add, port)
    @classmethod
    def establish_connection_test(cls):
        """
        This Function use to establish connection for vsperf to either using the dploy 
        or using the testcontrol server
        """
        client = VsperfClient()
        ip_add, port = client.get_test_channel_info()
        print("Establish connection for vsperf")
        menuitems_connection = [
            {"Connect to DUT Host": client.host_connect},
            {"Connect to TGen Host": client.tgen_connect},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_connection, client, ip_add, port)
    @classmethod
    def vsperf_setup(cls):
        """setup sub-options"""
        client = VsperfClient()
        ip_add, port = client.get_deploy_channel_info()
        print("Prerequisites Installation for VSPERF")
        menuitems_setup = [
            {"Install VSPERF": client.vsperf_install},
            {"Install TGen ": client.tgen_install},
            {"Install Collectd": client.collectd_install},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client, ip_add, port)
    @classmethod
    def upload_config_files(cls):
        """all the upload sub-options"""
        client = VsperfClient()
        ip_add, port = client.get_deploy_channel_info()
        menuitems_setup = [
            {"Upload TGen Configuration File": client.upload_tgen_config},
            {"Upload Collectd Configuration File": client.upload_collectd_config},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client, ip_add, port)
    @classmethod
    def manage_sysparam_config(cls):
        """manage system parameter on dut host before run test"""
        client = VsperfClient()
        ip_add, port = client.get_deploy_channel_info()
        menuitems_setup = [
            {"DUT-Host hugepages configuration": client.dut_hugepage_config},
            {"Check VSPERF Dependencies on DUT-Host": client.dut_check_dependecies},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client, ip_add, port)

    @classmethod
    def test_status_check(cls):
        """after running test , test status related sub-options"""
        client = VsperfClient()
        ip_add, port = client.get_test_channel_info()
        menuitems_setup = [
            {"Test status": client.test_status},
            {"Get Test Configuration file from DUT-host": client.get_test_conf_from_dut},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client, ip_add, port)

    @classmethod
    def sanity_check_options(cls):
        """all sanity check sub-options"""
        client = VsperfClient()
        ip_add, port = client.get_test_channel_info()
        menuitems_setup = [
            {"Check installed VSPERF": client.sanity_vsperf_check},
            {"Check Test Config's VNF path is available on DUT-Host": client.sanity_vnf_path},
            {"Check NIC PCIs is available on Traffic Generator": client.sanity_nic_check},
            {"Check CPU allocation on DUT-Host": client.cpu_allocation_check},
            {"Check installed Collectd": client.sanity_collectd_check},
            {"Check Connection between DUT-Host and Traffic Generator Host":
             client.sanity_dut_tgen_conn_check},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client, ip_add, port)

    @classmethod
    def run_test(cls):
        """run test sub-options"""
        print("**Before user Run Tests we highly recommend user to perform Sanity Checks.......")
        client = VsperfClient()
        ip_add, port = client.get_test_channel_info()
        menuitems_setup = [
            {"Upload Test Configuration File": client.upload_config},
            {"Perform Sanity Checks before running tests": client.sanity_check_options},
            {"Check if DUT-HOST is available": client.dut_test_availability},
            {"Start TGen ": client.start_tgen},
            {"Start Beats": client.start_beats},
            {"Start Test": client.start_test},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client, ip_add, port)

    @classmethod
    def clean_up(cls):
        """clean-up sub-options"""
        print(
            "*******************************************************************\n\n\
             IF you are performing Test on IntelPOD 12 - Node 4, Be careful during removal\n\n\
             *******************************************************************")
        client = VsperfClient()
        ip_add, port = client.get_test_channel_info()
        menuitems_setup = [
            {"Remove VSPERF": client.remove_vsperf},
            {"Terminate VSPERF": client.vsperf_terminate},
            {"Remove Results from DUT-Host": client.remove_result_folder},
            {"Remove Uploaded Configuration File": client.remove_config_files},
            {"Remove Collectd": client.remove_collectd},
            {"Remove Everything": client.remove_everything},
            {"Return to Previous Menu": client.exit_section}

        ]
        client.section_execute(menuitems_setup, client, ip_add, port)

def run():
    """It will run the actul primary options"""
    client = VsperfClient()
    client_mode = client.get_mode()
    print(client_mode)
    if "deploy" in client_mode.lower().strip():
        menuitems = [
        {"Establish Connections": client.establish_connection_deploy},
        {"Installation": client.vsperf_setup},
        {"Upload Configuration Files": client.upload_config_files},
        {"Manage DUT-System Configuration": client.manage_sysparam_config},
        {"Exit": sys.exit}
        ]
        #ip_add, port = client.get_channel_info()
        #channel = grpc.insecure_channel(ip_add + ':' + port)
        while True:
        # os.system('clear')
            print(colorize(HEADER, 'blue'))
            print(colorize('version 0.1\n', 'pink'))
            for item in menuitems:
                print(colorize("[" +
                               str(menuitems.index(item)) + "]", 'green') +
                      list(item.keys())[0])
            choice = input(">> ")
            try:
                if int(choice) < 0:
                    raise ValueError
                list(menuitems[int(choice)].values())[0]()
            except (ValueError, IndexError):
                pass

    elif "test" in  client_mode.lower().strip():
        menuitems = [
        {"Establish Connections": client.establish_connection_test},
        {"Run Test": client.run_test},
        {"Test Status": client.test_status_check},
        {"Clean-Up": client.clean_up},
        {"Exit": sys.exit}
	    ]
        #ip_add, port = client.get_channel_info()
        #channel = grpc.insecure_channel(ip_add + ':' + port)
        while True:
            # os.system('clear')
            print(colorize(HEADER, 'blue'))
            print(colorize('version 0.1\n', 'pink'))
            for item in menuitems:
                print(colorize("[" +
                               str(menuitems.index(item)) + "]", 'green') +
                      list(item.keys())[0])
            choice = input(">> ")
            try:
                if int(choice) < 0:
                    raise ValueError
                list(menuitems[int(choice)].values())[0]()
            except (ValueError, IndexError):
                pass

    elif "together" in client_mode.lower().strip():
        menuitems = [
        {"Establish Connections": client.establish_connection_both},
        {"Installation": client.vsperf_setup},
        {"Upload Configuration Files": client.upload_config_files},
        {"Manage DUT-System Configuration": client.manage_sysparam_config},
        {"Run Test": client.run_test},
        {"Test Status": client.test_status_check},
        {"Clean-Up": client.clean_up},
        {"Exit": sys.exit}
	    ]
        #ip_add, port = client.get_channel_info()
        #channel = grpc.insecure_channel(ip_add + ':' + port)
        while True:
            # os.system('clear')
            print(colorize(HEADER, 'blue'))
            print(colorize('version 0.1\n', 'pink'))
            for item in menuitems:
                print(colorize("[" +
                               str(menuitems.index(item)) + "]", 'green') +
                      list(item.keys())[0])
            choice = input(">> ")
            try:
                if int(choice) < 0:
                    raise ValueError
                list(menuitems[int(choice)].values())[0]()
            except (ValueError, IndexError):
                pass

    else:
        print("You have not defined client mode in vsperfclient.conf [!]")


if __name__ == '__main__':
    run()
