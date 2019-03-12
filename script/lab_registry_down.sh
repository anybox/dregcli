#!/usr/bin/env bash
containerName=dregcli_lab_registry

docker stop ${containerName}
docker rm ${containerName}
