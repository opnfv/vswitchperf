# Copyright (c) 2016-2017 Intel corporation.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

$fuel_settings = parseyaml(file('/etc/astute.yaml'))
$master_ip = $::fuel_settings['master_ip']

exec { "install vsperf":
    command => "mkdir -p /opt/vswitchperf; curl http://$master_ip:8080/plugins/fuel-plugin-vsperf-1.0/repositories/ubuntu/vswitchperf.tgz | tar xzv -C /opt/vswitchperf",
    path   => "/usr/bin:/usr/sbin:/bin:/sbin";
}
