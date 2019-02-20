import os
import requests
import sys
from unittest import mock
import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
import tools
from fixtures import (
    fixture_registry_url,
    fixture_repositories_url,
    fixture_repository,
    fixture_repositories,
    fixture_auth,
    fixture_auth_token
)
from dregcli.dregcli import DRegCliException, Client, Repository


@pytest.fixture()
def fixture_auth_token():
    return 'mytoken123456789'


class TestClient:
    def repositories(self, mo, client, expected_url):
        res = client.repositories()
        mo.assert_called_once_with(expected_url, headers={})
        return res

    @pytest.mark.usefixtures('fixture_registry_url')
    def test_init(self, fixture_registry_url):
        def assert_client(verbose):
            assert client.url == fixture_registry_url
            assert client.verbose == verbose
            assert not client.auth
            assert isinstance(client.request_kwargs, dict) \
                and not client.request_kwargs

        client = Client(fixture_registry_url)
        assert_client(False, )
        client = Client(fixture_registry_url, verbose=False)
        assert_client(False)
        client = Client(fixture_registry_url, verbose=True)
        assert_client(True)

    @pytest.mark.usefixtures('fixture_registry_url')
    def test_display(self, fixture_registry_url, capsys):
        client = Client(fixture_registry_url, verbose=True)
        client.display("hello", "world")
        captured = capsys.readouterr()
        assert captured.out == "hello world\n"

        client = Client(fixture_registry_url, verbose=False)
        client.display("hello")
        captured = capsys.readouterr()
        assert captured.out == ""

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repositories_url',
        'fixture_repositories'
    )
    def test_request(
        self,
        fixture_registry_url,
        fixture_repositories_url,
        fixture_repositories
    ):
        expected_url = fixture_registry_url + fixture_repositories_url
        expected_code = 200

        client = Client(fixture_registry_url, verbose=False)
        headers = {}

        # default
        mock_res = mock.MagicMock()
        mock_res.json = mock.MagicMock(return_value=fixture_repositories)
        mock_res.status_code = 200
        with mock.patch('requests.get', return_value=mock_res) as mo:
            res = client._request(expected_url)
            mo.assert_called_once_with(expected_url, headers=headers)
            assert res.status_code == expected_code and \
                res.json() == fixture_repositories

        # headers
        headers = {'foobar': 'foobar2000'}
        with mock.patch('requests.get', return_value=mock_res) as mo:
            res = client._request(expected_url, headers=headers)
            mo.assert_called_once_with(expected_url, headers=headers)
            assert res.status_code == expected_code and \
                res.json() == fixture_repositories

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
                res.json() == fixture_repositories

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
                res.json() == fixture_repositories

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
                    res.json() == fixture_repositories
            assert str(excinfo.value) == other_code_msg

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repositories_url',
        'fixture_repositories'
    )
    def test_repositories(
        self,
        fixture_registry_url,
        fixture_repositories_url,
        fixture_repositories
    ):
        mock_res = mock.MagicMock()
        mock_res.status_code = 200
        mock_res.json = mock.MagicMock(return_value=fixture_repositories)

        with mock.patch('requests.get', return_value=mock_res) as mo:
            client = Client(fixture_registry_url, verbose=False)
            repositories = self.repositories(
                mo,
                client,
                fixture_registry_url + fixture_repositories_url
            )
            expected_repos = fixture_repositories['repositories']
            assert isinstance(repositories, list) and \
                len(repositories) == len(expected_repos) and \
                all([type(r) == Repository for r in repositories]) and \
                all([r.client == client for r in repositories]) and  \
                [r.name for r in repositories] == expected_repos and \
                [str(r) for r in repositories] == expected_repos


class TestAuth:
    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_auth')
    def test_set_auth(self, fixture_registry_url, fixture_auth):
        client = Client(fixture_registry_url)
        client.set_auth(
            fixture_auth.get('login'),
            fixture_auth.get('password')
        )
        assert client.auth == fixture_auth

    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_auth')
    def test_set_auth(self, fixture_registry_url, fixture_auth):
        client = Client(fixture_registry_url)
        client.auth = fixture_auth

        client.reset_auth()
        assert not client.auth and isinstance(client.auth, bool)

    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_auth_token')
    def test_decorate_headers(self, fixture_registry_url, fixture_auth_token):
        client = Client(fixture_registry_url, verbose=False)
        client.auth = {'token': fixture_auth_token}

        headers = {'foobar': 'foobar2000'}
        original_headers = headers.copy()
        expected_headers = headers.copy()
        expected_headers['Authorization'] = \
            Client.Meta.auth_bearer_pattern.format(token=fixture_auth_token)

        decorated_headers = client._auth_decorate_headers(headers)
        # header should be unchanged
        assert headers == original_headers
        # decorated headers should be the expected
        decorated_headers == expected_headers

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_auth',
        'fixture_auth_token'
    )
    def test_get_token(
        self,
        fixture_registry_url,
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
        'fixture_registry_url',
        'fixture_repositories_url',
        'fixture_repositories',
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
        mock_res.json = mock.MagicMock(return_value=fixture_repositories)
        mock_res.status_code = 200
        with mock.patch('requests.get', return_value=mock_res) as mo:
            res = client._request(expected_url)
            assert res.status_code == expected_code and \
                res.json() == fixture_repositories
