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


class TestDeleteFromDateSingleTag:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_delete_tags',
    )
    def test_from_date_single_tag(
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
        tags_by_date_desc = repo.get_tags_by_date()
        expected_tags_by_desc_date = [
            tag_data['tag'] for tag_data in tags_by_date_desc
        ]
        assert sorted(expected_tags_by_desc_date) == \
            sorted(fixture_delete_tags)

        # delete from index desc order
        from_index = 10  # fixture_delete_tags, from 'alpha' in desc order
        from_date = tags_by_date_desc[from_index]['date']
        from_data_str = from_date.strftime('%Y-%m-%d %H:%M:%S.%f')

        handler = DeleteCommandHandler()
        deleted = handler.run(
            fixture_registry_url,
            fixture_repository,
            False,
            from_date=from_data_str,
            single_tag='^master-'
        )

        # 'commit tags' to be removed and left
        # (no other release tags like 'staging' on them)
        commit_tag_only_tags_deleted = [
            'master-2ze98e000wx39d60a7390925d0czr3qs03j90aaa-1382',
        ]

        # check commit_tags_only tags deleted
        assert sorted(deleted) == sorted(commit_tag_only_tags_deleted)

        # check repo should have over tags than commit_tags_only left now
        should_left_tags = [
            t for t in fixture_delete_tags
            if t not in commit_tag_only_tags_deleted
        ]
        assert sorted(repo.tags()) == sorted(should_left_tags)
