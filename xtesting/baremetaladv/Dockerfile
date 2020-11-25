FROM opnfv/xtesting

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
ENV VSPERF_CONFFILE=vsperf.conf
ENV RES_PATH=/tmp
ENV VSPERF_TRAFFICGEN_MODE=NO

COPY testcases.yaml /usr/lib/python3.8/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
