FROM houston-icse-2018:base

ADD . bugFiles
RUN sudo chown -R $USER:$USER bugFiles && \
    cp -rp bugFiles/* source/ && \
    sudo rm -rf bugFiles 
RUN cd source && \
    ./waf configure && \
    ./waf build -j$(nproc)
