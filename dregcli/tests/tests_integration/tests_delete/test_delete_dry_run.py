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


class TestDeleteDryRun:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_delete_tags'
    )
    def test_dry_run(
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

        handler = DeleteCommandHandler()
        deleted = handler.run(fixture_registry_url, fixture_repository, False,
                              all=True, dry_run=True)

        # check output: all tags deleted output
        assert sorted(deleted) == sorted(fixture_delete_tags)

        # check should have all tags left here versus no tag anymore
        # due to dry run mode
        assert sorted(repo_tags) == sorted(fixture_delete_tags)
