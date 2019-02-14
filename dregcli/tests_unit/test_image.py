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
def fixture_config_payload():
    return {'config': {'digest': 'config_digest'}}


@pytest.fixture()
def fixture_image_date():
    return '2019-02-05T14:42:38.943601587Z'


@pytest.fixture()
def fixture_blob_payload(fixture_image_date):
    return {'created': fixture_image_date}


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
        'fixture_config_payload'
    )
    def test_init(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_tag,
        fixture_alpine_digest,
        fixture_config_payload,
    ):
        data = {'config': {'digest': 'config_digest'}}

        image = Image(
            Client(fixture_registry_url),
            fixture_alpine_repo,
            fixture_alpine_tag,
            digest=fixture_alpine_digest,
            data=fixture_config_payload
        )
        assert image and \
            image.data == data and \
            image.tag == fixture_alpine_tag and \
            image.digest == fixture_alpine_digest and \
            image.config_digest == fixture_config_payload['config']['digest']

    @pytest.mark.usefixtures(
        'fixture_alpine_repo',
        'fixture_alpine_tag',
        'fixture_alpine_digest',
        'fixture_config_payload',
        'fixture_image_date',
        'fixture_blob_payload'
    )
    def test_get_date(
        self,
        fixture_registry_url,
        fixture_alpine_repo,
        fixture_alpine_tag,
        fixture_alpine_digest,
        fixture_config_payload,
        fixture_image_date,
        fixture_blob_payload
    ):
        mock_res = mock.MagicMock()
        mock_res.json = mock.MagicMock(return_value=fixture_blob_payload)
        mock_res.status_code = 200

        # get the date use case
        with mock.patch('requests.get', return_value=mock_res) as mo:
            image = Image(
                Client(fixture_registry_url),
                fixture_alpine_repo,
                fixture_alpine_tag,
                digest=fixture_alpine_digest,
                data=fixture_config_payload
            )
            date = image.get_date()
            assert date and date == fixture_image_date
            assert image.date == date

        # could not get the date use case
        mock_res.json = mock.MagicMock(return_value={})
        with mock.patch('requests.get', return_value=mock_res) as mo:
            image = Image(
                Client(fixture_registry_url),
                fixture_alpine_repo,
                fixture_alpine_tag,
                digest=fixture_alpine_digest,
                data=fixture_config_payload
            )
            with pytest.raises(DRegCliException) as excinfo:
                image.get_date()
            assert str(excinfo.value) == "Image date not found"

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
