import pytest

from dregcli.dregcli import DRegCliException, Client


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture(scope="module")
def fixture_client(fixture_registry_url):
    return Client(fixture_registry_url, verbose=True)


@pytest.fixture()
def fixture_repository():
    return "my-alpine"


@pytest.fixture()
def fixture_tags():
    return ["3.8"]


@pytest.fixture()
def fixture_digest():
    return "sha256:3d2e482b82608d153a374df3357c02" \
           "91589a61cc194ec4a9ca2381073a17f58e"


class TestClient:
    @pytest.mark.usefixtures('fixture_repository')
    def test_catalog(self, fixture_client, fixture_repository):
        repositories = fixture_client.catalog()
        assert isinstance(repositories, list) and \
            len(repositories) == 1 and \
            repositories[0].name == fixture_repository


class TestRepoImage:
    def get_repo(self, client):
        return client.catalog()[0]

    @pytest.mark.usefixtures('fixture_tags')
    def test_tags(self, fixture_client, fixture_tags):
        assert self.get_repo(fixture_client).tags() == fixture_tags

    @pytest.mark.usefixtures(
        'fixture_repository',
        'fixture_tags',
        'fixture_digest'
    )
    def test_image(
        self,
        fixture_client,
        fixture_repository,
        fixture_tags,
        fixture_digest
    ):
        tag = fixture_tags[0]
        image = self.get_repo(fixture_client).image(tag)
        assert image and image.name == fixture_repository \
            and image.tag == tag and \
            image.digest == fixture_digest

        image.delete()

        # after delete, same image delete should 404 (no more manifest)
        msg404 = "Status code error 404"
        with pytest.raises(DRegCliException) as excinfo:
            image.delete()
        assert str(excinfo.value) == msg404

        # after delete, same image request should 404 (no more manifest)
        with pytest.raises(DRegCliException) as excinfo:
            self.get_repo(fixture_client).image(tag)
        assert str(excinfo.value) == msg404

        # after delete, no tag left
        assert self.get_repo(fixture_client).tags() is None

        # after delete, repo should still be here in catalog
        assert self.get_repo(fixture_client).name == fixture_repository
