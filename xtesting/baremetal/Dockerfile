FROM opnfv/xtesting
LABEL maintainer="sridhar.rao@spirent.com"

RUN apk upgrade --update
RUN apk add --no-cache --virtual .build-deps gcc musl-dev
RUN apk add python3-dev
RUN apk add linux-headers
RUN apk add libffi-dev
RUN apk add make
RUN apk add openssl-dev
RUN pip3 install --upgrade pip
RUN pip3 install chainmap
RUN pip3 install oslo.utils
RUN pip3 install paramiko
RUN pip3 install scp

ENV DUT_IP_ADDRESS=10.10.120.24
ENV DUT_USERNAME=opnfv
ENV DUT_PASSWORD=opnfv
ENV VSPERF_TESTS=phy2phy_tput
ENV VSPERF_CONFFILE=vsperf.conf
ENV RES_PATH=/tmp
ENV VSPERF_TRAFFICGEN_MODE=NO

COPY vsperf.conf vsperf.conf
COPY vsperf_controller.py vsperf_controller.py
COPY utils.py utils.py
COPY ssh.py ssh.py
COPY exceptions.py exceptions.py

COPY testcases.yaml /usr/lib/python3.8/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
