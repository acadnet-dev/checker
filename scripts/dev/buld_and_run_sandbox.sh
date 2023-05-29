#!/bin/bash

docker build sandbox --tag sandbox
docker run -it -p 2999:2999 --rm --name sandbox sandbox