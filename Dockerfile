FROM django:onbuild
RUN mkdir -p /var/signalserver/files
RUN mkdir -p /var/signalserver/files/policies
RUN useradd -ms /bin/bash signalserversadmin
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash && apt-get install -y nodejs
RUN npm install -g bower
RUN cd frontend && bower install --allow-root
