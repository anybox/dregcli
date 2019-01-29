import pytest

from dregcli.dregcli import DRegCliException, Client, Repository, Image
from unittest import mock


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'localhost:5001'


@pytest.fixture()
def fixture_alpine_repo():
    return 'my-alpine'


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
def fixture_alpine_image_tag():
    return '3.8'


@pytest.fixture()
def fixture_alpine_image_url():
    return '/v2/my-alpine/manifests/3.8'


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


class TestRepositoryTag:
    @pytest.mark.usefixtures('fixture_alpine_repo', 'fixture_alpine_tags_url')
    def test_404(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_tags_url
    ):
        mock_res = mock.MagicMock()
        mock_res.status_code = 404

        with mock.patch('requests.get', return_value=mock_res) as mo:
            with pytest.raises(DRegCliException) as excinfo:
                repository = Repository(
                    Client(fixture_registry_url),
                    fixture_alpine_repo
                )
                repository.tags()
                mo.assert_called_once_with(
                    fixture_registry_url + fixture_alpine_tags_url,
                )
            assert str(excinfo.value) == "Status code error 404"

    @pytest.mark.usefixtures(
        'fixture_alpine_repo',
        'fixture_alpine_tags_url',
        'fixture_alpine_tags_json'
    )
    def test_200(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_tags_url,
        fixture_alpine_tags_json
    ):
        mock_res = mock.MagicMock()
        mock_res.status_code = 200
        mock_res.json = mock.MagicMock(return_value=fixture_alpine_tags_json)

        with mock.patch('requests.get', return_value=mock_res) as mo:
            repository = Repository(
                Client(fixture_registry_url),
                fixture_alpine_repo
            )
            res = repository.tags()
            mo.assert_called_once_with(
                fixture_registry_url + fixture_alpine_tags_url
            )
            assert isinstance(res, list) and \
                res == fixture_alpine_tags_json['tags']


class TestRepositoryImage:
    @pytest.mark.usefixtures(
        'fixture_alpine_repo',
        'fixture_alpine_image_tag',
        'fixture_alpine_image_url',
    )
    def test_404(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_image_tag,
        fixture_alpine_image_url
    ):
        mock_res = mock.MagicMock()
        mock_res.status_code = 404

        with mock.patch('requests.get', return_value=mock_res) as mo:
            with pytest.raises(DRegCliException) as excinfo:
                repository = Repository(
                    Client(fixture_registry_url),
                    fixture_alpine_repo
                )
                repository.image(fixture_alpine_image_tag)
                mo.assert_called_once_with(
                    fixture_registry_url + fixture_alpine_image_url,
                    headers=Repository._manifests_headers
                )
            assert str(excinfo.value) == "Status code error 404"

    @pytest.mark.usefixtures(
        'fixture_alpine_repo',
        'fixture_alpine_image_tag',
        'fixture_alpine_image_url',
        'fixture_alpine_image_json'
    )
    def test_200(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_image_tag,
        fixture_alpine_image_url,
        fixture_alpine_image_json
    ):
        mock_res = mock.MagicMock()
        mock_res.status_code = 200
        mock_res.json = mock.MagicMock(
            return_value=fixture_alpine_image_json
        )
        expected_image_name = "{repo}:{tag}".format(
            repo=fixture_alpine_repo,
            tag=fixture_alpine_image_tag
        )

        with mock.patch('requests.get', return_value=mock_res) as mo:
            repository = Repository(
                Client(fixture_registry_url),
                fixture_alpine_repo
            )
            res = repository.image(fixture_alpine_image_tag)
            mo.assert_called_once_with(
                fixture_registry_url + fixture_alpine_image_url,
                headers=Repository._manifests_headers
            )
            assert type(res) == Image and res.name == expected_image_name and \
                res.data == fixture_alpine_image_json
