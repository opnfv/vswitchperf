# To Build
# docker build --rm -t vsperf .

# -------- Builder stage.
FROM python:3.6.10-slim-buster
MAINTAINER Sridhar Rao <sridhar.rao@spirent.com>

# Create a directory
RUN mkdir /home/opnfv
#
# Update and Install required packages
#
RUN apt-get -y update
RUN apt-get -y install git iputils-ping openssh-client tk

#
# Get vswitchperf
#
RUN cd /home/opnfv && \
  git clone https://gerrit.opnfv.org/gerrit/vswitchperf

#
# Remove unnecessary python packages.
#
RUN cd /home/opnfv/vswitchperf && \
  sed -e '/numpy/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/matplotlib/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/pycrypto/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/pypsi/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/paramiko/ s/^#*/#\ /' -i requirements.txt && \
  sed -e '/pyzmq/ s/^#*/#\ /' -i requirements.txt && \
  sed -e "\$apyzmq" -i requirements.txt 

#
# Build VSPERF
#
RUN cd /home/opnfv/vswitchperf/systems && ./build_base_machine.sh --trafficgen
