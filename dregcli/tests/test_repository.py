import pytest

from dregcli.dregcli import DRegCliException, Client, Repository
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
    return {"name":"my-alpine","tags":["3.8"]}


class TestRepository:
    @pytest.mark.usefixtures('fixture_alpine_repo', 'fixture_alpine_tags_url')
    def test_tags_404(
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
    def test_tags_200(
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
