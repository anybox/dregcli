import pytest

from dregcli.dregcli import Client


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture(scope="module")
def fixture_client(fixture_registry_url):
    return Client(fixture_registry_url, verbose=True)


@pytest.fixture()
def fixture_repository():
    return "my-alpine"


class TestSerie:
    @pytest.mark.usefixtures('fixture_repository')
    def test_catalog(self, fixture_client, fixture_repository):
        repositories = fixture_client.catalog()
        assert isinstance(repositories, list) and \
            len(repositories) == 1 and \
            fixture_repository == repositories[0].name
