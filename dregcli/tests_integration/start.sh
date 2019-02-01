#!/usr/bin/env bash
function setImage() {
    docker pull alpine:$1
    docker tag alpine:$1 localhost:${port}/my-alpine:$1
    docker push localhost:${port}/my-alpine:$1
}

containerName=dregcli_ci_registry
port=5001

# IMPORTANT: REGISTRY_STORAGE_DELETE_ENABLED=true mandatory for delete rights
docker run -d -p ${port}:5000 -e REGISTRY_STORAGE_DELETE_ENABLED=true --restart=always --name ${containerName} registry:2

setImage 3.7
setImage 3.8
setImage latest

${DREGCLI_VENV}/bin/py.test --pep8 -v dregcli/tests_integration/

docker stop ${containerName}
docker rm ${containerName}
