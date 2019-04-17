import json
import os
import sys
import pytest

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.pardir + os.sep + os.pardir
    )
)
import tools
from fixtures import (
    fixture_registry_url,
    fixture_client,
    fixture_repository,
    fixture_delete_tags,
)
from dregcli.console.delete import DeleteCommandHandler


class TestDeleteFromCount:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_delete_tags',
    )
    def test_from_count(
        self,
        fixture_registry_url,
        fixture_client,
        fixture_repository,
        fixture_delete_tags,
        capsys
    ):
        # check data set adhoc state
        repo = fixture_client.repositories()[0]
        repo_tags = repo.tags()
        assert sorted(repo_tags) == sorted(fixture_delete_tags)

        # tags by date desc (and their name should match fixtures)
        expected_tags_by_desc_date = [
            tag_data['tag'] for tag_data in repo.get_tags_by_date()
        ]
        assert sorted(expected_tags_by_desc_date) == \
            sorted(fixture_delete_tags)

        # remove from staging/master-*-1388, see fixture_delete_tags docstring
        from_count = 3
        should_left = [
            'latest',
            # prod layer
            'master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386',
            'prod',
        ]

        handler = DeleteCommandHandler()
        deleted = handler.run(fixture_registry_url, fixture_repository, False,
                              from_count=from_count)

        # check delete from 3rd
        should_deleted = [tag for tag in repo_tags if tag not in should_left]
        assert sorted(deleted) == sorted(should_deleted)

        # check repo should have head of no deleted ones
        assert sorted(repo.tags()) == sorted(should_left)
