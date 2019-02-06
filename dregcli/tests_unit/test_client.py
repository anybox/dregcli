import os
import requests
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


@pytest.fixture()
def fixture_auth():
    return {
        'login': 'foobar',
        'password': 'foobar2000',
        'token': ''
    }


@pytest.fixture()
def fixture_auth_token():
    return 'mytoken123456789'


class TestClient:
    def repositories(self, mo, client, expected_url):
        res = client.repositories()
        mo.assert_called_once_with(expected_url, headers={})
        return res

    def test_init(self, fixture_registry_url):
        def assert_client(verbose, remote_type):
            remote_type = remote_type or Client.Meta.remote_type_registry
            assert client.url == fixture_registry_url
            assert client.verbose == verbose
            assert client.remote_type = remote_type
            assert isinstance(client.request_kwargs, dict) \
                and not client.request_kwargs

        client = Client(fixture_registry_url)
        assert_client(False)
        client = Client(fixture_registry_url, verbose=False)
        assert_client(False)
        client = Client(fixture_registry_url, verbose=True)
        assert_client(True)
        client = Client(fixture_registry_url,
                        remote_type=Client.Meta.remote_type_gitlab)
        assert_client(False, Client.Meta.remote_type_gitlab)

    def test_display(self, fixture_registry_url, capsys):
        client = Client(fixture_registry_url, verbose=True)
        client.display("hello", "world")
        captured = capsys.readouterr()
        assert captured.out == "hello world\n"

        client = Client(fixture_registry_url, verbose=False)
        client.display("hello")
        captured = capsys.readouterr()
        assert captured.out == ""

    @pytest.mark.usefixtures('fixture_repositories_url', 'fixture_registories')
    def test_request(
        self,
        fixture_registry_url,
        fixture_repositories_url,
        fixture_registories
    ):
        expected_url = fixture_registry_url + fixture_repositories_url
        expected_code = 200

        client = Client(fixture_registry_url, verbose=False)
        headers = {}

        # default
        mock_res = mock.MagicMock()
        mock_res.json = mock.MagicMock(return_value=fixture_registories)
        mock_res.status_code = 200
        with mock.patch('requests.get', return_value=mock_res) as mo:
            res = client._request(expected_url)
            mo.assert_called_once_with(expected_url, headers=headers)
            assert res.status_code == expected_code and \
                res.json() == fixture_registories

        # headers
        headers = {'foobar': 'foobar2000'}
        with mock.patch('requests.get', return_value=mock_res) as mo:
            res = client._request(expected_url, headers=headers)
            mo.assert_called_once_with(expected_url, headers=headers)
            assert res.status_code == expected_code and \
                res.json() == fixture_registories

        # method
        headers = {}
        with mock.patch('requests.post', return_value=mock_res) as mo:
            res = client._request(
                expected_url,
                method=requests.post,
                verb='POST'
            )
            mo.assert_called_once_with(
                expected_url,
                headers=headers,
            )
            assert res.status_code == expected_code and \
                res.json() == fixture_registories

        # expected_code matching
        expected_code = 202
        mock_res.status_code = expected_code
        with mock.patch('requests.get', return_value=mock_res) as mo:
            res = client._request(expected_url, expected_code=expected_code)
            mo.assert_called_once_with(
                expected_url,
                headers=headers,
            )
            assert res.status_code == expected_code and \
                res.json() == fixture_registories

        # expected code mismatch
        expected_code = 202
        other_code = 404    # other result than expected code
        other_code_msg = tools.get_error_status_message(other_code)
        mock_res.status_code = other_code
        with mock.patch('requests.get', return_value=mock_res) as mo:
            with pytest.raises(DRegCliException) as excinfo:
                res = client._request(
                    expected_url,
                    expected_code=expected_code
                )
                mo.assert_called_once_with(
                    expected_url,
                    headers=headers,
                )
                assert res.status_code == expected_code and \
                    res.json() == fixture_registories
            assert str(excinfo.value) == other_code_msg

    @pytest.mark.usefixtures('fixture_repositories_url', 'fixture_registories')
    def test_repositories(
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
    @pytest.mark.usefixtures('fixture_auth_token')
    def test_decorate_headers(self, fixture_registry_url, fixture_auth_token):
        client = Client(fixture_registry_url, verbose=False)
        client.auth = {'token': fixture_auth_token}

        headers = {'foobar': 'foobar2000'}
        expected_headers = headers.copy()
        expected_headers['Authorization'] = \
            Client.Meta.auth_bearer_pattern.format(token=fixture_auth_token)

        client._auth_decorate_headers(headers)
        assert headers == expected_headers

    @pytest.mark.usefixtures('fixture_auth', 'fixture_auth_token')
    def test_get_token(
        self,
        fixture_auth,
        fixture_auth_token
    ):
        expected_realm = "https://myhost/v2/token"
        expected_service = "docker-registry.myhost.com"
        expected_scope = "registry:catalog:*"

        authenticate_header_val = \
            'Bearer realm="{realm}",' \
            'service="{service}",' \
            'scope="{scope}"'.format(
                realm=expected_realm,
                service=expected_service,
                scope=expected_scope
            )
        headers = {'Www-Authenticate': authenticate_header_val}

        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.headers = headers

        auth_get_token_inner_get_result = mock.MagicMock()
        auth_get_token_inner_get_result.status_code = 200
        auth_get_token_inner_get_result.json = mock.MagicMock(
            return_value={'token': fixture_auth_token}
        )

        client = Client(fixture_registry_url, verbose=False)
        client.auth = fixture_auth

        with mock.patch('requests.get',
                        return_value=auth_get_token_inner_get_result) as mo:
            client._auth_get_token(mock_response)
            assert 'token' in client.auth and \
                client.auth['token'] == fixture_auth_token

        no_token_msg = "Get token request: no token found in response"
        auth_get_token_inner_get_result.json = mock.MagicMock(
            return_value={'token': ''}
        )
        with mock.patch('requests.get',
                        return_value=auth_get_token_inner_get_result) as mo:
            with pytest.raises(DRegCliException) as excinfo:
                client._auth_get_token(mock_response)
            assert str(excinfo.value) == no_token_msg

        # no token use case
        auth_get_token_inner_get_result.json = mock.MagicMock(
            return_value={}
        )
        with mock.patch('requests.get',
                        return_value=auth_get_token_inner_get_result) as mo:
            with pytest.raises(DRegCliException) as excinfo:
                client._auth_get_token(mock_response)
            assert str(excinfo.value) == no_token_msg

    @pytest.mark.usefixtures(
        'fixture_repositories_url',
        'fixture_auth',
        'fixture_auth_token'
    )
    def test_request(
        self,
        fixture_registry_url,
        fixture_repositories_url,
        fixture_auth,
        fixture_auth_token
    ):
        expected_url = fixture_registry_url + fixture_repositories_url
        expected_code = 200

        client = Client(fixture_registry_url, verbose=False)
        client.auth = fixture_auth
        client._auth_get_token = mock.MagicMock(
            return_value=fixture_auth_token
        )
        client.decorate_headers = mock.MagicMock(return_value={})

        # default
        mock_res = mock.MagicMock()
        mock_res.json = mock.MagicMock(return_value=fixture_registories)
        mock_res.status_code = 200
        with mock.patch('requests.get', return_value=mock_res) as mo:
            res = client._request(expected_url)
            assert res.status_code == expected_code and \
                res.json() == fixture_registories
