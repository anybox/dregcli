from unittest import mock
import pytest

from dregcli.dregcli import DRegCliException, Client, Repository, Image


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'localhost:5001'


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


class TestRepositoryTag:
    def tags(self, mo, client, repo, expected_url):
        repository = Repository(client, repo)
        res = repository.tags()
        mo.assert_called_once_with(expected_url)
        return res

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
                self.tags(
                    mo,
                    Client(fixture_registry_url),
                    fixture_alpine_repo,
                    fixture_registry_url + fixture_alpine_tags_url
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
            res = self.tags(
                mo,
                Client(fixture_registry_url),
                fixture_alpine_repo,
                fixture_registry_url + fixture_alpine_tags_url
            )
            assert isinstance(res, list) and \
                res == fixture_alpine_tags_json['tags']


class TestRepositoryImage:
    def image(self, mo, client, repo, tag, expected_url):
        repository = Repository(client, repo)
        res = repository.image(tag)
        mo.assert_called_once_with(
            expected_url,
            headers=Repository.Meta.manifests_headers
        )
        return res

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
                self.image(
                    mo,
                    Client(fixture_registry_url),
                    fixture_alpine_repo,
                    fixture_alpine_image_tag,
                    fixture_registry_url + fixture_alpine_image_url
                )
            assert str(excinfo.value) == "Status code error 404"

    @pytest.mark.usefixtures(
        'fixture_alpine_repo',
        'fixture_alpine_image_tag',
        'fixture_alpine_image_url',
        'fixture_alpine_image_digest',
        'fixture_alpine_image_json'
    )
    def test_200(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_image_tag,
        fixture_alpine_image_url,
        fixture_alpine_image_digest,
        fixture_alpine_image_json
    ):
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
            res = self.image(
                mo,
                Client(fixture_registry_url),
                fixture_alpine_repo,
                fixture_alpine_image_tag,
                fixture_registry_url + fixture_alpine_image_url
            )
            assert type(res) == Image and \
                res.name == fixture_alpine_repo and \
                res.tag == fixture_alpine_image_tag and \
                res.digest == fixture_alpine_image_digest and \
                res.data == fixture_alpine_image_json
