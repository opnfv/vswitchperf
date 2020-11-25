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

# Install required packages
RUN apk add --no-cache --update python3 python3-dev \
    py3-wheel py3-pip git openssh-client python3-tkinter \
    tk gcc musl-dev libffi-dev openssl-dev make

# Clone VSPERF.
RUN git clone https://gerrit.opnfv.org/gerrit/vswitchperf /vswitchperf

#
# Remove unnecessary python packages.
#
RUN cd /vswitchperf && \
  sed -e '/numpy/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/matplotlib/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/pycrypto/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/pypsi/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/paramiko/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/pyzmq/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/kubernetes/ s/^#*/#\ /' -i requirements.txt

#
# Build VSPERF
#
RUN cd /vswitchperf && \
    pip3 install --ignore-installed distlib -r requirements.txt && \
    cd /vswitchperf/src/trex && make

# Include vsperf into Path.
ENV PATH "$PATH:/vswitchperf"

COPY vsperfostack.conf /vsperfostack.conf

# Required step for Xtesting
ADD . /src/
RUN git init /src && pip3 install /src

# Copy Testcase
COPY testcases.yaml /usr/lib/python3.8/site-packages/xtesting/ci/testcases.yaml

# Set working directory - This helps to resolve path to templates.
WORKDIR /vswitchperf

# Command Run
CMD ["run_tests", "-t", "all"]
