import datetime
import pytest

from dregcli.dregcli import Client


@pytest.fixture()
def fixture_registry_url():
    return 'http://localhost:5002'


@pytest.fixture()
def fixture_client(fixture_registry_url):
    return Client(fixture_registry_url)


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
    tags = [
        'master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385',
        'master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386',
        'master-1c48755c0b257ccd106badcb973a36528f833fc0-1387',

        # 1388/latest layer: see start.sh setTestImages()
        'master-128a1e13dbe96705917020261ee23d097606bda2-1388',
        'latest'
    ]

    # desc date order regarding start.sh dataset
    tags.reverse()
    return tags


@pytest.fixture()
def fixture_delete_tags():
    """
    delete testings tags main data set
        date desc order
    see start.sh setdeleteTestImages()

    dregcli images:
    Tags                       Date
    -------------------------- -------------------
    prod,master-*-1386         2019-03-07 22:20:00
    master-*-1387,old-staging  2019-03-07 22:19:53
    master-*-1388,staging      2019-03-07 22:19:46
    latest                     2019-03-07 22:19:40
    master-*-1385,old-prod     2019-01-30 22:20:40
    master-*-1384              2019-01-30 22:20:30
    master-*-1383,alpha        2019-01-30 22:20:20
    master-*-1382              2019-01-30 22:20:12
    """
    return [
        # prod layer
        'master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386',
        'prod',

        # old staging layer
        'master-1c48755c0b257ccd106badcb973a36528f833fc0-1387',
        'old-staging',

        # staging layer
        'master-128a1e13dbe96705917020261ee23d097606bda2-1388',
        'staging',

        'latest',

        # old-prod layer
        'master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385',
        'old-prod',

        # layer with only commit tags
        'master-2bd32d000ez93c50h8486935f0fda5ee09z98bbb-1384',

        # a layer with a release tag between 2 layers with only commit tags
        'master-2yu50j111dy72e70b9623522e0zdt9wz29h71ddd-1383',
        'alpha',

        # layer with only commit tags
        'master-2ze98e000wx39d60a7390925d0czr3qs03j90aaa-1382',
    ]


@pytest.fixture()
def fixture_delete_tags_cotags_mapping():
    return {
        'master-2ze98e000wx39d60a7390925d0czr3qs03j90aaa-1382': [],

        # alpha layer
        'master-2yu50j111dy72e70b9623522e0zdt9wz29h71ddd-1383': ['alpha'],
        'alpha': ['master-2yu50j111dy72e70b9623522e0zdt9wz29h71ddd-1383'],

        'master-2bd32d000ez93c50h8486935f0fda5ee09z98bbb-1384': [],

        # old-prod layer
        'master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385': ['old-prod'],
        'old-prod': ['master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385'],

        # prod layer
        'master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386': ['prod'],
        'prod': ['master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386'],

        # old staging layer
        'master-1c48755c0b257ccd106badcb973a36528f833fc0-1387': \
        ['old-staging'],
        'old-staging': \
        ['master-1c48755c0b257ccd106badcb973a36528f833fc0-1387'],

        # staging layer
        'master-128a1e13dbe96705917020261ee23d097606bda2-1388': ['staging'],
        'staging': ['master-128a1e13dbe96705917020261ee23d097606bda2-1388'],

        'latest': [],
    }


@pytest.fixture()
def fixture_delete_tags_with_no_old():
    """
    without 'old-staging' 'old-prod' tags. and not cotags of them
    date desc order
    """
    return [
        # prod layer
        'master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386',
        'prod',

        # staging layer
        'master-128a1e13dbe96705917020261ee23d097606bda2-1388',
        'staging',

        'latest',

        # layer with only commit tags
        'master-2bd32d000ez93c50h8486935f0fda5ee09z98bbb-1384',

        # a layer with a release tag between 2 layers with only commit tags
        'master-2yu50j111dy72e70b9623522e0zdt9wz29h71ddd-1383',
        'alpha',

        # layer with only commit tags
        'master-2ze98e000wx39d60a7390925d0czr3qs03j90aaa-1382',
    ]


@pytest.fixture()
def fixture_delete_tags_old():
    """
    'old-staging'/'old-prod' tags and cotags of them.
    date desc order
    """
    return [
        # old staging
        'master-1c48755c0b257ccd106badcb973a36528f833fc0-1387',
        'old-staging',

        # old prod
        'master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385',
        'old-prod',
    ]


@pytest.fixture()
def fixture_delete_tags_old_only():
    """date desc order"""
    return [
        'old-staging',
        'old-prod',
    ]


@pytest.fixture()
def fixture_auth():
    return {
        'login': 'foobar',
        'password': 'foobar2000',
        'token': '',
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
    return {
        'schemaVersion': 2,
        'config': {
            'digest': 'config_digest'
        }
    }


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
def fixture_schema1_history(fixture_image_date_str):
    return {
        'schemaVersion': 1,
        'v1Compatibility': {
            'history': [
                {'created': fixture_image_date_str},
                {'created': '2019-01-03T12:41:55.621302432Z'},
            ]
        }
    }


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
    return '/v2/test-project/tags/list'


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
