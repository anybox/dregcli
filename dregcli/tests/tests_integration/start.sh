#!/usr/bin/env bash
function upRegistry() {
    # IMPORTANT: REGISTRY_STORAGE_DELETE_ENABLED=true mandatory for delete rights
    docker run -d -p ${port}:5000 -e REGISTRY_STORAGE_DELETE_ENABLED=true --restart=always --name ${containerName} registry:2
}

function downRegistry() {
        docker stop ${containerName}
    docker rm ${containerName}
}

# setImage source targetTag
function setImage() {
    docker pull alpine:$1
    docker tag alpine:$1 localhost:${port}/test-project:$2
    docker push localhost:${port}/test-project:$2
}

function setGarbageImages() {
    setImage 3.5 master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385
    setImage 3.5 old-prod
    setImage 3.6 master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386
    setImage 3.6 prod
    setImage 3.7 master-1c48755c0b257ccd106badcb973a36528f833fc0-1387
    setImage 3.7 old-staging
    setImage 3.8 master-128a1e13dbe96705917020261ee23d097606bda2-1388
    setImage 3.8 staging
    setImage 3.9 latest
}

# garbageTest 'name' python_script_name.py
function  garbageTest() {
    echo "GARBAGE $1"

    upRegistry
    setGarbageImages
    ${DREGCLI_VENV}/bin/py.test --pep8 -v dregcli/tests/tests_integration/tests_garbage/$2
    downRegistry
}

#
# SCRIPT
#
containerName=dregcli_ci_registry
port=5001

#
# MAIN
#
echo 'MAIN'

upRegistry
setImage 3.5 master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385
setImage 3.6 master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386
setImage 3.7 master-1c48755c0b257ccd106badcb973a36528f833fc0-1387
setImage 3.8 master-128a1e13dbe96705917020261ee23d097606bda2-1388
${DREGCLI_VENV}/bin/py.test --pep8 -v dregcli/tests/tests_integration/ --ignore dregcli/tests/tests_integration/tests_garbage/
downRegistry

#
# GARBAGE ALL
#
garbageTest 'ALL' test_garbage_all.py

#
# GARBAGE INCLUDE
#
garbageTest 'INCLUDE' test_garbage_include.py

#
# GARBAGE EXCLUDE
#
garbageTest 'EXCLUDE' test_garbage_exclude.py

#
# GARBAGE FROM COUNT
#
garbageTest 'FROM COUNT' test_garbage_from_count.py
