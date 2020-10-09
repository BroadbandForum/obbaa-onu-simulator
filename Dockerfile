# Dockerfile for obbaa-onu-simulator
# Copyright 2020 Broadband Forum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG FROM=broadbandforum/sphinx:latest

FROM $FROM

# install OS packages and create directories
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get --yes install \
        make \
        net-tools \
        iputils-ping \
        python3 \
        python3-pip \
        tshark \
        vim \
 && apt-get clean \
 && mkdir -p \
          /opt \
          /opt/obbaa-onu-simulator

# copy source code
COPY . /opt/obbaa-onu-simulator

# build documentation and install simulator
RUN PYTHONPATH=/opt/obbaa-onu-simulator \
        make -C /opt/obbaa-onu-simulator distclean html dist \
 && pip3 install --upgrade /opt/obbaa-onu-simulator \
 && (cd /usr/local/bin; ln -s /opt/obbaa-onu-simulator/bin/omci_dump_decoder)
