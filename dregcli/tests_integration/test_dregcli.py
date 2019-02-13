import os
import pytest

from . import tools
from dregcli.dregcli import DRegCliException, Client


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture(scope="module")
def fixture_client(fixture_registry_url):
    return Client(fixture_registry_url, verbose=True)


@pytest.fixture()
def fixture_repository():
    return 'my-alpine'


@pytest.fixture()
def fixture_tags():
    # FYI: through test_console.py testing, latest tag was removed
    # we pass from ['latest', '3.8'] to ['3.8']
    return ['3.8']


class TestClient:
    @pytest.mark.usefixtures('fixture_repository')
    def test_repositories(self, fixture_client, fixture_repository):
        repositories = fixture_client.repositories()
        assert isinstance(repositories, list) and \
            len(repositories) == 1 and \
            repositories[0].name == fixture_repository


class TestRepoImage:
    def get_repo(self, client):
        return client.repositories()[0]

    @pytest.mark.usefixtures('fixture_tags')
    def test_tags(self, fixture_client, fixture_tags):
        assert self.get_repo(fixture_client).tags() == fixture_tags

    @pytest.mark.usefixtures(
        'fixture_repository',
        'fixture_tags',
    )
    def test_image(
        self,
        fixture_client,
        fixture_repository,
        fixture_tags,
    ):
        tag = fixture_tags[0]  # FYI in test_console latest tag was deleted

        image = self.get_repo(fixture_client).image(tag)
        assert image and image.name == fixture_repository and \
            image.tag == tag and \
            tools.check_sha256(image.digest)

        image.delete()

        # after delete, same image delete should 404 (no more manifest)
        msg404 = tools.get_error_status_message(404)
        with pytest.raises(DRegCliException) as excinfo:
            image.delete()
        assert str(excinfo.value) == msg404

        # after delete, same image request should 404 (no more manifest)
        with pytest.raises(DRegCliException) as excinfo:
            self.get_repo(fixture_client).image(tag)
        assert str(excinfo.value) == msg404

        # after delete, tag removed, the last so no other tag remains
        assert self.get_repo(fixture_client).tags() is None

        # after delete, repo should still be here in catalog
        assert self.get_repo(fixture_client).name == fixture_repository

    @pytest.mark.usefixtures(
        'fixture_repository',
    )
    def test_garbage(
        self,
        fixture_client,
        fixture_repository,
    ):
        # TODO
        pass


class TestAuth:
    """
    following env vars are required for the auth integration env test
        - DREGCLI_HOST
        - DREGCLI_LOGIN
        - DREGCLI_PASSWORD
    """
    def get_credentials(self):
        self.host = os.environ.get('DREGCLI_HOST', False)
        self.login = os.environ.get('DREGCLI_LOGIN', False)
        self.pwd = os.environ.get('DREGCLI_PASSWORD', False)
        self.active = self.host and self.login and self.pwd
        return self.active

    def get_client(self):
        if self.active:
            client = Client(self.host)
            client.set_auth(self.login, self.pwd)
        else:
            client = None
        return client

    def test_auth(self):
        if self.get_credentials():
            # only flow test if test vars are set
            client = self.get_client()
            repositories = client.repositories()
            assert repositories and isinstance(repositories, list) and \
                len(repositories) > 0
