# ./bin/shared.sh - run from root
docker build -t sustaintrain-shared -f docker/SharedDocker .
docker stop sustaintrain-shared
docker rm sustaintrain-shared
docker run -d --name sustaintrain-shared sustaintrain-shared tail -f /dev/null
docker exec sustaintrain-shared bash -c 'cd /var/task/shared-libs && zip -r ../shared.zip .'
docker cp sustaintrain-shared:/var/task/shared.zip ./dist