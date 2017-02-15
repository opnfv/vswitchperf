#!/bin/bash

# Copyright (c) 2016-2017 Intel corporation.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

sudo apt-get update -y
sudo apt-get install -y ruby-dev rubygems-integration python-pip rpm createrepo dpkg-dev
sudo gem install fpm
sudo pip install fuel-plugin-builder
fpb --debug --build /vswitchperf/fuel-plugin-vsperf
