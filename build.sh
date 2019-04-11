#!/bin/bash

docker build -t ukauth .
docker run -p 8085:8085 -it ukauth
