#!/bin/sh

# https://github.com/tmknom/dockerfiles/blob/main/prettier/README.md
docker run --rm -u `id -u`:`id -g` -v "$(pwd):/work" tmknom/prettier --write index.html static/
black *.py
