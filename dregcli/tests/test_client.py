import pytest

from dregcli.dregcli import Client
from unittest import mock


@pytest.fixture(scope="module")
def registry_url():
    return 'localhost:5001'


class TestClient:
    def test_init(self, registry_url):
        def assert_client(verbose):
            assert client.url == registry_url
            assert client.verbose == verbose
            assert isinstance(client.request_kwargs, dict) \
                and not client.request_kwargs

        client = Client(registry_url)
        assert_client(False)
        client = Client(registry_url, verbose=False)
        assert_client(False)
        client = Client(registry_url, verbose=True)
        assert_client(True)

    def test_display(self, capsys):
        client = Client(registry_url, verbose=True)
        client.display("hello", "world")
        captured = capsys.readouterr()
        assert captured.out == "hello world\n"

        client = Client(registry_url, verbose=False)
        client.display("hello")
        captured = capsys.readouterr()
        assert captured.out == ""
