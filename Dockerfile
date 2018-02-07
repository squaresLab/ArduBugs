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
    sudo chown -R docker /usr/local/bin && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
USER docker

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
                            python-pexpect \
			                      bash && \
    sudo pip install future MAVProxy && \
    sudo pip install --upgrade pexpect && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# download and install jsbsim
WORKDIR /experiment
ENV JSBSIM_REVISION 9cc2bf1
RUN sudo chown -R $(whoami):$(whoami) /experiment && \
    git clone https://github.com/arktools/jsbsim /experiment/jsbsim && \
    cd jsbsim && \
    git checkout "${JSBSIM_REVISION}" && \
    ./autogen.sh --enable-libraries && \
    make -j

ENV PATH "${PATH}:/experiment/jsbsim/src"
ENV PATH "${PATH}:/experiment/source/Tools/autotest"
ENV PATH "${PATH}:/usr/lib/ccache:${PATH}"
ENV PATH "/usr/games:${PATH}"

# download ArduPilot source code
ENV ARDUPILOT_REVISION 7173025
RUN git clone https://github.com/ArduPilot/ardupilot source && \
    cd source && \
    git checkout "${ARDUPILOT_REVISION}" && \
    git submodule update --init --recursive && \
    sudo chown -R $(whoami):$(whoami) /experiment

RUN sudo pip install  future \
                      dronekit \
                      statistics \
                      geopy \
                      flask
                      #MAVProxy \

ENV ARDUPILOT_LOCATION "/experiment/source"

ADD default.parm /experiment/
ADD default_eeprom.bin /experiment/
RUN cp /experiment/default_eeprom.bin /experiment/eeprom.bin

# install dronekit SITL
RUN git clone https://github.com/dronekit/dronekit-sitl.git /experiment/dronekit-sitl && \
    cd /experiment/dronekit-sitl && \
    git checkout 2d854af && \
    sudo python setup.py install

# compile ArduPilot
# RUN cd "${ARDUPILOT_LOCATION}" && \
#     ./waf configure && \
#     ./waf build -j$(nproc)

ADD tester.py /experiment/source/Tools/autotest/tester.py
RUN sudo chown -R $(whoami):$(whoami) source

# fixes indefinite timeout in default test harness
RUN sudo pip uninstall -y pymavlink && \
    sudo pip install pymavlink

# install Python 3
RUN sudo apt-get update && \
    sudo apt-get install -y python3
# RUN sudo add-apt-repository ppa:jonathonf/python-3.6 && \
#     sudo apt-get update && \
#     sudo apt-get install -y python-3.6
