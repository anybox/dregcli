#!/usr/bin/env bash
containerName=dregcli_ci_registry
port=5001

# IMPORTANT: REGISTRY_STORAGE_DELETE_ENABLED=true mandatory for delete rights
docker run -d -p ${port}:5000 -e REGISTRY_STORAGE_DELETE_ENABLED=true --restart=always --name ${containerName} registry:2

docker pull alpine:3.8
docker tag alpine:3.8 localhost:${port}/my-alpine:3.8
docker push localhost:${port}/my-alpine:3.8
docker pull alpine:latest
docker tag alpine:latest localhost:${port}/my-alpine:latest
docker push localhost:${port}/my-alpine:latest

${DREGCLI_VENV}/bin/py.test --pep8 -v dregcli/tests_integration/

docker stop ${containerName}
docker rm ${containerName}
