#!/bin/bash
docker-compose up -d worker

echo 'Waiting for 10 seconds to let rabbitmq and worker to set up'
sleep 10s

docker-compose run -d task

echo 'Attaching to worker logs'
docker-compose logs -f worker