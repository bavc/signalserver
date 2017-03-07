#!/bin/bash
#docker-machine create --driver virtualbox default
#docker-machine start default
#docker-machine env default
#eval "$(docker-machine env default)"
docker-compose  -f docker-compose.yml -f docker-compose.dev.yml build
docker-compose up -d db
migration=1
while [[ $migration != 0 ]]; do
    sleep 2
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml run web python manage.py migrate
    migration=$?
done
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
echo ">> Application is running <<"
echo "http://${DOCKER_HOST:-localhost}" | sed 's/tcp:\/\///g' | sed -E 's/(\:[0-9]+)?$/:8000/'
