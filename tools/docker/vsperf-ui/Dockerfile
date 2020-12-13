FROM nginx:1.19.5-alpine
MAINTAINER Parth Yadav <parthyadav3105@gmail.com>

WORKDIR /usr/share/nginx/html
COPY ./client ./
WORKDIR /usr/share/nginx/html/scripts/lib/yahu/
RUN sh build.sh
WORKDIR /usr/share/nginx/html
RUN rm -r scripts/lib/yahu/
## Minify all code(CSS HTM HTML JS JSON SVG XML )  with https://github.com/tdewolff/minify/tree/master/cmd/minify

