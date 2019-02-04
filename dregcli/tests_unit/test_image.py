from unittest import mock
import pytest

from . import tools
from dregcli.dregcli import DRegCliException, Client, Repository, Image


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture()
def fixture_alpine_repo():
    return 'my-alpine'


@pytest.fixture()
def fixture_alpine_tag():
    return '3.8'


@pytest.fixture()
def fixture_alpine_digest():
    return "sha256:" \
           "3d2e482b82608d153a374df3357c0291589a61cc194ec4a9ca2381073a17f58e"


@pytest.fixture()
def fixture_alpine_delete_url(
    fixture_registry_url,
    fixture_alpine_repo,
    fixture_alpine_digest
):
    return "{registry}/v2/{repo}/manifests/{digest}".format(
        registry=fixture_registry_url,
        repo=fixture_alpine_repo,
        digest=fixture_alpine_digest
    )


class TestImage:
    @pytest.mark.usefixtures(
        'fixture_alpine_repo',
        'fixture_alpine_tag',
        'fixture_alpine_digest',
        'fixture_alpine_delete_url'
    )
    def test_delete(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_tag,
        fixture_alpine_digest,
        fixture_alpine_delete_url,
    ):
        mock_res = mock.MagicMock()
        mock_res.status_code = 202  # 202 for delete

        with mock.patch('requests.delete', return_value=mock_res) as mo:
            image = Image(
                Client(fixture_registry_url),
                fixture_alpine_repo,
                fixture_alpine_tag,
                digest=fixture_alpine_digest
            )
            image.delete()
            mo.assert_called_once_with(
                fixture_alpine_delete_url,
                headers=Repository.Meta.manifests_headers,
            )
