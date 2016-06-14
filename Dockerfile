FROM django:onbuild
MAINTAINER Yayoi Ukai <yayoi.ukai@gmail.com>
RUN mkdir -p /var/signalserver/files
RUN useradd -ms /bin/bash signalserversadmin