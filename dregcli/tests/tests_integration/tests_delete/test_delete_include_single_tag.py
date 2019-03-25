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
    fixture_delete_tags_with_no_old,
)
from dregcli.console.delete import DeleteCommandHandler


class TestDeleteIncludeSingleTag:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_delete_tags',
        'fixture_delete_tags_with_no_old',
    )
    def test_include_single_tag(
        self,
        fixture_registry_url,
        fixture_client,
        fixture_repository,
        fixture_delete_tags,
        fixture_delete_tags_with_no_old,
        capsys
    ):
        # check data set adhoc state
        repo = fixture_client.repositories()[0]
        repo_tags = repo.tags()
        assert sorted(repo_tags) == sorted(fixture_delete_tags)

        include = r"1382$"
        handler = DeleteCommandHandler()
        deleted = handler.run(
            fixture_registry_url,
            fixture_repository,
            False,
            include=include,
            single_tag='^master-'
        )

        # 'commit tags' to be removed
        # 1382 as no other release tag + included
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
