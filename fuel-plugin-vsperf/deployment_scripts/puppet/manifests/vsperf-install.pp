$fuel_settings = parseyaml(file('/etc/astute.yaml'))
$master_ip = $::fuel_settings['master_ip']

exec { "wget vsperf":
          command => "wget http://$master_ip:8080/plugins/fuel-plugin-vsperf-1.0/repositories/ubuntu/vswitchperf.tgz -O /opt/vswitchperf.tgz",
                        path   => "/usr/bin:/usr/sbin:/bin:/sbin",
}
exec { "untar vsperf":
          command => "tar xf /opt/vswitchperf.tgz -C /opt",
                        path   => "/usr/bin:/usr/sbin:/bin:/sbin",
}
