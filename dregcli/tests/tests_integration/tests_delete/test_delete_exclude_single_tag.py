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


class TestDeleteExcludeSingleTag:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_delete_tags',
    )
    def test_exclude_single_tag(
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

        exclude = '1382$'
        handler = DeleteCommandHandler()
        deleted = handler.run(
            fixture_registry_url,
            fixture_repository,
            False,
            exclude=exclude,
            single_tag='^master'
        )

        # 1384 to be removed: only 1382 and 1384 have no release tag
        # and 1382 is excluded
        commit_tag_only_tags_deleted = [
            'master-2bd32d000ez93c50h8486935f0fda5ee09z98bbb-1384',
        ]

        # check commit_tags_only tags deleted
        assert sorted(deleted) == sorted(commit_tag_only_tags_deleted)

        # check repo should have over tags than commit_tags_only left now
        should_left_tags = [
            t for t in fixture_delete_tags
            if t not in commit_tag_only_tags_deleted
        ]
        assert sorted(repo.tags()) == sorted(should_left_tags)
