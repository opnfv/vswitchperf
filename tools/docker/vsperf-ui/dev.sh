docker build . -t vs-ui

cd client
docker container run --rm -d --name vsperf-ui-dev -v $(pwd)/:/usr/share/nginx/html -p 80:80 vs-ui
cd scripts/lib/yahu
watch -n5 sh build.sh
