docker build . -t vs-ui

cd client
docker container run --rm -it -v $(pwd)/:/usr/share/nginx/html -p 80:80 vs-ui
