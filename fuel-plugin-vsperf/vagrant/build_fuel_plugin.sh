#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y ruby-dev rubygems-integration python-pip rpm createrepo dpkg-dev
sudo gem install fpm
sudo pip install fuel-plugin-builder
fpb --debug --build /vswitchperf/fuel-plugin-vsperf
