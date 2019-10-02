FROM python:3.6
LABEL maintainer="sridhar.rao@spirent.com"

ENV GRPC_PYTHON_VERSION 1.4.0
RUN apt-get update && apt-get -y install python3-pip
RUN pip3 install grpcio==${GRPC_PYTHON_VERSION} grpcio-tools==${GRPC_PYTHON_VERSION}
RUN pip3 install paramiko
RUN pip3 install chainmap
RUN pip3 install oslo.utils
RUN pip3 install scp

WORKDIR /usr/src/app

COPY ./vsperf ./vsperf

VOLUME ["/usr/src/app/vsperf"]

EXPOSE 50052

CMD ["python3", "./vsperf/vsperf_controller.py"]

#CMD tail -f /dev/null
