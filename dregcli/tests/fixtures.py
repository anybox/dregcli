import datetime
import pytest

from dregcli.dregcli import DRegCliException, Client, Repository


@pytest.fixture()
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture()
def fixture_repositories_url():
    return '/v2/_catalog'


@pytest.fixture()
def fixture_repository():
    return "test-project"


@pytest.fixture()
def fixture_repositories(fixture_repository):
    return {"repositories": [fixture_repository]}


@pytest.fixture()
def fixture_tags():
    return [
        'master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385',
        'master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386',
        'master-1c48755c0b257ccd106badcb973a36528f833fc0-1387',
        'master-128a1e13dbe96705917020261ee23d097606bda2-1388',
    ]


@pytest.fixture()
def fixture_auth():
    return {
        'login': 'foobar',
        'password': 'foobar2000',
        'token': '',
        'remote_type': Client.Meta.remote_type_registry,
    }


@pytest.fixture()
def fixture_auth_token():
    return 'foobar123456789'


@pytest.fixture()
def fixture_digest():
    return "sha256:" \
           "3d2e482b82608d153a374df3357c0291589a61cc194ec4a9ca2381073a17f58e"


@pytest.fixture()
def fixture_config_payload():
    return {'config': {'digest': 'config_digest'}}


@pytest.fixture()
def fixture_image_date():
    return datetime.datetime(
        year=2019,
        month=2,
        day=5,
        hour=14,
        minute=42,
        second=38,
        microsecond=943601
    )


@pytest.fixture()
def fixture_image_date_str():
    return '2019-02-05T14:42:38.943601587Z'


@pytest.fixture()
def fixture_blob_payload(fixture_image_date_str):
    return {'created': fixture_image_date_str}


@pytest.fixture()
def fixture_delete_url(
    fixture_registry_url,
    fixture_repositories,
    fixture_digest
):
    return "{registry}/v2/{repo}/manifests/{digest}".format(
        registry=fixture_registry_url,
        repo=fixture_repositories["repositories"][0],
        digest=fixture_digest
    )


@pytest.fixture()
def fixture_tags_url():
    return '/v2/my-alpine/tags/list'


@pytest.fixture()
def fixture_tags_json(fixture_repositories, fixture_tags):
    return {
        "name": fixture_repositories["repositories"][0],
        "tags": [fixture_tags[0]]
    }


@pytest.fixture()
def fixture_image_url(fixture_repositories, fixture_tags):
    return "/v2/{repo}/manifests/{tag}".format(
        repo=fixture_repositories["repositories"][0],
        tag=fixture_tags[0]
    )


@pytest.fixture()
def fixture_image_json():
    return {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {
            "mediaType": "application/vnd.docker.container.image.v1+json",
            "size": 1511,
            "digest": "sha256:3f53bb00af943dfdf815650"
                      "be70c0fa7b426e56a66f5e3362b47a129d57d5991",
        },
        "layers": [
            {
                "mediaType":
                "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": 2207025,
                "digest": "sha256:cd784148e3483c2c86c50"
                          "a48e535302ab0288bebd587accf40b714fffd0646b3"
            }
        ]
    }
