$fuel_settings = parseyaml(file('/etc/astute.yaml'))
$master_ip = $::fuel_settings['master_ip']

exec { "install vsperf":
    command => "mkdir -p /opt/vswitchperf; curl http://$master_ip:8080/plugins/fuel-plugin-vsperf-1.0/repositories/ubuntu/vswitchperf.tgz | tar xzv -C /opt/vswitchperf",
    path   => "/usr/bin:/usr/sbin:/bin:/sbin";
}
