FROM django:onbuild
MAINTAINER Yayoi Ukai <yayoi.ukai@gmail.com>
RUN mkdir -p /var/signalserver/files
RUN useradd -ms /bin/bash signalserversadmin
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash && apt-get install -y nodejs
RUN npm install -g bower
COPY ./frontend/bower.json bower.json
RUN bower install --allow-root