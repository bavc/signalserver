#docker build -t my-nodejs-app  -f /Users/yayoi/jan2016/signalserver/Dockerfile-alternate   .
docker build -t signalserver-frontend  -f /Users/yayoi/jan2016/signalserver/Dockerfile-frontend   .
docker run -v `pwd`/frontend:/var/build signalserver-frontend
#docker run -v /foo --name="vtest" my-nodejs-app sh -c 'echo hello docker volume > /foo/testing.txt'

