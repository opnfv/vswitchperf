# Copyright 2020 Spirent Communications.
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

FROM opnfv/xtesting
LABEL maintainer="sridhar.rao@spirent.com"

ADD . /src/
RUN apk add --no-cache --update --virtual .build-deps python3 \
    py3-pip py3-wheel git python3-dev linux-headers libffi-dev \
    make openssl-dev gcc musl-dev && \
    pip3 install --upgrade pip chainmap oslo.utils \
    paramiko scp && \
    git init /src && pip3 install /src

ENV DUT_IP_ADDRESS=10.10.120.24
ENV DUT_USERNAME=opnfv
ENV DUT_PASSWORD=opnfv
ENV VSPERF_TESTS=phy2phy_tput
ENV VSPERF_CONFFILE=/vsperf.conf
ENV RES_PATH=/tmp
ENV VSPERF_TRAFFICGEN_MODE=NO

COPY vsperf.conf /vsperf.conf
COPY testcases.yaml /usr/lib/python3.8/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
