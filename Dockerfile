FROM ubuntu:14.04
MAINTAINER Chris Timperley "christimperley@gmail.com"

# Create docker user
RUN apt-get update && \
    apt-get install --no-install-recommends -y sudo && \
    useradd -ms /bin/bash docker && \
    echo 'docker ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    adduser docker sudo && \
    apt-get clean && \
    mkdir -p /home/docker && \
    sudo chown -R docker /home/docker && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
USER docker

# reclaim ownership or /usr/local/bin
RUN sudo chown -R docker /usr/local/bin

# install basic packages
RUN sudo apt-get update && \
    sudo apt-get install --no-install-recommends -y build-essential \
                                                    curl \
                                                    libcap-dev \
                                                    git \
                                                    cmake \
                                                    vim \
                                                    jq \
                                                    wget \
                                                    zip \
                                                    unzip \
                                                    python3-setuptools \
                                                    software-properties-common \
                                                    libncurses5-dev && \
    sudo apt-get autoremove -y && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*  

WORKDIR /experiment


RUN sudo apt-get update && \
    sudo apt-get install -y libtool \
                            automake \
                            pkg-config \
                            autoconf \
                            gcc \
                            g++ \
                            libexpat1-dev \
                            python-matplotlib \
                            python-serial \
                            python-wxgtk2.8 \
                            python-wxtools \
                            python-lxml \
                            python-scipy \
                            python-opencv \
                            ccache \
                            gawk \
                            python-pip \
                            flightgear \
                            python-pexpect && \
    sudo pip install future pymavlink MAVProxy && \
    sudo pip install --upgrade pexpect && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN git clone git://github.com/tridge/jsbsim && \
    cd jsbsim && \
    ./autogen.sh --enable-libraries && \
    make -j

RUN sudo apt-get update && \
    sudo apt-get install -y flightgear && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PATH "${PATH}:/experiment/jsbsim/src"
ENV PATH "${PATH}:/experiment/source/Tools/autotest"
ENV PATH "${PATH}:/usr/lib/ccache:${PATH}"
ENV PATH "/usr/games:${PATH}"

ENV ARDUPILOT_REVISION 7173025
RUN git clone https://github.com/ArduPilot/ardupilot source && \
    cd source && \
    git checkout "${ARDUPILOT_REVISION}" && \
    git submodule update --init --recursive && \
    sudo chown -R $(whoami):$(whoami) /experiment

RUN sudo pip install  future \
                      MAVProxy \
                      dronekit \
                      statistics \
                      geopy \
                      flask


ENV ARDUPILOT_LOCATION "/experiment/source"

ADD default.parm /experiment/
ADD default_eeprom.bin /experiment/
RUN cp /experiment/default_eeprom.bin /experiment/eeprom.bin

RUN git clone https://github.com/dronekit/dronekit-sitl.git /experiment/dronekit-sitl && \
    cd /experiment/dronekit-sitl && \
    git checkout 2d854af && \
    sudo python setup.py install


RUN cd "${ARDUPILOT_LOCATION}" && \
    ./waf configure && \
    ./waf build -j$(nproc)

# ADD copter.parm /experiment/
ADD tester.py /experiment/source/Tools/autotest/tester.py
RUN sudo chown -R $USER:$USER source