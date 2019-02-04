from unittest import mock
import pytest

from . import tools
from dregcli.dregcli import DRegCliException, Client, Repository


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture()
def fixture_repositories_url():
    return '/v2/_catalog'


@pytest.fixture()
def fixture_registories():
    return {"repositories": ["my-alpine"]}


@pytest.fixture(scope="module")
def fixture_auth_login():
    return 'foobar'


@pytest.fixture(scope="module")
def fixture_auth_password():
    return 'foobar2000'


class TestClient:
    def repositories(self, mo, client, expected_url):
        res = client.repositories()
        mo.assert_called_once_with(expected_url, headers={})
        return res

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

    @pytest.mark.usefixtures('fixture_repositories_url')
    def test_repositories_404(
        self,
        fixture_registry_url,
        fixture_repositories_url
    ):
        mock_res = mock.MagicMock()
        mock_res.status_code = 404
        msg404 = tools.get_error_status_message(404)

        with mock.patch('requests.get', return_value=mock_res) as mo:
            with pytest.raises(DRegCliException) as excinfo:
                client = Client(fixture_registry_url, verbose=False)
                self.repositories(
                    mo,
                    client,
                    fixture_registry_url + fixture_repositories_url
                )
            assert str(excinfo.value) == msg404

    @pytest.mark.usefixtures('fixture_repositories_url', 'fixture_registories')
    def test_repositories_200(
        self,
        fixture_registry_url,
        fixture_repositories_url,
        fixture_registories
    ):
        mock_res = mock.MagicMock()
        mock_res.status_code = 200
        mock_res.json = mock.MagicMock(return_value=fixture_registories)

        with mock.patch('requests.get', return_value=mock_res) as mo:
            client = Client(fixture_registry_url, verbose=False)
            repositories = self.repositories(
                mo,
                client,
                fixture_registry_url + fixture_repositories_url
            )
            expected_repos = fixture_registories['repositories']
            assert isinstance(repositories, list) and \
                len(repositories) == len(expected_repos) and \
                all([type(r) == Repository for r in repositories]) and \
                all([r.client == client for r in repositories]) and  \
                [r.name for r in repositories] == expected_repos and \
                [str(r) for r in repositories] == expected_repos


class TestAuth:
    # TODO
    pass
