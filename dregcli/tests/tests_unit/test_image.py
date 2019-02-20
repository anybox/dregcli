import os
import sys
from unittest import mock
import pytest


sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
from fixtures import (
    fixture_registry_url,
    fixture_repository,
    fixture_repositories,
    fixture_tags,
    fixture_digest,
    fixture_config_payload,
    fixture_image_date,
    fixture_image_date_str,
    fixture_blob_payload,
    fixture_delete_url,
)
from dregcli.dregcli import DRegCliException, Client, Repository, Image


class TestImage:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repositories',
        'fixture_tags',
        'fixture_digest',
        'fixture_config_payload'
    )
    def test_init(
        self,
        fixture_registry_url,
        fixture_repositories,
        fixture_tags,
        fixture_digest,
        fixture_config_payload,
    ):
        data = {'config': {'digest': 'config_digest'}}

        image = Image(
            Client(fixture_registry_url),
            fixture_repositories["repositories"][0],
            fixture_tags[0],
            digest=fixture_digest,
            data=fixture_config_payload
        )
        assert image and \
            image.data == data and \
            image.tag == fixture_tags[0] and \
            image.digest == fixture_digest and \
            image.config_digest == fixture_config_payload['config']['digest']

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repositories',
        'fixture_tags',
        'fixture_digest',
        'fixture_config_payload',
        'fixture_image_date',
        'fixture_blob_payload'
    )
    def test_get_date(
        self,
        fixture_registry_url,
        fixture_repositories,
        fixture_tags,
        fixture_digest,
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
                fixture_repositories["repositories"][0],
                fixture_tags[0],
                digest=fixture_digest,
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
                fixture_repositories["repositories"][0],
                fixture_tags[0],
                digest=fixture_digest,
                data=fixture_config_payload
            )
            with pytest.raises(DRegCliException) as excinfo:
                image.get_date()
            assert str(excinfo.value) == "Image date not found"

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repositories',
        'fixture_tags',
        'fixture_digest',
        'fixture_delete_url'
    )
    def test_delete(
        self,
        fixture_registry_url,
        fixture_repositories,
        fixture_tags,
        fixture_digest,
        fixture_delete_url,
    ):
        mock_res = mock.MagicMock()
        mock_res.status_code = 202  # 202 for delete

        with mock.patch('requests.delete', return_value=mock_res) as mo:
            image = Image(
                Client(fixture_registry_url),
                fixture_repositories["repositories"][0],
                fixture_tags[0],
                digest=fixture_digest
            )
            image.delete()
            mo.assert_called_once_with(
                fixture_delete_url,
                headers=Repository.Meta.manifests_headers,
            )
