# Copyright 2020 Adarsh yadav, Aditya Srivastava
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

FROM fluent/fluentd:v1.11.0-debian-1.0
USER root
RUN gem sources --add https://rubygems.org/
RUN  apt-get update \
 &&  gem install fluent-plugin-elasticsearch \
 &&  gem install elasticsearch-xpack\
 &&  gem install fluent-plugin-rewrite-tag-filter\
 &&  gem install fluent-plugin-dio
USER fluent