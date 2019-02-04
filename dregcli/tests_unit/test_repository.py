from unittest import mock
import pytest

from . import tools
from dregcli.dregcli import DRegCliException, Client, Repository, Image


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture()
def fixture_alpine_repo():
    return 'my-alpine'


@pytest.fixture()
def fixture_alpine_image_tag():
    return '3.8'


@pytest.fixture()
def fixture_alpine_tags_url():
    return '/v2/my-alpine/tags/list'


@pytest.fixture()
def fixture_alpine_tags_json():
    return {
        "name": "my-alpine",
        "tags": ["3.8"]
    }


@pytest.fixture()
def fixture_alpine_image_url(fixture_alpine_repo, fixture_alpine_image_tag):
    return "/v2/{repo}/manifests/{tag}".format(
        repo=fixture_alpine_repo,
        tag=fixture_alpine_image_tag
    )


@pytest.fixture()
def fixture_alpine_image_digest():
    return "sha256:3d2e482b82608d153a374df3357c0291589" \
           "a61cc194ec4a9ca2381073a17f58e"


@pytest.fixture()
def fixture_alpine_image_json():
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


class TestRepository:
    @pytest.mark.usefixtures(
        'fixture_alpine_repo',
        'fixture_alpine_tags_url',
        'fixture_alpine_tags_json'
    )
    def test_tags(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_tags_url,
        fixture_alpine_tags_json
    ):
        expected_url = fixture_registry_url + fixture_alpine_tags_url
        mock_res = mock.MagicMock()
        mock_res.status_code = 200
        mock_res.json = mock.MagicMock(return_value=fixture_alpine_tags_json)

        with mock.patch('requests.get', return_value=mock_res) as mo:
            repository = Repository(
                Client(fixture_registry_url),
                fixture_alpine_repo
            )
            tags = repository.tags()
            assert isinstance(tags, list) and \
                tags == fixture_alpine_tags_json['tags']

    @pytest.mark.usefixtures(
        'fixture_alpine_repo',
        'fixture_alpine_image_tag',
        'fixture_alpine_image_url',
        'fixture_alpine_image_digest',
        'fixture_alpine_image_json'
    )
    def test_image(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_image_tag,
        fixture_alpine_image_url,
        fixture_alpine_image_digest,
        fixture_alpine_image_json
    ):
        expected_url = fixture_registry_url + fixture_alpine_image_url
        mock_res = mock.MagicMock()
        mock_res.status_code = 200
        mock_res.json = mock.MagicMock(
            return_value=fixture_alpine_image_json
        )

        # mock response headers
        response_headers = {}
        response_headers[Repository.Meta.manifest_response_header_digest] = \
            fixture_alpine_image_digest
        mock_res.headers.__getitem__.side_effect = response_headers.__getitem__
        mock_res.headers.get.side_effect = response_headers.get  # mock get
        mock_res.headers.__iter__.side_effect = response_headers.__iter__

        expected_image_name = "{repo}:{tag}".format(
            repo=fixture_alpine_repo,
            tag=fixture_alpine_image_tag
        )

        with mock.patch('requests.get', return_value=mock_res) as mo:
            repository = Repository(
                Client(fixture_registry_url),
                fixture_alpine_repo
            )
            image = repository.image(fixture_alpine_image_tag)
            mo.assert_called_once_with(
                expected_url,
                headers=Repository.Meta.manifests_headers
            )
            assert type(image) == Image and \
                image.name == fixture_alpine_repo and \
                image.tag == fixture_alpine_image_tag and \
                image.digest == fixture_alpine_image_digest and \
                image.data == fixture_alpine_image_json and \
                str(image) == "{repo}:{tag}".format(
                    repo=fixture_alpine_repo,
                    tag=fixture_alpine_image_tag
                )
