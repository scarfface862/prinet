#!/bin/bash
docker update `docker ps -q` --restart no
docker kill `docker ps -q`
