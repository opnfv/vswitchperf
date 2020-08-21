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

FROM python:alpine
RUN apk --update upgrade && \
    apk add gcc libffi-dev musl-dev python3-dev openssl-dev tzdata libmagic && \
    rm -rf /var/cache/apk/*
RUN pip install elastalert &&\
	apk del gcc libffi-dev musl-dev python3-dev openssl-dev
RUN mkdir -p /opt/elastalert && \
	mkdir -p /opt/elastalert/rules &&\
WORKDIR /opt/elastalert