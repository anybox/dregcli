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
from dregcli.dregcli import DRegCliException, Client, Image


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
        tags = self.get_repo(fixture_client).tags()
        assert sorted(tags) == sorted(fixture_tags)

    @pytest.mark.usefixtures('fixture_client', 'fixture_tags')
    def test_get_tags_by_date(
        self,
        fixture_client,
        fixture_tags,
    ):
        repo = self.get_repo(fixture_client)
        tags = repo.tags()

        tags_by_date = repo.get_tags_by_date()

        assert tags_by_date and isinstance(tags_by_date, list)
        index = 0
        for tag_data in tags_by_date:
            assert tag_data['tag'] and tag_data['tag'] in tags
            assert type(tag_data['image']) == Image and \
                tag_data['image'].tag == tag_data['tag']
            if index + 1 < len(tags_by_date):
                # check well in desc date order
                next_tag_data = tags_by_date[index + 1]
                assert tag_data['date'] >= next_tag_data['date']
            index += 1

    @pytest.mark.usefixtures('fixture_client', 'fixture_tags')
    def test_group_tags(
        self,
        fixture_client,
        fixture_tags,
    ):
        repo = self.get_repo(fixture_client)
        images = repo.group_tags()

        # master-128a1e13dbe96705917020261ee23d097606bda2-1388
        # latest
        # tags should be in same group key
        assert any([len(images[key]) == 2 for key in images])
        expected = [
            'latest',
            'master-128a1e13dbe96705917020261ee23d097606bda2-1388',
        ]
        for key in images:
            if len(images[key]) == 2:
                tags = [image.tag for image in images[key]]
                assert sorted(tags) == expected

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
        tag = 'master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385'

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

        fixture_tags.remove(tag)
        repo = self.get_repo(fixture_client)
        assert sorted(repo.tags()) == sorted(fixture_tags)

        # after delete, repo should still be here in catalog
        assert repo.name == fixture_repository


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
