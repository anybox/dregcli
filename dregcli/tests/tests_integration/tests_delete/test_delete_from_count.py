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

        from_count = 3
        handler = DeleteCommandHandler()
        deleted = handler.run(fixture_registry_url, fixture_repository, False,
                              from_count=from_count)

        # check delete from 3rd
        should_deleted = expected_tags_by_desc_date[from_count - 1:]
        assert deleted == should_deleted

        # check reop should have head of no deleted ones
        should_left = expected_tags_by_desc_date[:from_count - 1]
        assert sorted(repo.tags()) == sorted(should_left)