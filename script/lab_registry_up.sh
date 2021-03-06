#!/usr/bin/env bash
function upRegistry() {
    # IMPORTANT: REGISTRY_STORAGE_DELETE_ENABLED=true mandatory for delete rights
    docker run -d -p ${port}:5000 -e REGISTRY_STORAGE_DELETE_ENABLED=true --name ${containerName} registry:2
}

# setImage source targetTag
function setImage() {
    docker pull alpine:$1
    docker tag alpine:$1 localhost:${port}/test-project:$2
    docker push localhost:${port}/test-project:$2
}


#
# SCRIPT
#
containerName=dregcli_lab_registry
port=5001

upRegistry

# layer with only commit tags
setImage 3.2 master-2ze98e000wx39d60a7390925d0czr3qs03j90aaa-1382

# a layer with a release tag between 2 layers with only commit tags
setImage 3.3 master-2yu50j111dy72e70b9623522e0zdt9wz29h71ddd-1383
setImage 3.3 alpha

# layer with only commit tags
setImage 3.4 master-2bd32d000ez93c50h8486935f0fda5ee09z98bbb-1384

# layers with release tags
# old-prod layer
setImage 3.5 master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385
setImage 3.5 old-prod

# prod layer
setImage 3.6 master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386
setImage 3.6 prod

# old-staging layer
setImage 3.7 master-1c48755c0b257ccd106badcb973a36528f833fc0-1387
setImage 3.7 old-staging

# staging layer
setImage 3.8 master-128a1e13dbe96705917020261ee23d097606bda2-1388
setImage 3.8 staging

# latest layer
setImage 3.9 latest
