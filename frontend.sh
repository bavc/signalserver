docker build -t signalserver-frontend  -f Dockerfile-frontend   .
docker run -v `pwd`/frontend:/var/build signalserver-frontend
