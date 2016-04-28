#!/bin/bash
docker-machine create --driver virtualbox default
docker-machine start default
docker-machine env default
eval "$(docker-machine env default)"
docker-compose build
docker-compose up -d db
migration=1
while [[ $migration != 0 ]]; do
    sleep 2
    docker-compose run web python manage.py migrate
    migration=$?
done
docker-compose up -d
echo ">> Application is running <<"
echo "http://${DOCKER_HOST:-localhost}" | sed 's/tcp:\/\///g' | sed -E 's/(\:[0-9]+)?$/:8000/'