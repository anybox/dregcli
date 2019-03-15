import datetime
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


class TestGarbageFromDate:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_delete_tags',
    )
    def test_from_date(
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
        tags_by_desc_date = repo.get_tags_by_date()
        expected_tag_names_by_desc_date = [
            tag_data['tag'] for tag_data in tags_by_desc_date
        ]
        assert sorted(expected_tag_names_by_desc_date) == \
            sorted(fixture_delete_tags)

        # index to test from
        from_index = 3

        from_date = tags_by_desc_date[from_index]['date']
        from_data_str = from_date.strftime('%Y-%m-%d %H:%M:%S.%f')

        handler = DeleteCommandHandler()
        deleted = handler.run(fixture_registry_url, fixture_repository, False,
                              from_date=from_data_str)

        # get expected remove from index (from date)
        expected_from_index = -1
        index = 0
        for tag_data in tags_by_desc_date:
            if tag_data['date'] == from_date:
                expected_from_index = index
                break
            index += 1
        assert expected_from_index >= 0  # base condition of below contracts

        # check delete from 3rd
        assert deleted == expected_tag_names_by_desc_date[expected_from_index:]

        # check should have left of no deleted ones
        assert sorted(repo.tags()) == \
            sorted(expected_tag_names_by_desc_date[:expected_from_index])
