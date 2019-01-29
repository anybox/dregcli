import pytest

from dregcli.dregcli import DRegCliException, Client, Repository
from unittest import mock


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'localhost:5001'


@pytest.fixture()
def fixture_catalog_url():
    return '/v2/_catalog'


@pytest.fixture()
def fixture_registories():
    return {"repositories":["my-alpine"]}


class TestClient:
    def test_init(self, fixture_registry_url):
        def assert_client(verbose):
            assert client.url == fixture_registry_url
            assert client.verbose == verbose
            assert isinstance(client.request_kwargs, dict) \
                and not client.request_kwargs

        client = Client(fixture_registry_url)
        assert_client(False)
        client = Client(fixture_registry_url, verbose=False)
        assert_client(False)
        client = Client(fixture_registry_url, verbose=True)
        assert_client(True)

    def test_display(self, fixture_registry_url, capsys):
        client = Client(fixture_registry_url, verbose=True)
        client.display("hello", "world")
        captured = capsys.readouterr()
        assert captured.out == "hello world\n"

        client = Client(fixture_registry_url, verbose=False)
        client.display("hello")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_catalog_404(self, fixture_registry_url):
        mock_res = mock.MagicMock()
        mock_res.status_code = 404

        with mock.patch('requests.get', return_value=mock_res) as mo:
            with pytest.raises(DRegCliException) as excinfo:
                client = Client(fixture_registry_url, verbose=False)
                client.catalog()
                mo.assert_called_once_with(
                    fixture_registry_url + '/v2/_catalog',
                )
            assert str(excinfo.value) == "Status code error 404"

    @pytest.mark.usefixtures('fixture_catalog_url', 'fixture_registories')
    def test_catalog_200(
        self,
        fixture_registry_url,
        fixture_catalog_url,
        fixture_registories):
        mock_res = mock.MagicMock()
        mock_res.status_code = 200
        mock_res.json = mock.MagicMock(return_value=fixture_registories)

        with mock.patch('requests.get', return_value=mock_res) as mo:
            client = Client(fixture_registry_url, verbose=False)
            res = client.catalog()
            mo.assert_called_once_with(
                fixture_registry_url + fixture_catalog_url,
            )
            assert isinstance(res, list) and len(res) \
                == len(fixture_registories['repositories']) and \
                all([type(r) == Repository for r in res]) and \
                all([r.client == client for r in res]) and \
                [str(r) for r in res] == fixture_registories['repositories']
