import os
import sys
import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
import tools
from fixtures import (
    fixture_registry_url,
    fixture_client,
    fixture_repository,
    fixture_tags,
)
from dregcli.dregcli import DRegCliException, Client


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
        # FYI in test_console.py 2 first tags were deleted, should remains
        # the others
        assert self.get_repo(fixture_client).tags() == fixture_tags[2:]

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
        # FYI in test_console tags 0 and 1 were deleted
        tag = fixture_tags[2]

        image = self.get_repo(fixture_client).image(tag)
        assert image and image.name == fixture_repository and \
            image.data and isinstance(image.data, dict) and \
            image.tag == tag and \
            tools.check_sha256(image.digest) and \
            tools.check_sha256(image.config_digest)

        # get image date
        image.get_date()
        assert image.date

        # delete flow
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

        # after delete, tag removed, 0, 1, 2 tags removed,
        # so the last remains
        assert self.get_repo(fixture_client).tags() == [fixture_tags[-1]]

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
