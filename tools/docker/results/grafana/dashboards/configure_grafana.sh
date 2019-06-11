# Copyright 2017 OPNFV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/datasources -d \
      '{"name":"collectd","type":"influxdb","url":"http://localhost:8086","access":"proxy","isDefault":true,"database":"collectd","user":"admin","password":"admin","basicAuth":false}'
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/dashboards/db -d @cpu_usage_dashboard.json
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/dashboards/db -d @average_load_dashboard.json
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/dashboards/db -d @host_overview_dashboard.json
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/dashboards/db -d @intel_pmu_dashboard.json
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/dashboards/db -d @intel_rdt_dashboard.json
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/dashboards/db -d @ipmi_dashboard.json
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/dashboards/db -d @mcelog_dashboard.json
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/dashboards/db -d @ovs_stats_dashboard.json
curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/dashboards/db -d @virt_dashboard.json
