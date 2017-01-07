docker build -t signalserver-frontend  -f /Users/your/projectpath/signalserver/Dockerfile-frontend   .
                                          /home/ubuntu/signalserver
docker run -v `pwd`/frontend:/var/build signalserver-frontend
